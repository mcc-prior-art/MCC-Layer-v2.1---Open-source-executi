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

from examples.gpt6_astra_reference.astra_provider import AstraResponse, DeterministicAstraProvider
from examples.gpt6_astra_reference.evidence import TerminalStatus, classify_exec_outcome
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig, GitHubActuatorConfigError, GitHubActuatorDisabledError, GitHubIssueActuator,
    build_marked_payload,
)
from examples.gpt6_astra_reference.models import (
    AstraNonCanonicalActionError, AstraProposal, AstraProposalError, parse_proposal, require_canonical_action,
)
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
        proposal = AstraProposal(
            action=ACTION, resource=stack.demo_repo,
            payload=build_marked_payload({"title": "t", "body": "b"}, logical_operation_id="op-test-5"),
        )
        outcome = run(run_positive_path(
            stack.service, mandate=bad_mandate, actor=ACTOR, proposal=proposal, attestation=None,
            logical_operation_id="op-test-5",
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


# ---------------------------------------------------------------------------
# 16-18. Live-shaped non-canonical action contract (regression: a real
# OpenAI-compatible endpoint proposed "github.create_issue" instead of the
# canonical "create_github_issue"); complete, independent scenario reporting
# even when a positive-shaped proposal is denied or would otherwise raise
# AuthorityDeniedError. No network access, no OpenAI credentials -- the
# live provider is replaced with an in-process test double that reproduces
# the exact observed shape.
# ---------------------------------------------------------------------------


class _FixedActionProvider:
    """Test double standing in for a live ``OpenAIAstraProvider``: always
    returns exactly one proposal with a fixed action/resource, regardless of
    the task string. Used to deterministically reproduce, offline, the
    live-model failure modes this regression guards against -- a
    non-canonical action identifier, or a canonical action for an
    out-of-mandate resource."""

    def __init__(self, action: str, resource: str = DEMO_REPO) -> None:
        self._action = action
        self._resource = resource

    async def propose(self, task: str) -> AstraResponse:
        proposal = AstraProposal(action=self._action, resource=self._resource,
                                 payload={"title": "t", "body": "b"})
        return AstraResponse(outcome=[proposal], is_live=True, model="gpt-6-astra")


def test_16_require_canonical_action_rejects_the_live_shaped_alias():
    """The exact mismatch observed live: the model said "github.create_issue"
    where the mandate is scoped to the canonical "create_github_issue". This
    must be rejected outright -- never normalized or aliased."""
    proposal = AstraProposal(action="github.create_issue", resource=DEMO_REPO, payload={})
    with pytest.raises(AstraNonCanonicalActionError):
        require_canonical_action(proposal, ACTION)


def test_16_require_canonical_action_accepts_the_exact_canonical_identifier():
    proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={})
    assert require_canonical_action(proposal, ACTION) is proposal


def test_16_positive_scenario_fails_closed_on_non_canonical_action_not_a_crash(monkeypatch):
    """Regression test for the exact live failure observed against a real
    OpenAI-compatible endpoint (gpt-6-astra): the model proposed
    'github.create_issue' instead of the canonical 'create_github_issue'.
    This must be reported as an ASTRA_ERROR -- MCC is never invoked, no
    alias is accepted, and the scenario function must not raise."""
    from examples.gpt6_astra_reference import cli as cli_module

    monkeypatch.setattr(
        cli_module.OpenAIAstraProvider, "from_env",
        classmethod(lambda cls, env=None: _FixedActionProvider("github.create_issue")),
    )
    trace = run(run_positive(live_astra=True))
    assert trace.terminal_status == TerminalStatus.ASTRA_ERROR
    assert trace.gate_accepted is None  # MCC was never invoked
    assert trace.actuator_invocations == 0
    assert "github.create_issue" in trace.notes[0]
    assert "create_github_issue" in trace.notes[0]


def test_17_tamper_scenario_reports_completely_on_authority_denial_not_a_crash(monkeypatch):
    """Regression test for 'every CLI scenario is independent': when
    authority issuance itself is denied before a token exists, the scenario
    must return a complete, classified RunTrace instead of letting
    AuthorityDeniedError propagate out of the scenario function.

    The proposal here is fully canonical -- exact action AND exact resource
    -- so it clears the proposal-contract check cleanly; the denial is
    forced one layer deeper, at real MCC mandate-signature verification (a
    forged mandate signature), decoupled from anything the model itself
    proposed. A live model producing a non-canonical action/resource is
    covered separately (test_16/test_20); this test covers a genuine
    authority-layer denial that the contract check does NOT and must NOT
    intercept."""
    from examples.gpt6_astra_reference import _localstack as localstack_module
    from examples.gpt6_astra_reference import cli as cli_module

    real_issue_mandate = localstack_module.issue_mandate

    def _forged_issue_mandate(*args, **kwargs):
        mandate = dict(real_issue_mandate(*args, **kwargs))
        mandate["sig"] = "tampered-signature-value"
        return mandate

    monkeypatch.setattr(localstack_module, "issue_mandate", _forged_issue_mandate)
    monkeypatch.setattr(
        cli_module.OpenAIAstraProvider, "from_env",
        classmethod(lambda cls, env=None: _FixedActionProvider(ACTION, resource=DEMO_REPO)),
    )
    trace = run(run_tamper(live_astra=True))
    assert trace.terminal_status == TerminalStatus.MCC_AUTHORITY_DENY
    assert "INVALID_MANDATE_SIGNATURE" in trace.gate_reason
    assert trace.actuator_invocations == 0


def test_18_all_scenarios_report_even_after_a_positive_path_denial(monkeypatch, capsys):
    """System-level regression test for 'all --live-astra must continue
    through and report every scenario even if the positive scenario is
    denied or raises AuthorityDeniedError': force every scenario's live
    Astra call to return the same live-shaped non-canonical proposal, and
    assert the CLI driver still reaches and reports every single scenario,
    with no unhandled traceback."""
    from examples.gpt6_astra_reference import cli as cli_module

    monkeypatch.setattr(
        cli_module.OpenAIAstraProvider, "from_env",
        classmethod(lambda cls, env=None: _FixedActionProvider("github.create_issue")),
    )
    exit_code = run(cli_module._main(["all", "--live-astra"]))
    out = capsys.readouterr().out
    for name in cli_module._SCENARIOS:
        assert f"===== scenario: {name} =====" in out, f"scenario {name!r} was never reported"
    assert "Traceback" not in out
    assert "[SCENARIO ERROR]" not in out
    # None of these scenarios can prove their invariant with a rejected,
    # non-canonical proposal -- the run correctly reports failure, but by
    # completing and reporting every scenario, never by crashing.
    assert exit_code == 1


# ---------------------------------------------------------------------------
# 19-21. Canonical RESOURCE contract (regression: a live run proposed the
# correct canonical action but a paraphrased/URL-form resource -- the task
# prompts stated the exact required action but only described the resource
# as "the configured demo repository", never its exact identifier -- and
# was denied deep in the chain with RESOURCE_SCOPE_MISMATCH). And:
# RunTrace.render() now surfaces notes, with secret-shaped substrings
# sanitized.
# ---------------------------------------------------------------------------


def test_19_require_canonical_resource_rejects_a_non_canonical_resource():
    from examples.gpt6_astra_reference.models import AstraNonCanonicalResourceError, require_canonical_resource

    proposal = AstraProposal(action=ACTION, resource="https://github.com/owner/mcc-astra-demo-sandbox",
                             payload={})
    with pytest.raises(AstraNonCanonicalResourceError):
        require_canonical_resource(proposal, DEMO_REPO)


def test_19_require_canonical_resource_accepts_the_exact_canonical_identifier():
    from examples.gpt6_astra_reference.models import require_canonical_resource

    proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={})
    assert require_canonical_resource(proposal, DEMO_REPO) is proposal


