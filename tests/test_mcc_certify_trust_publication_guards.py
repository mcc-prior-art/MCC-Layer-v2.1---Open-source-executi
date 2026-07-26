"""PR #68 architecture guards -- Trust Anchor / Issuer Signing-Key /
Publication foundation. These complement (never duplicate)
``tests/test_mcc_certify_architecture_guards.py``'s general
runtime-governance-import and adapter-framework-import guards, which
already run against every file in ``src/mcc_certify`` including the four
new PR #68 modules (``issuer.py``, ``trust_store.py``,
``signing_provider.py``, ``publication.py``).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "src" / "mcc_certify"

_NETWORK_MODULES = {
    "socket", "urllib", "urllib.request", "http.client", "requests", "httpx",
    "aiohttp", "websockets", "ftplib", "smtplib", "telnetlib",
}


def _py_files():
    return sorted(PACKAGE_DIR.rglob("*.py"))


def _source(name: str) -> str:
    return (PACKAGE_DIR / name).read_text(encoding="utf-8")


def _imported_modules(source: str) -> set:
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


# ---------------------------------------------------------------------------
# No private key material is ever exported/serialized outside the one
# provider module that legitimately loads it into memory.
# ---------------------------------------------------------------------------


def test_private_bytes_never_called_outside_signing_provider():
    # ``.private_bytes(`` (a call on a key object, used to *export/serialize*
    # key material) is distinct from constructors like
    # ``Ed25519PrivateKey.from_private_bytes(seed)`` (building a key object
    # *from* raw bytes the caller already produced) -- only the former is
    # the export/serialization operation this guard forbids outside the one
    # module that legitimately loads real key material into memory.
    for path in _py_files():
        if path.name == "signing_provider.py":
            continue
        source = path.read_text(encoding="utf-8")
        assert ".private_bytes(" not in source, (
            f"{path}: exports/serializes private key bytes outside signing_provider.py"
        )


def test_no_module_writes_a_pem_or_private_key_literal():
    forbidden_substrings = ("BEGIN PRIVATE KEY", "BEGIN EC PRIVATE KEY", "BEGIN RSA PRIVATE KEY")
    for path in _py_files():
        source = path.read_text(encoding="utf-8")
        for needle in forbidden_substrings:
            assert needle not in source, f"{path}: contains a private-key PEM literal ({needle!r})"


def test_evidence_and_certificate_artifacts_never_carry_key_material_fields():
    # Static guard: neither the Publication Record nor the Issuer Identity
    # to_dict() serializers reference a private-key-shaped field name.
    forbidden = {"private_key", "private_bytes", "signing_key_pem", "secret_key"}
    for name in ("issuer.py", "publication.py", "trust_store.py"):
        source = _source(name)
        tree = ast.parse(source)
        string_literals = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        hits = forbidden & {s.lower() for s in string_literals}
        assert not hits, f"{name}: references a private-key-shaped dict key {hits}"


# ---------------------------------------------------------------------------
# No certificate self-trust: nothing that establishes a Trust Anchor may be
# derived from a Technical Certificate's own declared content.
# ---------------------------------------------------------------------------


def test_trust_store_never_imports_the_technical_certificate_model():
    imported = _imported_modules(_source("trust_store.py"))
    assert "mcc_evidence.tc001_certificate" not in imported or all(
        name not in _source("trust_store.py") for name in ("TechnicalCertificate", "read_tc001_certificate")
    )
    # Only the Trust Anchor / Trust Anchor Registry runtime types may be
    # imported from tc001_certificate -- never the Certificate model itself,
    # which would let a Certificate's own declared fields feed trust.
    tree = ast.parse(_source("trust_store.py"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "mcc_evidence.tc001_certificate":
            names = {alias.name for alias in node.names}
            forbidden = names & {"TechnicalCertificate", "read_tc001_certificate", "build_technical_certificate"}
            assert not forbidden, f"trust_store.py imports Certificate-producing/reading symbols: {forbidden}"


def test_issuer_identity_fingerprint_is_always_independently_recomputed():
    # The normative property under test (already unit-tested behaviorally in
    # test_mcc_certify_pr68.py): IssuerIdentity.__post_init__ recomputes the
    # fingerprint from the actual public key and rejects a mismatching
    # declared one -- this is a static guard that the source still contains
    # that recomputation-and-compare, not a declared-value passthrough.
    source = _source("issuer.py")
    assert "expected_fingerprint = public_key_fingerprint(resolved_key)" in source
    assert "self.public_key_fingerprint != expected_fingerprint" in source


# ---------------------------------------------------------------------------
# No network-based trust resolution anywhere in the trust/publication layer.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", _py_files(), ids=lambda p: p.name)
def test_no_network_imports_in_certify_package(path: Path):
    imported = _imported_modules(path.read_text(encoding="utf-8"))
    hits = {m for m in imported if any(m == f or m.startswith(f + ".") for f in _NETWORK_MODULES)}
    assert not hits, f"{path}: imports a networking module: {hits}"


def test_trust_store_and_publication_index_readers_take_only_local_paths():
    # Static guard: read_trust_store / read_publication_index / verify_*
    # accept Path|str and use Path(...).read_bytes() -- never urlopen/get/post.
    for name in ("trust_store.py", "publication.py"):
        source = _source(name)
        for forbidden in ("urlopen(", ".get(http", "requests.get", "requests.post", "httpx."):
            assert forbidden not in source, f"{name}: contains a network call pattern {forbidden!r}"


# ---------------------------------------------------------------------------
# No duplicated Hash Reference / Trust Anchor / Technical Certificate model.
# ---------------------------------------------------------------------------


def test_no_duplicate_hash_reference_or_trust_anchor_class_defined():
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        defined_classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        forbidden = defined_classes & {"HashReference", "TrustAnchor", "TechnicalCertificate", "TrustAnchorRegistry"}
        assert not forbidden, f"{path}: redefines an existing Wave A/B/C model class: {forbidden}"


def test_publication_reuses_the_existing_hash_reference_primitive():
    imported = _imported_modules(_source("publication.py"))
    assert "mcc_evidence.hash_reference" in imported
    source = _source("publication.py")
    assert "def compute_hash_reference" not in source
    assert "def verify_hash_reference" not in source


def test_trust_store_reuses_the_existing_trust_anchor_registry():
    imported = _imported_modules(_source("trust_store.py"))
    assert "mcc_evidence.tc001_certificate" in imported
    tree = ast.parse(_source("trust_store.py"))
    defined = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    assert "TrustAnchorRegistry" not in defined, "trust_store.py must reuse, not redefine, TrustAnchorRegistry"


# ---------------------------------------------------------------------------
# No adapter signing / no target-defined trust keys.
# ---------------------------------------------------------------------------


def test_certification_target_carries_no_trust_or_signing_key_surface():
    from mcc_certify.target import CertificationTarget

    field_names = set(CertificationTarget.__dataclass_fields__.keys())
    forbidden_words = {"trust", "signing", "issuer", "private_key", "publickey"}
    hits = {f for f in field_names if any(word in f.lower() for word in forbidden_words)}
    assert not hits, f"CertificationTarget declares a trust/signing-shaped field: {hits}"


def test_adapter_sdk_and_framework_modules_never_imported_by_trust_or_publication_modules():
    forbidden = {"langgraph", "autogen_core", "autogen_agentchat", "crewai", "voltagent", "mcc_adapter_sdk"}
    for name in ("issuer.py", "trust_store.py", "signing_provider.py", "publication.py"):
        imported = _imported_modules(_source(name))
        hits = {m for m in imported if any(m == f or m.startswith(f + ".") for f in forbidden)}
        assert not hits, f"{name}: imports an adapter/framework module: {hits}"


# ---------------------------------------------------------------------------
# No fixture signing accepted in official mode (static confirmation that the
# gating check exists and textually precedes certificate construction).
# ---------------------------------------------------------------------------


def test_pipeline_rejects_fixture_signing_key_provider_before_building_a_certificate():
    source = _source("pipeline.py")
    fixture_check_idx = source.index("signing_key_provider.is_fixture")
    build_cert_idx = source.index("cert = build_technical_certificate(")
    assert fixture_check_idx < build_cert_idx, (
        "the is_fixture rejection check must textually precede certificate construction"
    )


def test_pipeline_never_derives_a_fixture_key_when_official_mode_is_true():
    # In official mode, the signing key used for Stage 5 must come from the
    # validated signing_key_provider, never from _derive_signing_key.
    source = _source("pipeline.py")
    pattern = re.compile(
        r"if request\.official_mode:\s*\n\s*signing_key = official_signing_key",
    )
    assert pattern.search(source), "official_mode must select official_signing_key, not the fixture derivation"


# ---------------------------------------------------------------------------
# Publication never mutates an already-issued certificate/manifest, and the
# external persistent index is only ever touched after full success.
# ---------------------------------------------------------------------------


def test_publication_module_never_opens_certificate_or_manifest_files_for_writing():
    source = _source("publication.py")
    # Publication only ever reads bytes from the Certificate/Manifest paths
    # (to hash them) -- it must never open them for writing.
    assert "technical_certificate_path" in source
    assert re.search(r"technical_certificate_path.*write", source) is None
    assert re.search(r"certification_manifest_path.*write", source) is None


def test_external_publication_index_write_happens_after_the_run_directory_is_finalized():
    source = _source("pipeline.py")
    rename_idx = source.index("tmp_run_dir.rename(final_run_dir)")
    publish_call_idx = source.index("publish_certificate(\n                existing_publication_index")
    assert publish_call_idx > rename_idx, (
        "publish_certificate (the external, persistent index mutation) must happen strictly after "
        "the run directory has been atomically finalized"
    )
