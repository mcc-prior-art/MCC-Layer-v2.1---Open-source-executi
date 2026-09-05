"""GPT-6 Astra Reference Integration — offline test suite.

No OpenAI or GitHub credentials are required for anything in this file;
every scenario runs the REAL MCC-Core chain (Attester -> PreExecutionControl
-> DecisionEngine -> ExecutionGate -> EnforcementCoordinator) with the
offline ``DeterministicAstraProvider`` and the local mock GitHub service.
Live-credential tests, if any are added later, must be separately opt-in
and skipped when credentials are absent (Phase 10's explicit requirement) —
this file contains none.
"""

from __future__ import annotations

import asyncio

import pytest

from examples.gpt6_astra_reference.astra_provider import DeterministicAstraProvider
from examples.gpt6_astra_reference.evidence import TerminalStatus, classify_exec_outcome
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig, GitHubActuatorConfigError, GitHubActuatorDisabledError, GitHubIssueActuator,
)
from examples.gpt6_astra_reference.models import AstraProposal, AstraProposalError, parse_proposal
from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.pipeline import (
    run_positive_path,
)
from examples.gpt6_astra_reference.cli import (
    DEMO_REPO, run_autonomous_expansion, run_expired, run_positive, run_replay,
    run_self_refusal, run_tamper, run_wrong_scope,
)

run = asyncio.run


# ---------------------------------------------------------------------------
# 1/2/3. Strict Astra proposal schema; trusted fields rejected; malformed
# model output fails closed.
# ---------------------------------------------------------------------------


def test_1_strict_schema_accepts_the_closed_shape():
    p = parse_proposal({"action": "create_github_issue", "resource": "o/r",
                        "payload": {"title": "t"}, "reason": "why"})
    assert isinstance(p, AstraProposal)
    assert p.action == "create_github_issue" and p.resource == "o/r"


@pytest.mark.parametrize("field_name", [
    "verified", "authority", "execution_token", "token", "decision_token", "attestation",
    "attestation_signature", "sig", "attester_id", "kid", "nonce", "action_hash",
    "payload_hash", "evidence_digest", "policy_hash", "policy_version",
    "issued_at", "not_before", "expires_at", "exp", "nbf", "iat", "mandate", "mandate_id",
])
def test_2_model_cannot_submit_trusted_mcc_fields(field_name):
    raw = {"action": "create_github_issue", "resource": "o/r", "payload": {}, field_name: "x"}
    with pytest.raises(AstraProposalError, match="forbidden trusted field"):
        parse_proposal(raw)


@pytest.mark.parametrize("raw", [
    "not a dict", 123, None, [], {}, {"resource": "o/r"}, {"action": "a"},
    {"action": "a", "resource": "o/r", "unexpected_field": "x"},
    {"action": "", "resource": "o/r"}, {"action": "a", "resource": ""},
])
def test_3_malformed_model_output_fails_closed(raw):
    with pytest.raises(AstraProposalError):
        parse_proposal(raw)


def test_3_malformed_fixture_produces_astra_error_not_a_crash():
    provider = DeterministicAstraProvider({"bad-task": {"action": "x"}})  # missing resource
    resp = run(provider.propose("bad-task"))
    from examples.gpt6_astra_reference.models import AstraError

    assert isinstance(resp.outcome, AstraError)


# ---------------------------------------------------------------------------
# 4. The Astra adapter cannot call the actuator directly (static + behavioral).
# ---------------------------------------------------------------------------


def test_4_astra_provider_module_never_imports_the_actuator():
    import ast
    from pathlib import Path

    for name in ("astra_provider.py", "models.py"):
        path = Path("examples/gpt6_astra_reference") / name
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name)
        assert not any("github_actuator" in n or "mock_github_service" in n for n in names), (
            f"{name} must never import the actuator or its mock service"
        )


def test_4_astra_provider_has_no_actuate_or_execute_method():
    provider = DeterministicAstraProvider({})
    forbidden = {"execute", "actuate", "call_github", "create_issue", "run"}
    assert not (forbidden & set(dir(provider)))


# ---------------------------------------------------------------------------
# 5. The actuator cannot run without Gate success.
# ---------------------------------------------------------------------------


