"""PR #69 architecture guards -- the five ecosystems are certification
SUBJECTS, never certification AUTHORITIES. These complement (never
duplicate) ``test_mcc_certify_architecture_guards.py`` (PR #67, general
runtime-governance/adapter-framework import guards, parametrized over
every file in ``src/mcc_certify`` including ``ecosystems.py``/``aggregate.py``)
and ``test_mcc_certify_trust_publication_guards.py`` (PR #68, trust/
publication/signing guards).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "src" / "mcc_certify"
ADAPTERS_DIR = REPO_ROOT / "tests" / "interoperability" / "adapters"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _imported_modules(source: str) -> set:
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _adapter_files():
    return sorted(ADAPTERS_DIR.glob("*.py"))


# ---------------------------------------------------------------------------
# No adapter signs, verifies trust, or writes publication -- adapters are
# certification subjects, not certification authorities.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", _adapter_files(), ids=lambda p: p.name)
def test_no_adapter_imports_mcc_certify(path: Path):
    imported = _imported_modules(_source(path))
    hits = {m for m in imported if m == "mcc_certify" or m.startswith("mcc_certify.")}
    assert not hits, f"{path}: an ecosystem adapter must never import the certification package: {hits}"


@pytest.mark.parametrize("path", _adapter_files(), ids=lambda p: p.name)
def test_no_adapter_references_certificate_trust_or_publication_symbols(path: Path):
    forbidden_substrings = (
        "sign_technical_certificate", "build_technical_certificate", "TrustAnchor",
        "PublicationRecord", "PublicationIndex", "IssuerIdentity", "SigningKeyProvider",
        "verify_technical_certificate", "CertificationPipeline",
    )
    source = _source(path)
    hits = [s for s in forbidden_substrings if s in source]
    assert not hits, f"{path}: an ecosystem adapter references certification-authority symbols: {hits}"


@pytest.mark.parametrize("path", _adapter_files(), ids=lambda p: p.name)
def test_no_adapter_defines_its_own_certificate_evidence_or_manifest_format(path: Path):
    tree = ast.parse(_source(path))
    defined = {n.name for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
    forbidden = defined & {
        "TechnicalCertificate", "EvidenceBundle", "CertificationManifest", "HashReference",
        "PublicationRecord", "PublicationIndex", "TrustAnchorRegistry",
    }
    assert not forbidden, f"{path}: defines its own certification-artifact type: {forbidden}"


# ---------------------------------------------------------------------------
# No CertificationTarget defines its own trusted key / embeds a private key.
# ---------------------------------------------------------------------------


def test_certification_target_dataclass_carries_no_trust_or_key_fields():
    from mcc_certify.target import CertificationTarget

    field_names = set(CertificationTarget.__dataclass_fields__.keys())
    forbidden_words = {"trust", "signing", "issuer", "private_key", "publickey", "key_id"}
    hits = {f for f in field_names if any(word in f.lower() for word in forbidden_words)}
    assert not hits, f"CertificationTarget declares a trust/signing-shaped field: {hits}"


def test_ecosystems_module_never_calls_private_bytes():
    source = (PACKAGE_DIR / "ecosystems.py").read_text(encoding="utf-8")
    assert ".private_bytes(" not in source


def test_ecosystems_module_never_contains_pem_material():
    source = (PACKAGE_DIR / "ecosystems.py").read_text(encoding="utf-8")
    assert "BEGIN PRIVATE KEY" not in source
    assert "BEGIN EC PRIVATE KEY" not in source


# ---------------------------------------------------------------------------
# No ecosystem bypasses `mcc certify`, creates its own certificate, evidence
# bundle format, manifest format, or offline verifier; no second pipeline.
# ---------------------------------------------------------------------------


def test_ecosystems_module_defines_no_second_certification_pipeline():
    source = (PACKAGE_DIR / "ecosystems.py").read_text(encoding="utf-8")
    for forbidden in ("class CertificationPipeline", "def verify_technical_certificate",
                      "def build_technical_certificate", "def compute_hash_reference",
                      "def sign_token", "Ed25519PrivateKey.generate("):
        assert forbidden not in source, f"ecosystems.py must not redefine: {forbidden!r}"


def test_aggregate_module_defines_no_second_publication_or_certificate_model():
    source = (PACKAGE_DIR / "aggregate.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    forbidden = defined & {"PublicationRecord", "PublicationIndex", "TechnicalCertificate", "HashReference"}
    assert not forbidden, f"aggregate.py redefines an existing model: {forbidden}"
    imported = _imported_modules(source)
    assert "mcc_certify.publication" not in imported  # imported via relative .publication
    assert ".publication" in source or "from .publication import" in source


def test_all_five_ecosystem_targets_share_the_same_pipeline_and_verifier():
    # Static guard: every ecosystem target builder produces a plain
    # CertificationTarget consumed by the ONE CertificationPipeline -- there
    # is no per-ecosystem branch anywhere in pipeline.py's control flow.
    pipeline_source = (PACKAGE_DIR / "pipeline.py").read_text(encoding="utf-8")
    for forbidden in ("generic-http", "langgraph", "crewai", "autogen", "voltagent",
                      "GENERIC_HTTP_TARGET_ID", "LANGGRAPH_TARGET_ID"):
        assert forbidden not in pipeline_source, (
            f"pipeline.py must not special-case an ecosystem by name ({forbidden!r}) -- "
            "all targets share one identical pipeline implementation"
        )


def test_ecosystems_module_never_imports_argparse_or_defines_a_cli():
    source = (PACKAGE_DIR / "ecosystems.py").read_text(encoding="utf-8")
    assert "argparse" not in source
    assert "def main(" not in source


# ---------------------------------------------------------------------------
# Fixture signing cannot produce official status; test issuer artifacts
# cannot enter the official publication set; cross-target evidence reuse
# is rejected -- static confirmations that the checks exist, complementing
# the behavioral proof in test_mcc_certify_pr69.py.
# ---------------------------------------------------------------------------


def test_aggregate_checks_target_id_before_accepting_a_publication_record():
    source = (PACKAGE_DIR / "aggregate.py").read_text(encoding="utf-8")
    assert "record.target_id != target_id" in source


def test_aggregate_rejects_missing_publication_record_rather_than_defaulting():
    source = (PACKAGE_DIR / "aggregate.py").read_text(encoding="utf-8")
    assert "publication-record.json" in source
    assert "not record_path.exists()" in source


def test_pipeline_official_mode_still_rejects_fixture_signing_key_provider():
    # Same invariant PR #68 established, re-confirmed here because ecosystem
    # certification is the first real consumer of official mode at scale.
    source = (PACKAGE_DIR / "pipeline.py").read_text(encoding="utf-8")
    assert "signing_key_provider.is_fixture" in source


def test_ecosystem_targets_never_short_circuit_run_conformance_checks():
    # Static guard: CertificationTarget.run_conformance_checks (the ONE
    # entry point every target -- ecosystem or fixture -- goes through) is
    # never bypassed by ecosystems.py; ecosystems.py calls only the
    # public conformance_entry_point contract, never a private pipeline hook.
    source = (PACKAGE_DIR / "ecosystems.py").read_text(encoding="utf-8")
    assert "run_conformance_checks" not in source, (
        "ecosystems.py must not call run_conformance_checks itself -- that is the "
        "pipeline's job when it certifies a resolved target"
    )


# ---------------------------------------------------------------------------
# No adapter framework import at module scope in the new PR #69 files
# (complements test_mcc_certify_architecture_guards.py's existing
# parametrized guard, which already covers ecosystems.py/aggregate.py).
# ---------------------------------------------------------------------------


def test_ecosystems_module_only_imports_frameworks_lazily():
    tree = ast.parse((PACKAGE_DIR / "ecosystems.py").read_text(encoding="utf-8"))
    module_level_imports = set()
    for node in tree.body:  # top-level statements only, not nested in functions
        if isinstance(node, ast.Import):
            module_level_imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_level_imports.add(node.module)
    forbidden = {"langgraph", "autogen_core", "autogen_agentchat", "crewai", "mcc_compliance.capability_profile"}
    hits = {m for m in module_level_imports if any(m == f or m.startswith(f + ".") for f in forbidden)}
    assert not hits, f"ecosystems.py imports a framework/heavy dependency at module scope: {hits}"
    assert "tests.interoperability" not in " ".join(module_level_imports), (
        "ecosystems.py must not import tests.interoperability at module scope -- only lazily, "
        "inside each target's conformance_entry_point"
    )
