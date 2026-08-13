"""A DELIBERATELY vulnerable reference actuator -- the negative control
(PR #71).

An assurance suite that always reports PASS is not evidence of anything;
it could just as easily never be exercising the properties it claims to
check. This module is a small, self-contained, KNOWINGLY BROKEN reference
service exposing the SAME wire shape as ``egress_proxy``'s real
``POST /v1/http/execute`` (method/url/headers/body/actor/resource/
transaction_id/idempotency_key/challenge_id/votes in, an outcome/executed
JSON response out) but with the real invariants deliberately removed:

* no client API key check at all;
* no destination allowlist / SSRF check -- any host, any port;
* no consensus/signature verification -- ANY votes (or none at all)
  authorize execution;
* no replay protection -- the same request can be resubmitted forever;
* the outbound call always actually happens.

``assurance/tests/test_negative_control.py`` runs a subset of Workstream
A's real attacks against THIS target instead of the real actuator and
asserts they SUCCEED here -- proving the assurance suite has genuine
discriminating power (it can tell a broken system from a correct one),
not just that it always reports PASS. This is provisioning/fixture code,
like the rest of ``assurance/sut/`` -- it is never imported by anything
outside ``assurance/`` and never used as a stand-in for the real actuator
anywhere else in this repository.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]

VIOLATED_INVARIANTS = (
    "no client authentication (any caller, any key, is accepted)",
    "no destination allowlist / SSRF check (any host, any port is reachable)",
    "no consensus or signature verification (any votes, or none, authorize execution)",
    "no replay protection (the identical request executes again on resubmission)",
)


def build_vulnerable_app():
    from fastapi import FastAPI

    app = FastAPI(title="MCC-Core Negative Control -- DELIBERATELY VULNERABLE, never deploy")

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"status": "ok", "warning": "this service is a deliberately vulnerable negative control"}

    @app.post("/v1/http/execute")
    async def execute(req: Dict[str, Any]) -> Dict[str, Any]:
        # VULNERABILITY: no API key dependency at all -- contrast with
        # egress_proxy.app's require_api_key.
        # VULNERABILITY: no challenge/votes verification -- contrast with
        # egress_proxy's mandatory two-round consensus handshake. Any
        # request -- with garbage votes, no votes, or a replayed body --
        # executes on the FIRST call.
        # VULNERABILITY: no SSRF/allowed_hosts validation -- contrast with
        # egress_proxy.ssrf.validate_destination.
        method = req.get("method", "GET")
        url = req.get("url", "")
        body = req.get("body")
        headers = req.get("headers") or {}
        try:
            async with httpx.AsyncClient() as client:
                r = await client.request(
                    method, url, headers=headers,
                    json=body if isinstance(body, dict) else None,
                    content=body if isinstance(body, (str, bytes)) else None,
                    timeout=10.0,
                )
            return {"outcome": "ALLOW", "executed": True, "upstream_status": r.status_code,
                     "upstream_body": r.text[:2000]}
        except Exception as exc:  # noqa: BLE001 -- a negative control does not need to be robust
            return {"outcome": "ALLOW", "executed": False, "reason": f"upstream error: {exc}"}

    return app


@dataclass
class VulnerableTarget:
    base_url: str
    _proc: Any

    def close(self) -> None:
        try:
            self._proc.terminate()
            self._proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            self._proc.kill()

    def __enter__(self) -> "VulnerableTarget":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def spawn_vulnerable_target(*, port: Optional[int] = None) -> VulnerableTarget:
    import os
    import subprocess
    import time

    from assurance.sut.harness import free_port

    p = port if port is not None else free_port()
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(REPO_ROOT / "src"), str(REPO_ROOT), str(REPO_ROOT / "sdk" / "python" / "src"),
                       env.get("PYTHONPATH")])
    )
    proc = subprocess.Popen(
        [sys.executable, "-m", "assurance.sut.vulnerable_target", "--port", str(p)],
        cwd=str(REPO_ROOT), env=env,
    )
    base_url = f"http://127.0.0.1:{p}"
    deadline = time.time() + 15.0
    last_error: Optional[Exception] = None
    while time.time() < deadline:
        try:
            r = httpx.get(f"{base_url}/health", timeout=1.0)
            if r.status_code < 500:
                return VulnerableTarget(base_url=base_url, _proc=proc)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(0.1)
    proc.terminate()
    raise RuntimeError(f"vulnerable target did not become ready in time: {last_error}")


@dataclass
class NegativeControlEnvironment:
    target: VulnerableTarget
    notify_url: str
    _notify_proc: Any

    def notification_receipt_count(self) -> int:
        return httpx.get(f"{self.notify_url}/receipts", timeout=5.0).json()["count"]

    def close(self) -> None:
        self.target.close()
        try:
            self._notify_proc.terminate()
            self._notify_proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            self._notify_proc.kill()

    def __enter__(self) -> "NegativeControlEnvironment":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def spawn_negative_control_environment() -> NegativeControlEnvironment:
    """The vulnerable target plus its OWN dedicated, local external-effect
    sink -- so the negative control's attacks stay fully offline (no
    dependency on live internet access) while still proving a real
    unauthenticated outbound call actually reaches something observable."""
    import os
    import subprocess
    import time

    from assurance.sut.harness import free_port

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(REPO_ROOT / "src"), str(REPO_ROOT), str(REPO_ROOT / "sdk" / "python" / "src"),
                       env.get("PYTHONPATH")])
    )
    notify_port = free_port()
    notify_proc = subprocess.Popen(
        [sys.executable, "-m", "assurance.sut.notify_process", "--port", str(notify_port)],
        cwd=str(REPO_ROOT), env=env,
    )
    notify_url = f"http://127.0.0.1:{notify_port}"
    deadline = time.time() + 15.0
    last_error: Optional[Exception] = None
    while time.time() < deadline:
        try:
            r = httpx.get(f"{notify_url}/health", timeout=1.0)
            if r.status_code < 500:
                break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(0.1)
    else:
        notify_proc.terminate()
        raise RuntimeError(f"negative-control notify sink did not become ready in time: {last_error}")

    target = spawn_vulnerable_target()
    return NegativeControlEnvironment(target=target, notify_url=notify_url, _notify_proc=notify_proc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    import uvicorn

    uvicorn.run(build_vulnerable_app(), host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
