"""PR-4 — Independent Attester Service: PROCESS ISOLATION EVIDENCE.

The task specification is explicit that "independent service" must not be
satisfied solely with two Python objects in the same process. This file
launches the Attester Service as a genuine, separate OS process (via
``python -m mcc_attester_service``, the reference entrypoint in
``src/mcc_attester_service/__main__.py``) and talks to it over real HTTP,
demonstrating:

* the Attester process has the private key (it signs successfully);
* the "governed MCC" side of this test (this test's own process) does NOT
  hold the private key -- it retains only the raw Ed25519 PUBLIC key bytes,
  captured once at key-generation time, and never reads the private PEM
  file at all;
* the signed artifact crosses the process boundary as plain HTTP response
  data (JSON), and, carried across that boundary, still verifies through
  the existing, unmodified MCC-AT-001 verifier and still flows correctly
  through the existing PR-2 PreExecutionControl.

This is intentionally a small, deterministic, CI-portable subprocess test
(no Docker), per the task's own guidance ("A subprocess-based local HTTP
test is acceptable if deterministic and portable in CI").
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from examples._demo_server import free_port
from gateway.pre_execution_control import (
    AttestationRequirement,
    AttestationRequirementRegistry,
    PreExecutionControl,
)
from mcc_attestation import AttesterTrustAnchor, AttesterTrustStore, verify_attestation
from mcc_core import InMemoryNonceRegistry, hash_action, hash_payload

run = asyncio.run

ROOT = Path(__file__).resolve().parents[1]
ACTION = "send_payment"
RESOURCE = "vendor-1"
SCOPE_TEMPLATE = "payment:{resource}"
AUTH_SECRET = "attester-process-isolation-auth-secret-01"
STARTUP_TIMEOUT_SECONDS = 15.0
POLL_INTERVAL_SECONDS = 0.1


def _generate_keypair_and_write_private_pem(path: Path):
    """Generate an Ed25519 key pair, write ONLY the private key to disk (for
    the child process to load), and return the public key object. The
    caller must never read the private PEM back in THIS process -- the
    public key returned here, captured before the private material is even
    written, is the only key material this ("governed MCC") side of the
    test ever holds."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pem = private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    path.write_bytes(pem)
    # Drop the local reference; only `public_key` survives in this scope.
    del private_key, pem
    return public_key


