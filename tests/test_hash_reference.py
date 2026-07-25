"""Direct behavioral tests for the MCC-CM-001 structured Hash Reference
(``src/mcc_evidence/hash_reference.py``), covering the Wave A selected
requirements: CM-HASH-001, CM-HASH-002, CM-HASH-004.

CM-HASH-003 ("Every Evidence Bundle Reference MUST include at least one
Hash Reference") is deliberately NOT covered here -- it is an obligation on
the Evidence Bundle Reference object defined by MCC-CM-001 Section 14,
which does not exist yet (Wave B). See
conformance/normative-v1.0/remediation/wave-a-evidence-bundle-scope-manifest.md
for the exclusion rationale.
"""

from __future__ import annotations

import pytest

from mcc_evidence.hash_reference import (
    SUPPORTED_HASH_ALGORITHMS,
    HashReference,
    HashReferenceError,
    compute_hash_reference,
    verify_hash_reference,
)


# ---------------------------------------------------------------------------
# CM-HASH-001: a Hash Reference MUST identify a Digest, a hash algorithm, and
# the content it corresponds to.
# ---------------------------------------------------------------------------


def test_cm_hash_001_structure_identifies_digest_algorithm_and_content():
    ref = compute_hash_reference(b"hello world", content_ref="evidence/item1.json")
    assert ref.digest.startswith("sha256:")
    assert ref.algorithm == "sha256"
    assert ref.content_ref == "evidence/item1.json"
    d = ref.to_dict()
    assert set(d) == {"digest", "algorithm", "content_ref"}


def test_cm_hash_001_round_trips_through_to_dict_from_dict():
    ref = compute_hash_reference(b"payload", content_ref="bundle_descriptor.json")
    restored = HashReference.from_dict(ref.to_dict())
    assert restored == ref


def test_cm_hash_001_from_dict_rejects_missing_field():
    with pytest.raises(HashReferenceError):
        HashReference.from_dict({"digest": "sha256:" + "a" * 64, "algorithm": "sha256"})


def test_cm_hash_001_from_dict_rejects_non_object():
    with pytest.raises(HashReferenceError):
        HashReference.from_dict("not-an-object")


def test_cm_hash_001_from_dict_rejects_empty_string_field():
    with pytest.raises(HashReferenceError):
        HashReference.from_dict({"digest": "", "algorithm": "sha256", "content_ref": "x"})


# ---------------------------------------------------------------------------
# CM-HASH-002: Hash Reference algorithms MUST be collision-resistant.
# ---------------------------------------------------------------------------


def test_cm_hash_002_sha256_is_supported():
    assert "sha256" in SUPPORTED_HASH_ALGORITHMS


def test_cm_hash_002_md5_is_rejected_as_non_collision_resistant():
    assert "md5" not in SUPPORTED_HASH_ALGORITHMS


def test_cm_hash_002_sha1_is_rejected_as_non_collision_resistant():
    assert "sha1" not in SUPPORTED_HASH_ALGORITHMS


def test_cm_hash_002_compute_refuses_unsupported_algorithm():
    with pytest.raises(HashReferenceError):
        compute_hash_reference(b"data", content_ref="x", algorithm="md5")


def test_cm_hash_002_validate_rejects_unsupported_algorithm():
    ref = HashReference(digest="md5:" + "a" * 32, algorithm="md5", content_ref="x")
    problems = ref.validate()
    assert problems
    assert "not collision-resistant" in problems[0] or "not supported" in problems[0]


def test_cm_hash_002_verify_fails_closed_for_unsupported_algorithm():
    ref = HashReference(digest="md5:" + "a" * 32, algorithm="md5", content_ref="x")
    assert verify_hash_reference(ref, b"data") is False


# ---------------------------------------------------------------------------
# CM-HASH-004: Hash References MUST be independently recomputable and
# verifiable by a validator.
# ---------------------------------------------------------------------------


def test_cm_hash_004_verify_succeeds_for_matching_content():
    data = b"the quick brown fox"
    ref = compute_hash_reference(data, content_ref="evidence/x.bin")
    assert verify_hash_reference(ref, data) is True


def test_cm_hash_004_verify_fails_for_mismatched_content():
    ref = compute_hash_reference(b"original content", content_ref="evidence/x.bin")
    assert verify_hash_reference(ref, b"tampered content") is False


def test_cm_hash_004_verify_fails_closed_for_malformed_digest_syntax():
    ref = HashReference(digest="sha256:not-valid-hex", algorithm="sha256", content_ref="x")
    assert ref.validate()  # non-empty: syntax problem reported
    assert verify_hash_reference(ref, b"anything") is False


def test_cm_hash_004_verify_fails_closed_for_wrong_length_digest():
    ref = HashReference(digest="sha256:" + "a" * 10, algorithm="sha256", content_ref="x")
    assert verify_hash_reference(ref, b"anything") is False


def test_cm_hash_004_recomputation_is_deterministic_across_calls():
    data = b"deterministic input"
    ref1 = compute_hash_reference(data, content_ref="c")
    ref2 = compute_hash_reference(data, content_ref="c")
    assert ref1 == ref2
