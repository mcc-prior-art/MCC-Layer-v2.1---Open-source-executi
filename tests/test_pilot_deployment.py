"""Deployment-level pilot guarantees for the VoltAgent + MCC-Core pilot.

Two things are proven here that are specific to the *deployment*:

1. **Fail-closed without valid execution authority.** The pilot's execution
   authorization is consensus (evaluator trust) + gateway-minted single-use
   approvals — NOT the external-mandate path. This asserts that, with the pilot's
   trust posture (no ``MCC_TRUST_CONFIG`` — an empty external-mandate trust set),
   nothing executes without valid authority: no votes, forged votes, a forged
   approval mandate, and an untrusted external mandate all fail closed.

   This is why ``MCC_ENV=pilot``'s mandate-trust requirement is not applicable to
   this pilot, and why ``MCC_REDIS_NAMESPACE=pilot`` (Redis key isolation only)
   grants no authority: the two authorization mechanisms the pilot DOES use each
   have their own configured trust, and the mandate path is empty → reject-all.

2. **Bypass topology.** The pilot compose file is parsed to prove the network
   trust boundary is enforced by deployment, not documentation: the external
   service is unreachable by the agent, and the agent holds no operator key.

The cryptographic / replay / receipt failure modes themselves are covered by the
existing suites (test_mcc_core, test_consensus_enforcement,
test_governed_executor_pilot, test_voltagent_quorum, and the TypeScript suite);
this file adds the pilot-specific deployment assertions without duplicating them.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk" / "python" / "src"))

from pilot.client import MCCGatewayClient  # noqa: E402
from pilot_notify import recorded_receipts, reset_receipts  # noqa: E402

from tests._notify_harness import API_KEY, OPERATOR_KEY, NotifyPilotHarness, _free_port  # noqa: E402
from integrations.voltagent.mcc_side.evaluator_quorum import QuorumSettings, build_quorum_app  # noqa: E402
from examples._demo_server import DemoServer  # noqa: E402

COMPOSE = ROOT / "docker-compose.pilot-voltagent.yml"
ENV_EXAMPLE = ROOT / ".env.pilot.example"


# --------------------------------------------------------------------------- #
# 1. Fail-closed without valid execution authority.                           #
#                                                                             #
# NotifyPilotHarness builds the gateway with the pilot's trust posture: an     #
# empty external-mandate trust set (no MCC_TRUST_CONFIG) plus the runtime       #
# approver issuer and the evaluator consensus trust.                           #
# --------------------------------------------------------------------------- #

@pytest.fixture()
def stack():
    reset_receipts()
    hz = NotifyPilotHarness()
    q_settings = QuorumSettings({"MCC_QUORUM_GATEWAY_URL": hz.base_url, "MCC_GATEWAY_API_KEY": API_KEY})
    q_app = build_quorum_app(hz.evaluators, q_settings)
    q_port = _free_port()
    q_server = DemoServer(q_app, q_port)
    q_server.start()
    client = MCCGatewayClient(hz.base_url, api_key=API_KEY, operator_key=OPERATOR_KEY)
    try:
        yield hz, client, f"http://127.0.0.1:{q_port}"
    finally:
        q_server.stop()
        hz.close()


def _ctx(corr):
    return {"recipient": "customer-1", "message": "hi", "priority": 2, "channel": "email",
            "correlation_id": corr}


def test_consensus_without_votes_fails_closed(stack):
    hz, client, _ = stack
    d = client.propose(identity="agent/notify-bot", action="send_notification", resource_id="crm",
                       actor_id="agent/notify-bot", context=_ctx("corr-noauth"))
    assert d.decision.value == "ALLOW"
    ch = client.issue_challenge(actor="agent/notify-bot", action="send_notification",
                                resource="crm", context=d.forward_context)
    out = client.execute_with_consensus(votes=[], actor="agent/notify-bot",
                                        action="send_notification", resource="crm",
                                        context=d.forward_context, nonce=ch["nonce"],
                                        challenge_id=ch["challenge_id"])
    assert not out.executed
    assert recorded_receipts() == []


def test_consensus_with_forged_votes_fails_closed(stack):
    hz, client, _ = stack
    d = client.propose(identity="agent/notify-bot", action="send_notification", resource_id="crm",
                       actor_id="agent/notify-bot", context=_ctx("corr-forged"))
    ch = client.issue_challenge(actor="agent/notify-bot", action="send_notification",
                                resource="crm", context=d.forward_context)
    forged = [{"evaluator_id": "eval-0", "verdict": "ALLOW", "sig": "not-a-real-signature"}]
    out = client.execute_with_consensus(votes=forged, actor="agent/notify-bot",
                                        action="send_notification", resource="crm",
                                        context=d.forward_context, nonce=ch["nonce"],
                                        challenge_id=ch["challenge_id"])
    assert not out.executed
    assert recorded_receipts() == []


def test_forged_approval_mandate_fails_closed(stack):
    hz, client, _ = stack
    d = client.propose(identity="agent/unknown", action="send_notification", resource_id="crm",
                       actor_id="agent/unknown", context=_ctx("corr-escf"))
    assert d.decision.value == "ESCALATE"
    appr = client.request_approval(actor="agent/unknown", action="send_notification", resource="crm")
    # Execute with a forged (unsigned) mandate instead of an operator-granted one.
    out = client.execute_with_approval(
        appr["request_id"], mandate={"forged": True, "approval_id": appr["request_id"]},
        actor="agent/unknown", action="send_notification", resource="crm",
        context=_ctx("corr-escf"))
    assert not out.executed
    assert recorded_receipts() == []


def test_untrusted_external_mandate_rejected(stack):
    """The pilot has no MCC_TRUST_CONFIG, so the external-mandate path trusts no
    issuer: any presented mandate is rejected (strictly fail-closed)."""
    hz, client, _ = stack
    out = client.execute_with_mandate(
        mandate={"issuer": "whoever", "subject": "agent/notify-bot", "sig": "x"},
        actor="agent/notify-bot", action="send_notification", resource="crm",
        context=_ctx("corr-mand"))
    assert not out.executed
    assert recorded_receipts() == []


# --------------------------------------------------------------------------- #
# 2. Bypass topology — enforced by the deployment, not documentation.          #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def compose():
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def _networks(service) -> set:
    nets = service.get("networks", [])
    return set(nets) if isinstance(nets, list) else set(nets.keys())


def test_agent_has_no_network_path_to_external_service(compose):
    services = compose["services"]
    agent_nets = _networks(services["voltagent-agent"])
    external_nets = _networks(services["external-service"])
    # The agent and the external service must share NO network.
    assert agent_nets.isdisjoint(external_nets), (
        f"agent nets {agent_nets} must not overlap external-service nets {external_nets}")
    # And the external service is not exposed on the agent's edge network.
    assert "agent_edge" not in external_nets


def test_only_the_gateway_bridges_the_two_networks(compose):
    services = compose["services"]
    # The gateway (governed executor) is the only service on BOTH networks.
    bridged = {name for name, svc in services.items()
               if {"agent_edge", "gov_internal"}.issubset(_networks(svc))}
    assert "mcc-gateway" in bridged
    assert "external-service" not in bridged
    assert "voltagent-agent" not in bridged


def test_agent_service_holds_no_operator_key(compose):
    agent = compose["services"]["voltagent-agent"]
    env = agent.get("environment", {}) or {}
    if isinstance(env, list):
        env = dict(e.split("=", 1) for e in env if "=" in e)
    assert "MCC_GATEWAY_OPERATOR_API_KEY" not in env, "agent must not be given the operator key inline"
    # No external-service endpoint is handed to the agent either.
    assert "MCC_UPSTREAM_BASE" not in env


def test_pilot_profile_does_not_disable_governance(compose):
    gw = compose["services"]["mcc-gateway"]
    env = gw.get("environment", {}) or {}
    if isinstance(env, list):
        env = dict(e.split("=", 1) for e in env if "=" in e)
    # Enforcing mode + Redis-backed (fail-closed) state — never observe/in-memory.
    assert env.get("MCC_GATEWAY_MODE") == "inline"
    for backend in ("MCC_NONCE_BACKEND", "MCC_IDEMPOTENCY_BACKEND", "MCC_APPROVAL_BACKEND"):
        assert env.get(backend) == "redis", f"{backend} must be redis (fail-closed) in the pilot"


def test_env_example_has_no_secrets_and_is_fail_closed():
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    # The template must not disable governance and must default to the offline model.
    assert "MCC_GATEWAY_MODE=inline" in text
    assert "MCC_VOLTAGENT_MODEL_PROVIDER=deterministic" in text
    # No real-looking secret values (placeholders only).
    assert "sk-" not in text.replace("# OPENAI_API_KEY", "")
