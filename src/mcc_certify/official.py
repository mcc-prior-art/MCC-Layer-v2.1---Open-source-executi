"""Official-Certificate Eligibility Gate (PR #70).

There is exactly one place in this repository that decides whether a
certification run may be labelled OFFICIAL: this module. It is not a
string field, not a CLI flag, and not something a caller can assert --
:func:`evaluate_official_eligibility` re-derives eligibility from first
principles every time, against the actual artifacts on disk, and returns
an enumerated list of every failing condition rather than a bare boolean.

A run is OFFICIAL only when ALL of the following independently hold:

1. it is one of the five approved reference ecosystem targets
   (``mcc_certify.aggregate.REQUIRED_ECOSYSTEM_TARGET_IDS`` -- reused, not
   redeclared);
2. its Technical Certificate declares the registered production Issuer
   (``PRODUCTION_ISSUER_ID``) -- checked as an explicit string comparison,
   which is necessary but never sufficient on its own;
3. the run was actually certified in official mode (a
   ``publication-record.json`` exists -- a candidate/fixture run never
   produces one, see ``pipeline.py``'s official-mode gating from PR #68);
4. trusted offline verification (:func:`mcc_certify.verify.verify_certification_run_trusted`)
   against the caller-supplied OFFICIAL Trust Store passes -- this is the
   cryptographic check: a candidate/fixture-signed certificate's signature
   simply does not verify against a Trust Store that only recognizes the
   real production Issuer's public key, independent of what the
   certificate's own ``issuer_id`` string claims;
5. (when a publication index is supplied) the certificate is present in
   the published set;
6. (when an expected source commit is supplied) the run's own recorded
   provenance names that exact commit -- binding the certificate to the
   exact certified source state, not merely "some commit".

Because check 4 is a real Ed25519 signature verification against a Trust
Store the caller controls, a candidate or fixture issuer is
**cryptographically** unable to produce a result this function calls
eligible for OFFICIAL status when evaluated against the real official
Trust Store -- the check does not rely on the ``issuer_id`` string alone.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from .aggregate import REQUIRED_ECOSYSTEM_TARGET_IDS
from .pipeline import CERTIFICATE_FILE, PUBLICATION_RECORD_FILE, RUN_METADATA_FILE
from .publication import PublicationIndex
from .target import CertifyError
from .trust_store import TrustStore
from .verify import RunVerificationError, verify_certification_run_trusted

#: The one, stable, versioned production Issuer identity every official
#: certificate must declare. Reused from the operator tooling
#: (``scripts/generate_production_issuer_identity.py``) -- defined once
#: here so code and tooling never drift.
PRODUCTION_ISSUER_ID = "mcc-official-certification-issuer-v1"


class OfficialEligibilityError(CertifyError):
    """The run directory itself could not be evaluated at all (missing a
    required artifact) -- distinct from a failing eligibility *result*,
    which is returned by :func:`evaluate_official_eligibility`, never
    raised, so a caller always gets a complete, enumerated reason list."""


@dataclass(frozen=True)
class OfficialEligibility:
    """The one, centralized eligibility verdict. ``eligible`` is True iff
    ``reasons`` is empty -- there is no other way to become eligible, and
    no caller may override this by setting a flag."""

    target_id: str
    certificate_id: Optional[str]
    eligible: bool
    reasons: Tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "target_id": self.target_id,
            "certificate_id": self.certificate_id,
            "eligible": self.eligible,
            "reasons": list(self.reasons),
        }


def evaluate_official_eligibility(
    run_dir: Path | str,
    *,
    trust_store: TrustStore,
    publication_index: Optional[PublicationIndex] = None,
    expected_source_commit_sha: Optional[str] = None,
    production_issuer_id: str = PRODUCTION_ISSUER_ID,
) -> OfficialEligibility:
    run_dir = Path(run_dir)
    required = (RUN_METADATA_FILE, CERTIFICATE_FILE)
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise OfficialEligibilityError(f"run directory {run_dir} is missing required artifact(s): {missing}")

    run_metadata = json.loads((run_dir / RUN_METADATA_FILE).read_bytes())
    cert = json.loads((run_dir / CERTIFICATE_FILE).read_bytes())
    target_id = run_metadata.get("target_id")
    certificate_id = cert.get("certificate_id")

    reasons = []

    if target_id not in REQUIRED_ECOSYSTEM_TARGET_IDS:
        reasons.append(
            f"target_id {target_id!r} is not one of the five approved reference ecosystems "
            f"({sorted(REQUIRED_ECOSYSTEM_TARGET_IDS)})"
        )

    declared_issuer_id = cert.get("issuer_id")
    if declared_issuer_id != production_issuer_id:
        reasons.append(
            f"certificate issuer_id {declared_issuer_id!r} is not the registered production issuer "
            f"{production_issuer_id!r}"
        )

    if not (run_dir / PUBLICATION_RECORD_FILE).exists():
        reasons.append(
            "no publication-record.json present -- this run was not certified in official mode "
            "(candidate/fixture runs never produce one)"
        )

    try:
        report = verify_certification_run_trusted(
            run_dir, trust_store=trust_store, publication_index=publication_index,
            require_published=publication_index is not None,
        )
    except RunVerificationError as e:
        reasons.append(f"trusted offline verification could not be performed: {e}")
    else:
        if not report["valid"]:
            reasons.append(f"trusted offline verification failed: {report['failures']}")

    if expected_source_commit_sha is not None:
        actual_commit = (run_metadata.get("provenance") or {}).get("source_commit_sha")
        if actual_commit != expected_source_commit_sha:
            reasons.append(
                f"source_commit_sha {actual_commit!r} does not match the expected ceremony commit "
                f"{expected_source_commit_sha!r}"
            )

    return OfficialEligibility(
        target_id=target_id, certificate_id=certificate_id, eligible=not reasons, reasons=tuple(reasons),
    )


__all__ = [
    "PRODUCTION_ISSUER_ID",
    "OfficialEligibilityError",
    "OfficialEligibility",
    "evaluate_official_eligibility",
]
