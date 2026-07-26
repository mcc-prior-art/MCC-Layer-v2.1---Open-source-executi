"""Aggregate Five-Ecosystem Publication Set (PR #69).

CP-001 Section 9.8/8.8 Publication says nothing about aggregating multiple
Certification Subjects into one set -- this is a repository-level milestone
concern (certify all five reference ecosystems as one all-or-nothing
release), implemented entirely on top of the existing, UNCHANGED
``mcc_certify.publication`` model (``PublicationRecord``/``PublicationIndex``
from PR #68). This module introduces no new certificate format, no new
publication schema, and no parallel pipeline: it reads five already-
completed, already-officially-certified run directories (each produced by
an independent ``mcc certify <target> --issuer-config ... `` invocation,
because the five ecosystems' Python dependencies are mutually incompatible
and can never coexist in one process -- see
``tests/interoperability/requirements-*.txt`` and the per-ecosystem
isolated CI jobs), re-verifies each one with
:func:`mcc_certify.verify.verify_certification_run_trusted` against the
SAME explicit Trust Store, and merges their existing Publication Records
into one aggregate :class:`~mcc_certify.publication.PublicationIndex`.

All-or-nothing: this is a single release milestone, not five independent
ones. If any of the five ecosystems is missing, produces an invalid
certificate, fails trusted verification, or collides with another
ecosystem's certificate/target identity, :func:`build_five_ecosystem_publication_set`
raises :class:`AggregatePublicationError` and writes **no** aggregate
index at all -- there is no partial four-out-of-five publication.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .ecosystems import ECOSYSTEM_TARGET_IDS
from .publication import (
    PUBLICATION_INDEX_FILE_NAME,
    PublicationIndex,
    PublicationRecord,
    empty_publication_index,
    read_publication_record,
    write_publication_index,
)
from .target import CertifyError
from .trust_store import TrustStore
from .verify import RunVerificationError, verify_certification_run_trusted

#: Exactly the five production reference ecosystems -- reused from
#: ``mcc_certify.ecosystems``, never redeclared.
REQUIRED_ECOSYSTEM_TARGET_IDS = frozenset(ECOSYSTEM_TARGET_IDS)

PUBLICATION_RECORD_FILE_NAME = "publication-record.json"


class AggregatePublicationError(CertifyError):
    """The aggregate five-ecosystem publication set could not be built.
    All-or-nothing: raised for any missing/unexpected/failed/duplicate
    ecosystem run. No aggregate index is ever written when this is raised."""


@dataclass(frozen=True)
class EcosystemRunOutcome:
    """One ecosystem's contribution to the aggregate set -- included in
    diagnostics regardless of success or failure, so a failing aggregate
    run always identifies exactly which ecosystem(s) blocked it."""

    target_id: str
    run_dir: str
    certificate_id: Optional[str]
    valid: bool
    detail: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "target_id": self.target_id, "run_dir": self.run_dir,
            "certificate_id": self.certificate_id, "valid": self.valid, "detail": self.detail,
        }


def _evaluate_one_ecosystem(target_id: str, run_dir: Path, trust_store: TrustStore) -> Tuple[Optional[PublicationRecord], EcosystemRunOutcome]:
    try:
        report = verify_certification_run_trusted(run_dir, trust_store=trust_store)
    except RunVerificationError as e:
        return None, EcosystemRunOutcome(target_id, str(run_dir), None, False, f"trusted verification error: {e}")

    record_path = run_dir / PUBLICATION_RECORD_FILE_NAME
    if not record_path.exists():
        return None, EcosystemRunOutcome(
            target_id, str(run_dir), None, False,
            "run directory has no publication-record.json (was it certified in official mode?)",
        )
    try:
        record = read_publication_record(record_path)
    except CertifyError as e:
        return None, EcosystemRunOutcome(target_id, str(run_dir), None, False, f"malformed publication record: {e}")

    if record.target_id != target_id:
        return None, EcosystemRunOutcome(
            target_id, str(run_dir), record.certificate_id, False,
            f"publication record target_id {record.target_id!r} does not match the expected {target_id!r} "
            "-- refusing (cross-target substitution)",
        )
    if not report["valid"]:
        return None, EcosystemRunOutcome(
            target_id, str(run_dir), record.certificate_id, False,
            f"trusted offline verification failed: {report['failures']}",
        )
    return record, EcosystemRunOutcome(target_id, str(run_dir), record.certificate_id, True, "OK")


def build_five_ecosystem_publication_set(
    run_dirs: Dict[str, Path],
    *,
    trust_store: TrustStore,
    aggregate_publication_dir: Path,
) -> Tuple[PublicationIndex, Tuple[EcosystemRunOutcome, ...]]:
    """Build the aggregate Publication Index for exactly the five required
    ecosystems. All-or-nothing: raises :class:`AggregatePublicationError`
    (never writes anything) unless every ecosystem is present, unique,
    trusted-offline-verifies, and contributes a distinct certificate id."""
    provided_ids = set(run_dirs)
    missing = REQUIRED_ECOSYSTEM_TARGET_IDS - provided_ids
    unexpected = provided_ids - REQUIRED_ECOSYSTEM_TARGET_IDS
    if missing or unexpected:
        raise AggregatePublicationError(
            f"aggregate five-ecosystem publication requires exactly "
            f"{sorted(REQUIRED_ECOSYSTEM_TARGET_IDS)}; missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )

    outcomes: List[EcosystemRunOutcome] = []
    records: List[PublicationRecord] = []
    certificate_ids_seen = set()

    for target_id in sorted(run_dirs):
        record, outcome = _evaluate_one_ecosystem(target_id, Path(run_dirs[target_id]), trust_store)
        outcomes.append(outcome)
        if record is None:
            continue
        if record.certificate_id in certificate_ids_seen:
            outcomes[-1] = EcosystemRunOutcome(
                target_id, outcome.run_dir, record.certificate_id, False,
                f"duplicate certificate_id {record.certificate_id!r} across ecosystems -- refusing",
            )
            continue
        certificate_ids_seen.add(record.certificate_id)
        records.append(record)

    if len(records) != len(REQUIRED_ECOSYSTEM_TARGET_IDS) or not all(o.valid for o in outcomes):
        raise AggregatePublicationError(
            "all-or-nothing: not every required ecosystem produced a valid, uniquely-identified, "
            f"trusted certificate: {[o.to_dict() for o in outcomes]}"
        )

    index = empty_publication_index()
    for record in records:
        index = index.add(record)
    if len(index.records) != len(REQUIRED_ECOSYSTEM_TARGET_IDS):
        raise AggregatePublicationError(
            f"internal inconsistency: aggregate index has {len(index.records)} record(s), "
            f"expected exactly {len(REQUIRED_ECOSYSTEM_TARGET_IDS)}"
        )

    write_publication_index(index, Path(aggregate_publication_dir) / PUBLICATION_INDEX_FILE_NAME)
    return index, tuple(outcomes)


def verify_aggregate_publication_set(
    aggregate_publication_dir: Path,
    *,
    trust_store: TrustStore,
    run_dirs: Dict[str, Path],
) -> Tuple[bool, List[str]]:
    """Independently re-verify an already-built aggregate Publication Index:
    exactly five records, exactly the five required target ids (via the
    supplied run directories' own publication records), no duplicates, and
    every one still trusted-offline-verifies. Never mutates anything."""
    from .publication import read_publication_index

    failures: List[str] = []
    index_path = Path(aggregate_publication_dir) / PUBLICATION_INDEX_FILE_NAME
    if not index_path.exists():
        return False, [f"no aggregate publication index found at {index_path}"]
    index = read_publication_index(index_path)

    if len(index.records) != len(REQUIRED_ECOSYSTEM_TARGET_IDS):
        failures.append(
            f"aggregate index contains {len(index.records)} record(s), expected exactly "
            f"{len(REQUIRED_ECOSYSTEM_TARGET_IDS)}"
        )

    seen_targets = {r.target_id for r in index.records}
    if seen_targets != REQUIRED_ECOSYSTEM_TARGET_IDS:
        failures.append(
            f"aggregate index target ids {sorted(seen_targets)} != required "
            f"{sorted(REQUIRED_ECOSYSTEM_TARGET_IDS)}"
        )

    for target_id, run_dir in run_dirs.items():
        report = verify_certification_run_trusted(
            Path(run_dir), trust_store=trust_store, publication_index=index, require_published=True,
        )
        if not report["valid"]:
            failures.append(f"{target_id}: trusted verification against the aggregate set failed: {report['failures']}")

    return not failures, failures


__all__ = [
    "REQUIRED_ECOSYSTEM_TARGET_IDS",
    "AggregatePublicationError",
    "EcosystemRunOutcome",
    "build_five_ecosystem_publication_set",
    "verify_aggregate_publication_set",
]