def test_19_require_canonical_proposal_checks_action_before_resource():
    """When both action and resource are non-canonical, the action check
    fires first -- a stable, deterministic failure precedence, not a
    fallback or partial acceptance of either field."""
    from examples.gpt6_astra_reference.models import AstraNonCanonicalActionError, require_canonical_proposal

    proposal = AstraProposal(action="github.create_issue", resource="some/other-repo", payload={})
    with pytest.raises(AstraNonCanonicalActionError):
        require_canonical_proposal(proposal, canonical_action=ACTION, canonical_resource=DEMO_REPO)


def test_20_positive_scenario_fails_closed_on_non_canonical_resource_not_a_crash(monkeypatch):
    """Regression test for the exact live failure observed: the model
    proposed the correct canonical action but a URL-form paraphrase of the
    resource instead of the exact canonical repository identifier. This
    must be reported as ASTRA_ERROR -- MCC is never invoked, no alias or
    URL-vs-slug equivalence is accepted -- and the scenario must not raise."""
    from examples.gpt6_astra_reference import cli as cli_module

    monkeypatch.setattr(
        cli_module.OpenAIAstraProvider, "from_env",
        classmethod(lambda cls, env=None: _FixedActionProvider(
            ACTION, resource="https://github.com/owner/mcc-astra-demo-sandbox",
        )),
    )
    trace = run(run_positive(live_astra=True))
    assert trace.terminal_status == TerminalStatus.ASTRA_ERROR
    assert trace.gate_accepted is None  # MCC was never invoked
    assert trace.actuator_invocations == 0
    assert "https://github.com/owner/mcc-astra-demo-sandbox" in trace.notes[0]
    assert DEMO_REPO in trace.notes[0]