def test_5_actuator_not_called_when_authority_verification_fails():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        calls = {"n": 0}

        async def counting_upstream(action, payload):
            calls["n"] += 1
            return {"ok": True}

        stack.upstream = counting_upstream
        bad_mandate = dict(stack.mandate)
        bad_mandate["sig"] = "tampered-signature-value"
        proposal = AstraProposal(action=ACTION, resource=stack.demo_repo, payload={"title": "t", "body": "b"})
        outcome = run(run_positive_path(
            stack.service, mandate=bad_mandate, actor=ACTOR, proposal=proposal, attestation=None,
        ))
        assert outcome.status != "EXECUTED"
        assert calls["n"] == 0


# ---------------------------------------------------------------------------
# 6/7. Deny-source attribution; self-refusal is not an MCC denial.
# ---------------------------------------------------------------------------


def test_6_classify_exec_outcome_authority_layer():
    assert classify_exec_outcome("ACTION_SCOPE_MISMATCH: action outside mandate scope") == \
        TerminalStatus.MCC_AUTHORITY_DENY
    assert classify_exec_outcome("RESOURCE_SCOPE_MISMATCH: resource outside mandate scope") == \
        TerminalStatus.MCC_AUTHORITY_DENY
    assert classify_exec_outcome("UNTRUSTED_ISSUER: unknown or revoked issuer key") == \
        TerminalStatus.MCC_AUTHORITY_DENY


def test_6_classify_exec_outcome_control_layer():
    assert classify_exec_outcome("ATTESTATION_REQUIRED: no attestation supplied") == \
        TerminalStatus.MCC_CONTROL_DENY
    assert classify_exec_outcome("ATTESTATION_SCOPE_MISMATCH: scope mismatch") == \
        TerminalStatus.MCC_CONTROL_DENY


def test_6_classify_exec_outcome_attestation_layer():
    assert classify_exec_outcome("ATTESTER_UNTRUSTED: unknown attester") == \
        TerminalStatus.MCC_ATTESTATION_DENY
    assert classify_exec_outcome("ATTESTATION_REPLAYED: nonce already consumed") == \
        TerminalStatus.MCC_ATTESTATION_DENY


def test_6_classify_exec_outcome_gate_layer_catch_all():
    assert classify_exec_outcome("NONCE_REJECTED: replay or registry unavailable") == \
        TerminalStatus.MCC_GATE_DENY
    assert classify_exec_outcome("PAYLOAD_HASH_MISMATCH: payload differs") == TerminalStatus.MCC_GATE_DENY
    assert classify_exec_outcome("TOKEN_EXPIRED") == TerminalStatus.MCC_GATE_DENY


def test_7_self_refusal_is_not_reported_as_an_mcc_denial():
    trace = run(run_self_refusal())
    assert trace.terminal_status == TerminalStatus.ASTRA_SELF_REFUSAL
    assert trace.terminal_status not in (
        TerminalStatus.MCC_ATTESTATION_DENY, TerminalStatus.MCC_CONTROL_DENY,
        TerminalStatus.MCC_AUTHORITY_DENY, TerminalStatus.MCC_GATE_DENY,
    )
    assert trace.actuator_invocations == 0
    assert trace.gate_accepted is None  # MCC was never invoked at all


# ---------------------------------------------------------------------------
# 8-12. The six scenarios, dual-oracle.
# ---------------------------------------------------------------------------


def test_scenario_positive_executes_and_actuates_once():
    trace = run(run_positive())
    assert trace.terminal_status == TerminalStatus.EXECUTED
    assert trace.actuator_invocations == 1
    assert trace.actuator_result is not None


def test_8_tamper_no_actuator_invocation():
    trace = run(run_tamper())
    assert trace.terminal_status == TerminalStatus.MCC_GATE_DENY
    assert "PAYLOAD_HASH_MISMATCH" in trace.gate_reason
    assert trace.actuator_invocations == 0


def test_9_replay_exactly_one_actuator_invocation():
    trace = run(run_replay())
    assert trace.terminal_status == TerminalStatus.MCC_GATE_DENY
    assert "NONCE_REJECTED" in trace.gate_reason
    assert trace.actuator_invocations == 1