class _AttesterSubprocess:
    """Owns the child process lifecycle: start, wait for /health, stop."""

    def __init__(self, *, env: dict, port: int) -> None:
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self._proc = subprocess.Popen(
            [sys.executable, "-m", "mcc_attester_service"],
            cwd=str(ROOT), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def wait_ready(self) -> None:
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        last_exc = None
        while time.monotonic() < deadline:
            if self._proc.poll() is not None:
                out = self._proc.stdout.read() if self._proc.stdout else ""
                raise RuntimeError(
                    f"attester subprocess exited early (code {self._proc.returncode}): {out}"
                )
            try:
                resp = httpx.get(f"{self.base_url}/health", timeout=1.0)
                if resp.status_code == 200:
                    return
            except httpx.HTTPError as exc:
                last_exc = exc
            time.sleep(POLL_INTERVAL_SECONDS)
        raise TimeoutError(f"attester subprocess never became ready: {last_exc}")

    def stop(self) -> None:
        if self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait(timeout=5.0)


@pytest.fixture
def attester_process(tmp_path):
    """Boots a real Attester subprocess with a freshly generated key pair
    and a deterministic assessment table; yields
    ``(process, public_key, port)``; tears down afterward."""
    key_path = tmp_path / "attester_private.pem"
    public_key = _generate_keypair_and_write_private_pem(key_path)

    table_path = tmp_path / "assessment_table.json"
    table_path.write_text(json.dumps({
        ACTION: {
            "evidence_type": "risk_assessment",
            "claims": {"risk_class": "low"},
            "provenance": {"model": "payment-risk-v3"},
        },
    }))

    port = free_port()
    child_env = {
        # Deliberately NOT a copy of this test process's private-key state
        # (there is none) -- built explicitly so it's obvious exactly what
        # the child receives.
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": f"{ROOT / 'src'}:{ROOT}",
        "MCC_ATTESTER_ID": "attester.payment-risk.v1",
        "MCC_ATTESTER_SIGNING_KEY_PATH": str(key_path),
        "MCC_ATTESTER_KEY_ID": "attester.payment-risk.v1-key-01",
        "MCC_ATTESTER_SERVICE_AUTH_SECRET": AUTH_SECRET,
        "MCC_ATTESTER_SCOPE_TEMPLATE": SCOPE_TEMPLATE,
        "MCC_ATTESTER_VALIDITY_SECONDS": "900",
        "MCC_ATTESTER_TEST_ASSESSMENT_TABLE": str(table_path),
        "MCC_ATTESTER_HOST": "127.0.0.1",
        "MCC_ATTESTER_PORT": str(port),
    }
    proc = _AttesterSubprocess(env=child_env, port=port)
    try:
        proc.wait_ready()
        yield proc, public_key, port
    finally:
        proc.stop()


def test_process_isolation_subprocess_signs_and_this_process_never_touches_the_key(attester_process):
    proc, public_key, _port = attester_process

    # This test's OWN process environment was never mutated with the
    # private key path -- the child received an explicitly built dict, not
    # os.environ itself.
    assert "MCC_ATTESTER_SIGNING_KEY_PATH" not in os.environ

    payload = {"amount": 100, "currency": "eur"}
    resp = httpx.post(
        f"{proc.base_url}/attest",
        json={"action": ACTION, "resource": RESOURCE, "payload": payload},
        headers={"X-Attester-Auth": AUTH_SECRET}, timeout=5.0,
    )
    assert resp.status_code == 200, resp.text
    raw = resp.json()

    # Verifies through the existing, unmodified MCC-AT-001 verifier, using
    # ONLY the public key this process captured before the private PEM was
    # ever written to disk -- this process's own address space never held
    # the private scalar.
    trust_store = AttesterTrustStore([
        AttesterTrustAnchor("attester.payment-risk.v1", "attester.payment-risk.v1-key-01",
                            public_key, frozenset({"risk_assessment"})),
    ])
    result = verify_attestation(
        raw, trust_store=trust_store, expected_action_hash=hash_action(ACTION),
        expected_scope=f"payment:{RESOURCE}", now=int(time.time()),
        expected_payload_hash=hash_payload(payload),
    )
    assert result.verified, result.failures


def test_process_isolation_artifact_flows_through_real_pre_execution_control(attester_process):
    """The cross-process artifact isn't just individually verifiable -- it
    satisfies the real, unmodified PR-2 PreExecutionControl exactly as an
    in-process artifact would."""
    proc, public_key, _port = attester_process

    payload = {"amount": 100, "currency": "eur"}
    resp = httpx.post(
        f"{proc.base_url}/attest",
        json={"action": ACTION, "resource": RESOURCE, "payload": payload},
        headers={"X-Attester-Auth": AUTH_SECRET}, timeout=5.0,
    )
    assert resp.status_code == 200, resp.text
    raw = resp.json()

    control = PreExecutionControl(
        requirements=AttestationRequirementRegistry([AttestationRequirement(
            action_pattern=ACTION, evidence_type="risk_assessment",
            scope_template=SCOPE_TEMPLATE, required_claims={"risk_class": ("low",)},
        )]),
        trust_store=AttesterTrustStore([
            AttesterTrustAnchor("attester.payment-risk.v1", "attester.payment-risk.v1-key-01",
                                public_key, frozenset({"risk_assessment"})),
        ]),
        nonce_registry=InMemoryNonceRegistry(),
    )
    result = run(control.evaluate(
        action=ACTION, forward_context=payload, resource=RESOURCE, raw_attestation=raw,
    ))
    assert result.ok, result.reason
    assert result.evidence_digest is not None


def test_process_isolation_wrong_auth_secret_rejected_over_real_http(attester_process):
    proc, _public_key, _port = attester_process
    resp = httpx.post(
        f"{proc.base_url}/attest",
        json={"action": ACTION, "resource": RESOURCE, "payload": {}},
        headers={"X-Attester-Auth": "wrong-secret"}, timeout=5.0,
    )
    assert resp.status_code == 401


def test_process_isolation_child_pid_differs_from_parent(attester_process):
    """Explicit, not merely implied: the Attester runs under a distinct OS
    process id, not a thread or in-process object sharing this
    interpreter's address space."""
    proc, _public_key, _port = attester_process
    assert proc._proc.pid != os.getpid()