def test_20_wrong_scope_scenario_reaches_the_gate_when_resource_matches_its_own_contract(monkeypatch):
    """Complementary check: a live-shaped proposal that DOES supply the
    exact canonical resource this task requires -- even the deliberately
    out-of-mandate WRONG_SCOPE_RESOURCE -- must reach the Attester/Gate
    rather than being rejected at the contract layer, proving the fix
    rejects only genuinely non-canonical values, not every live proposal."""
    from examples.gpt6_astra_reference import cli as cli_module

    monkeypatch.setattr(
        cli_module.OpenAIAstraProvider, "from_env",
        classmethod(lambda cls, env=None: _FixedActionProvider(
            ACTION, resource=cli_module.WRONG_SCOPE_RESOURCE,
        )),
    )
    trace = run(run_wrong_scope(live_astra=True))
    assert trace.terminal_status == TerminalStatus.MCC_AUTHORITY_DENY
    assert "RESOURCE_SCOPE_MISMATCH" in trace.gate_reason
    assert trace.actuator_invocations == 0


def test_21_render_includes_a_notes_section():
    trace = run(run_replay())
    rendered = trace.render()
    assert "[NOTES]" in rendered
    assert "first enforce:" in rendered
    assert "second enforce (replay):" in rendered


def test_21_render_and_to_dict_sanitize_secret_shaped_notes():
    """Defense in depth: even if a note ever carried a secret-shaped
    substring, RunTrace must never render or serialize it verbatim."""
    import json

    from examples.gpt6_astra_reference.evidence import RunTrace

    trace = RunTrace(
        scenario="synthetic", astra_is_live=True, astra_model="gpt-6-astra",
        proposal_fingerprint=None, attestation_status=None, attestation_fingerprint=None,
        control_decision=None, authority_fingerprint=None, gate_accepted=None, gate_reason=None,
        actuator_invocations=0, actuator_result=None, terminal_status=TerminalStatus.ASTRA_ERROR,
        notes=["OpenAI request failed: Authorization: Bearer sk-testFAKEsecretvalue1234567890",
               "leaked token ghp_1234567890abcdefFAKE"],
    )
    rendered = trace.render()
    assert "sk-testFAKEsecretvalue1234567890" not in rendered
    assert "ghp_1234567890abcdefFAKE" not in rendered
    assert "[REDACTED]" in rendered
    serialized = json.dumps(trace.to_dict())
    assert "sk-testFAKEsecretvalue1234567890" not in serialized
    assert "ghp_1234567890abcdefFAKE" not in serialized