def test_10_expired_no_actuator_invocation():
    trace = run(run_expired())
    assert trace.terminal_status == TerminalStatus.MCC_GATE_DENY
    assert "TOKEN_EXPIRED" in trace.gate_reason
    assert trace.actuator_invocations == 0


def test_11_wrong_scope_no_actuator_invocation():
    trace = run(run_wrong_scope())
    assert trace.terminal_status == TerminalStatus.MCC_AUTHORITY_DENY
    assert "RESOURCE_SCOPE_MISMATCH" in trace.gate_reason
    assert trace.actuator_invocations == 0


def test_12_autonomous_scope_expansion_denied():
    trace = run(run_autonomous_expansion())
    assert trace.terminal_status == TerminalStatus.MCC_AUTHORITY_DENY
    assert "ACTION_SCOPE_MISMATCH" in trace.gate_reason
    # exactly the PRIMARY action actuated once; the extra action never did.
    assert trace.actuator_invocations == 1


# ---------------------------------------------------------------------------
# 13. Evidence artifact excludes secrets.
# ---------------------------------------------------------------------------


_FORBIDDEN_SUBSTRINGS = ("sk-", "Bearer ", "BEGIN PRIVATE KEY", "ghp_", "github_pat_")


def test_13_evidence_trace_excludes_secrets():
    trace = run(run_positive())
    rendered = trace.render()
    for forbidden in _FORBIDDEN_SUBSTRINGS:
        assert forbidden not in rendered
    d = trace.to_dict()
    import json

    serialized = json.dumps(d)
    for forbidden in _FORBIDDEN_SUBSTRINGS:
        assert forbidden not in serialized
    # No raw token, no raw private key material -- only fingerprints (hashes).
    assert "token" not in d or d.get("authority_fingerprint") != d.get("proposal_fingerprint")


# ---------------------------------------------------------------------------
# 14/15. Live mode disabled by default; explicit repo configuration required.
# ---------------------------------------------------------------------------


def test_14_live_mode_disabled_by_default():
    config = GitHubActuatorConfig.from_env({})
    assert config.mode == "disabled"
    actuator = GitHubIssueActuator(config)
    with pytest.raises(GitHubActuatorDisabledError):
        run(actuator("create_github_issue", {"title": "t", "body": "b"}))


def test_14_disabled_actuator_never_makes_an_http_call(monkeypatch):
    import httpx

    def _boom(*a, **k):  # pragma: no cover - must never be reached
        raise AssertionError("disabled actuator must never construct an HTTP client")

    monkeypatch.setattr(httpx, "AsyncClient", _boom)
    actuator = GitHubIssueActuator(GitHubActuatorConfig.from_env({}))
    with pytest.raises(GitHubActuatorDisabledError):
        run(actuator("create_github_issue", {"title": "t"}))


def test_15_live_mode_requires_explicit_repo():
    with pytest.raises(GitHubActuatorConfigError):
        GitHubActuatorConfig.from_env({"MCC_ASTRA_DEMO_MODE": "live"})


def test_15_live_mode_refuses_the_mcc_core_repo_itself():
    with pytest.raises(GitHubActuatorConfigError):
        GitHubActuatorConfig.from_env({
            "MCC_ASTRA_DEMO_MODE": "live", "MCC_ASTRA_GITHUB_REPO": "mcc-prior-art/mcc-layer",
        })


def test_15_unknown_mode_refused():
    with pytest.raises(GitHubActuatorConfigError):
        GitHubActuatorConfig.from_env({"MCC_ASTRA_DEMO_MODE": "enabled"})


def test_15_disabled_actuator_refuses_unsupported_action():
    config = GitHubActuatorConfig.from_env({
        "MCC_ASTRA_DEMO_MODE": "live", "MCC_ASTRA_GITHUB_REPO": "owner/sandbox",
        "MCC_ASTRA_GITHUB_BASE_URL": "http://127.0.0.1:1",
    })
    actuator = GitHubIssueActuator(config)
    with pytest.raises(GitHubActuatorDisabledError):
        run(actuator("delete_repository", {}))
