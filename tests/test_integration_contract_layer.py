"""Normative Integration Contract layer — reconcile tests (PR #43).

These cover the *canonical normative layer* added on top of the existing
``mcc_client`` models (which remain the single source of truth):

  * contract version + deterministic, fail-closed compatibility;
  * the stable error taxonomy (codes ↔ categories ↔ retryability) and its mapping
    from the SDK exception hierarchy;
  * the conformance manifest (deterministic; no drift vs the committed golden);
  * the framework-neutral golden vectors, replayed offline;
  * backward compatibility: no new top-level exports, facade parity intact;
  * the reconcile guard: the contract layer defines NO parallel data models and
    performs no I/O.

Deterministic and fully offline: no gateway, no network, no LLM.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk" / "python" / "src"))

import mcc_client  # noqa: E402
from mcc_client import Decision, Verdict  # noqa: E402
from mcc_client import contract as C  # noqa: E402
from mcc_client import exceptions as E  # noqa: E402
from mcc_client.exceptions import MCCProtocolError  # noqa: E402

VECTORS = ROOT / "tests" / "contract_vectors"
MANIFEST_GOLDEN = ROOT / "docs" / "contract" / "conformance-manifest.json"


def _load(name: str):
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Contract identity + version.                                                #
# --------------------------------------------------------------------------- #

def test_contract_version_is_single_sourced_and_wellformed():
    assert C.CONTRACT_VERSION == f"{C.CONTRACT_MAJOR}.{C.CONTRACT_MINOR}"
    assert C.CONTRACT_MAJOR in C.SUPPORTED_MAJORS
    assert C.CONTRACT_IDENTIFIER == "mcc-integration-contract"


def test_contract_version_distinct_from_package_version():
    # Contract version and distribution version are separate concepts.
    assert C.CONTRACT_VERSION != mcc_client.__version__


# --------------------------------------------------------------------------- #
# Version compatibility — golden vectors + explicit fail-closed.              #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("vec", _load("versions.json"), ids=lambda v: v["id"])
def test_version_vectors(vec):
    res = C.check_version_compatibility(vec["input"])
    exp = vec["expected"]
    assert res.compatible is exp["compatible"]
    if exp["error_code"] is None:
        assert res.error_code is None
        if "newer_minor" in exp:
            assert res.newer_minor is exp["newer_minor"]
    else:
        assert res.error_code is C.ContractErrorCode(exp["error_code"])


def test_unsupported_major_fails_closed():
    res = C.check_version_compatibility("2.0")
    assert not res.compatible
    assert res.error_code is C.ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED


def test_check_version_is_pure_and_deterministic():
    a = C.check_version_compatibility("1.0")
    b = C.check_version_compatibility("1.0")
    assert a == b  # frozen dataclass value equality


# --------------------------------------------------------------------------- #
# Error taxonomy — golden vectors + exhaustiveness.                           #
# --------------------------------------------------------------------------- #

# Map the vector's exception name to a constructed instance (args where required).
_EXC_INSTANCES = {
    "MCCTimeoutError": E.MCCTimeoutError("t"),
    "MCCTransportError": E.MCCTransportError("t"),
    "MCCAuthenticationError": E.MCCAuthenticationError("a"),
    "MCCDeniedError": E.MCCDeniedError("denied"),
    "MCCApprovalRequiredError": E.MCCApprovalRequiredError("escalate"),
    "MCCInvalidDecisionError": E.MCCInvalidDecisionError("bind"),
    "MCCReplayError": E.MCCReplayError("replay"),
    "MCCAmbiguousExecutionError": E.MCCAmbiguousExecutionError("ambiguous"),
    "MCCExecutionError": E.MCCExecutionError("failed"),
    "MCCProtocolError": E.MCCProtocolError("proto"),
    "MCCError": E.MCCError("base"),
}


@pytest.mark.parametrize("vec", _load("errors.json"), ids=lambda v: v["id"])
def test_error_vectors(vec):
    exc = _EXC_INSTANCES[vec["exception"]]
    code = C.error_code_for_exception(exc)
    exp = vec["expected"]
    assert code is C.ContractErrorCode(exp["code"])
    assert C.category_of(code) is C.ErrorCategory(exp["category"])
    assert C.is_retryable(code) is exp["retryable"]


def test_every_sdk_exception_maps_to_a_code():
    # Every concrete MCCError subclass resolves to a stable code (never unmapped).
    for name in mcc_client.exceptions.__all__:
        cls = getattr(E, name)
        try:
            inst = cls("x")
        except TypeError:
            inst = cls("x")  # all take a message-positional; keep simple
        code = C.error_code_for_exception(inst)
        assert isinstance(code, C.ContractErrorCode)


def test_non_mcc_exception_fails_closed_to_internal():
    assert C.error_code_for_exception(ValueError("boom")) is C.ContractErrorCode.INTERNAL_ERROR


def test_every_code_has_exactly_one_category():
    for code in C.ContractErrorCode:
        assert isinstance(C.category_of(code), C.ErrorCategory)


def test_only_transport_codes_are_retryable():
    for code in C.ContractErrorCode:
        if C.is_retryable(code):
            assert C.category_of(code) is C.ErrorCategory.TRANSPORT


# --------------------------------------------------------------------------- #
# Decision golden vectors — through the EXISTING canonical model.             #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("vec", _load("decisions.json"), ids=lambda v: v["id"])
def test_decision_vectors_through_canonical_model(vec):
    req = vec["request"]
    exp = vec["expected"]
    if exp["outcome"] == "invalid":
        with pytest.raises(MCCProtocolError):
            Decision.from_response(vec["response"], requested_actor=req["actor_id"],
                                   requested_action=req["action"],
                                   requested_resource=req.get("resource"),
                                   requested_payload=req.get("payload"))
        return
    d = Decision.from_response(vec["response"], requested_actor=req["actor_id"],
                              requested_action=req["action"],
                              requested_resource=req.get("resource"),
                              requested_payload=req.get("payload"))
    assert d.verdict is Verdict(exp["verdict"])
    assert d.executable is exp["executable"]
    if "authorized_payload" in exp:
        assert d.authorized_payload == exp["authorized_payload"]


# --------------------------------------------------------------------------- #
# Conformance manifest — deterministic, no drift, self-consistent.           #
# --------------------------------------------------------------------------- #

def test_manifest_is_deterministic_and_json_serializable():
    m1 = C.conformance_manifest()
    m2 = C.conformance_manifest()
    assert m1 == m2
    json.dumps(m1)  # must be serializable


def test_manifest_matches_committed_golden_no_drift():
    live = json.loads(json.dumps(C.conformance_manifest(), sort_keys=True))
    golden = json.loads(json.dumps(json.loads(MANIFEST_GOLDEN.read_text()), sort_keys=True))
    assert live == golden, (
        "conformance manifest drifted from docs/contract/conformance-manifest.json; "
        "regenerate it from mcc_client.contract.conformance_manifest()"
    )


def test_manifest_is_internally_consistent():
    m = C.conformance_manifest()
    assert m["contract_version"] == C.CONTRACT_VERSION
    assert m["supported_verdicts"] == [v.value for v in Verdict]
    assert set(m["error_categories"]) == {c.value for c in C.ErrorCategory}
    codes = {e["code"] for e in m["error_codes"]}
    assert codes == {c.value for c in C.ContractErrorCode}
    for e in m["error_codes"]:
        assert e["category"] == C.category_of(C.ContractErrorCode(e["code"])).value
    assert m["certifies_any_adapter"] is False
    assert m["framework_neutral"] is True


def test_manifest_invariants_match_module_constant():
    m = C.conformance_manifest()
    assert tuple(m["required_security_invariants"]) == C.REQUIRED_SECURITY_INVARIANTS


# --------------------------------------------------------------------------- #
# Backward compatibility — no new top-level exports, facade parity intact.    #
# --------------------------------------------------------------------------- #

_FROZEN_CLIENT_ALL = {
    "__version__", "MCCClient", "Authorization", "Transport",
    "Verdict", "Decision", "Approval", "ExecutionResult",
    "ApprovalAuthorization", "MandateAuthorization", "ConsensusAuthorization",
    "Payload",
    "MCCError", "MCCTransportError", "MCCTimeoutError", "MCCProtocolError",
    "MCCAuthenticationError", "MCCDeniedError", "MCCApprovalRequiredError",
    "MCCInvalidDecisionError", "MCCReplayError", "MCCExecutionError",
    "MCCAmbiguousExecutionError",
}


def test_top_level_client_exports_are_unchanged():
    # The contract layer is a SUBMODULE (mcc_client.contract); it adds no new
    # top-level public exports and so cannot perturb the frozen facade parity.
    assert set(mcc_client.__all__) == _FROZEN_CLIENT_ALL


def test_facade_parity_still_holds():
    import mcc
    for name in mcc_client.__all__:
        if name.startswith("__"):
            continue
        assert name in mcc.__all__


def test_contract_submodule_is_importable_and_exports_layer():
    for name in ("CONTRACT_VERSION", "check_version_compatibility",
                 "error_code_for_exception", "conformance_manifest",
                 "ContractErrorCode", "ErrorCategory", "VersionCompatibility"):
        assert hasattr(C, name)
        assert name in C.__all__


# --------------------------------------------------------------------------- #
# Reconcile guard — no parallel models, no I/O, framework-neutral.            #
# --------------------------------------------------------------------------- #

def test_contract_layer_defines_no_parallel_models():
    # It must NOT introduce a second Decision/Verdict/ExecutionResult/Request type.
    import inspect
    forbidden = {"Decision", "Verdict", "ExecutionResult", "GovernanceRequest",
                 "GovernanceDecision", "ExecutionAuthorization", "IntegrationDescriptor",
                 "ActorDescriptor", "ResourceDescriptor", "ActionDescriptor"}
    own_classes = {
        name for name, obj in vars(C).items()
        if inspect.isclass(obj) and getattr(obj, "__module__", "") == C.__name__
    }
    assert not (own_classes & forbidden), (
        f"contract layer defines parallel models: {own_classes & forbidden}"
    )
    # If it references Verdict at all, it must be the SAME object as the SDK's.
    assert C.Verdict is Verdict if hasattr(C, "Verdict") else True


def test_contract_layer_performs_no_io():
    # Pure module: no network/socket/subprocess/file libraries imported.
    src = (ROOT / "sdk" / "python" / "src" / "mcc_client" / "contract.py").read_text()
    for banned in ("import httpx", "import requests", "import socket",
                   "import urllib", "subprocess", "open(", "import os"):
        assert banned not in src, f"contract layer must be pure; found {banned!r}"


def test_contract_layer_and_manifest_are_framework_neutral():
    frameworks = ("voltagent", "langgraph", "crewai", "openai", "autogen",
                  "semantic_kernel", "semantickernel", "adk")
    src = (ROOT / "sdk" / "python" / "src" / "mcc_client" / "contract.py").read_text().lower()
    for fw in frameworks:
        assert fw not in src, f"framework name {fw!r} leaked into the normative layer"
    manifest_text = json.dumps(C.conformance_manifest()).lower()
    for fw in frameworks:
        assert fw not in manifest_text


def test_spec_pins_the_normative_statement():
    doc = (ROOT / "docs" / "INTEGRATION_CONTRACT.md").read_text(encoding="utf-8")
    assert "Status: Normative" in doc
    # The pinned framing: spec is normative; models are implementation artifacts;
    # adapters (incl. VoltAgent) conform but do not define the contract.
    assert "canonical implementation artifacts" in doc
    assert "do not define the contract" in doc
    for section in ("Traceability matrix", "Invariant ownership matrix",
                    "Negative guarantees", "Stable error taxonomy",
                    "Contract versioning", "Change-control policy",
                    "Lifecycle and state transitions"):
        assert section in doc, f"spec missing normative section: {section}"
