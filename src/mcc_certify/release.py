"""Official Certification Release packaging (PR #70).

Builds the deterministic, immutable release tree for one official
certification release, from five already-officially-certified run
directories (each produced by an independent ``mcc certify <target>
--issuer-config ...`` invocation -- see ``mcc_certify.aggregate`` for why
they cannot be produced in one process). This module introduces **no**
alternative Evidence Bundle, Certification Manifest, Technical Certificate,
or offline-verification format -- every existing run directory is copied
into the release tree byte-for-byte, complete and unmodified. The only new
artifacts this module adds are release *metadata*: ``release-index.json``
(binding release version, source commit, issuer identity, and every
ecosystem's certificate/status), ``checksums.sha256`` (a standard checksum
manifest over the entire release tree), ``verification-summary.json``, and
a human-readable ``README.md``.

All-or-nothing, exactly like :mod:`mcc_certify.aggregate`: this reuses
:func:`mcc_certify.aggregate.build_five_ecosystem_publication_set`
unchanged for the aggregate Publication Index, and additionally requires
every ecosystem to pass :func:`mcc_certify.official.evaluate_official_eligibility`
(the one centralized OFFICIAL-status gate) before anything is written.
Building is atomic: artifacts are staged in a temporary directory and only
renamed into place after every check passes -- a failed release build
leaves no partial release tree.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mcc_core.signing import canonical_bytes

from .aggregate import (
    REQUIRED_ECOSYSTEM_TARGET_IDS,
    AggregatePublicationError,
    build_five_ecosystem_publication_set,
)
from .official import PRODUCTION_ISSUER_ID, OfficialEligibility, evaluate_official_eligibility
from .pipeline import CP001_SPECIFICATION_VERSION, TOOL_NAME, TOOL_VERSION
from .target import CertifyError
from .trust_store import TrustStore

RELEASE_INDEX_FILE = "release-index.json"
CHECKSUMS_FILE = "checksums.sha256"
VERIFICATION_SUMMARY_FILE = "verification-summary.json"
README_FILE = "README.md"

RELEASE_SCHEMA_VERSION = "mcc-official-release/1"


class OfficialReleaseError(CertifyError):
    """The official release could not be built. All-or-nothing: raised for
    any ineligible/missing/unverifiable ecosystem, or an internal
    inconsistency. No release directory is ever partially written."""


@dataclass(frozen=True)
class OfficialReleaseResult:
    release_dir: Path
    release_version: str
    dry_run: bool
    eligibilities: Tuple[OfficialEligibility, ...]

    def to_dict(self) -> dict:
        return {
            "release_dir": str(self.release_dir),
            "release_version": self.release_version,
            "dry_run": self.dry_run,
            "eligibilities": [e.to_dict() for e in self.eligibilities],
        }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_checksums(release_root: Path, dest: Path) -> None:
    lines = []
    for path in sorted(release_root.rglob("*")):
        if path.is_file() and path != dest:
            digest = _sha256_file(path)
            rel = path.relative_to(release_root)
            lines.append(f"{digest}  {rel.as_posix()}\n")
    dest.write_text("".join(lines), encoding="utf-8")


def verify_release_checksums(release_dir: Path | str) -> Tuple[bool, List[str]]:
    """Independently re-verify ``checksums.sha256`` against the actual
    bytes of every file in an already-built release tree. Never mutates
    anything. Returns ``(valid, failures)`` -- a missing checksums file, a
    missing referenced file, or any digest mismatch is a failure, never an
    exception a caller must remember to catch."""
    release_dir = Path(release_dir)
    checksums_path = release_dir / CHECKSUMS_FILE
    if not checksums_path.exists():
        return False, [f"{CHECKSUMS_FILE} not found in {release_dir}"]

    failures: List[str] = []
    declared: Dict[str, str] = {}
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, rel_path = line.partition("  ")
        declared[rel_path] = digest

    for rel_path, expected_digest in declared.items():
        path = release_dir / rel_path
        if not path.exists():
            failures.append(f"{rel_path}: file referenced in {CHECKSUMS_FILE} is missing")
            continue
        actual_digest = _sha256_file(path)
        if actual_digest != expected_digest:
            failures.append(f"{rel_path}: checksum mismatch (expected {expected_digest}, got {actual_digest})")

    # Every file actually present (other than the checksums file itself)
    # must also be declared -- an added/undeclared file is equally suspicious.
    for path in sorted(release_dir.rglob("*")):
        if path.is_file() and path != checksums_path:
            rel = path.relative_to(release_dir).as_posix()
            if rel not in declared:
                failures.append(f"{rel}: present in release tree but not declared in {CHECKSUMS_FILE}")

    return not failures, failures


def _readme_text(
    *, release_version: str, release_tag: str, source_commit_sha: str, ceremony_timestamp: str,
    production_issuer_id: str, dry_run: bool, eligibilities: Tuple[OfficialEligibility, ...],
) -> str:
    status_line = "DRY RUN -- NOT AN OFFICIAL RELEASE" if dry_run else "OFFICIAL CERTIFICATION RELEASE"
    lines = [
        f"# MCC Official Certification Release {release_version}",
        "",
        f"**Status: {status_line}**",
        "",
        f"- release_tag: `{release_tag}`",
        f"- source_commit_sha: `{source_commit_sha}`",
        f"- ceremony_timestamp: `{ceremony_timestamp}`",
        f"- production_issuer_id: `{production_issuer_id}`",
        f"- certification_pipeline: `{TOOL_NAME} {TOOL_VERSION}`",
        f"- specification_version: `{CP001_SPECIFICATION_VERSION}`",
        "",
        "All five ecosystems below were certified through one identical MCC "
        "Certification Suite -- the same pipeline, Evidence Bundle format, "
        "Certification Manifest format, Technical Certificate model, and "
        "offline verifier for every ecosystem. No ecosystem has "
        "adapter-specific certification authority.",
        "",
        "| target_id | certificate_id | eligible |",
        "|---|---|---|",
    ]
    for e in eligibilities:
        lines.append(f"| `{e.target_id}` | `{e.certificate_id}` | {e.eligible} |")
    lines += [
        "",
        "## Reproduce offline verification",
        "",
        "```bash",
        "python -m mcc_certify verify-aggregate \\",
        "  --trust-store official-trust-store.json \\",
        "  --publication-dir . \\",
        *[f"  --run {e.target_id}={e.target_id} \\" for e in eligibilities],
        "```",
        "",
        "See `release-index.json` for the full machine-readable binding and "
        "`checksums.sha256` to verify every file in this release.",
    ]
    return "\n".join(lines) + "\n"


def build_official_release(
    run_dirs: Dict[str, Path],
    *,
    trust_store: TrustStore,
    release_version: str,
    release_tag: str,
    source_commit_sha: str,
    ceremony_timestamp: str,
    output_dir: Path,
    production_issuer_id: str = PRODUCTION_ISSUER_ID,
    dry_run: bool = False,
) -> OfficialReleaseResult:
    """All-or-nothing: build one official release tree at
    ``<output_dir>/<release_version>/``. Raises :class:`OfficialReleaseError`
    (writing nothing) unless every one of the five required ecosystems is
    eligible for OFFICIAL status (see ``mcc_certify.official``) AND the
    aggregate Publication Set builds and verifies successfully."""
    provided_ids = set(run_dirs)
    missing = REQUIRED_ECOSYSTEM_TARGET_IDS - provided_ids
    unexpected = provided_ids - REQUIRED_ECOSYSTEM_TARGET_IDS
    if missing or unexpected:
        raise OfficialReleaseError(
            f"official release requires exactly {sorted(REQUIRED_ECOSYSTEM_TARGET_IDS)}; "
            f"missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )

    eligibilities: List[OfficialEligibility] = []
    for target_id in sorted(run_dirs):
        run_dir = Path(run_dirs[target_id])
        try:
            eligibility = evaluate_official_eligibility(
                run_dir, trust_store=trust_store, production_issuer_id=production_issuer_id,
                expected_source_commit_sha=source_commit_sha,
            )
        except CertifyError as e:
            eligibility = OfficialEligibility(
                target_id=target_id, certificate_id=None, eligible=False, reasons=(str(e),),
            )
        eligibilities.append(eligibility)

    if not all(e.eligible for e in eligibilities):
        raise OfficialReleaseError(
            f"not every ecosystem is eligible for OFFICIAL status: {[e.to_dict() for e in eligibilities]}"
        )

    output_dir = Path(output_dir)
    final_release_dir = output_dir / release_version
    if final_release_dir.exists():
        raise OfficialReleaseError(f"release directory already exists: {final_release_dir} (releases are immutable)")

    with tempfile.TemporaryDirectory(dir=str(output_dir) if output_dir.exists() else None) as tmp:
        tmp_release_dir = Path(tmp) / release_version
        tmp_release_dir.mkdir(parents=True)

        for target_id in sorted(run_dirs):
            shutil.copytree(Path(run_dirs[target_id]), tmp_release_dir / target_id)

        try:
            _, aggregate_outcomes = build_five_ecosystem_publication_set(
                run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_release_dir,
            )
        except AggregatePublicationError as e:
            raise OfficialReleaseError(f"aggregate publication set build failed: {e}") from e

        release_index = {
            "release_schema_version": RELEASE_SCHEMA_VERSION,
            "release_version": release_version,
            "release_tag": release_tag,
            "source_commit_sha": source_commit_sha,
            "ceremony_timestamp": ceremony_timestamp,
            "specification_version": CP001_SPECIFICATION_VERSION,
            "certification_pipeline": f"{TOOL_NAME} {TOOL_VERSION}",
            "production_issuer_id": production_issuer_id,
            "dry_run": dry_run,
            "status": "DRY_RUN" if dry_run else "OFFICIAL",
            "ecosystems": [
                {
                    "target_id": e.target_id,
                    "certificate_id": e.certificate_id,
                    "eligible": e.eligible,
                }
                for e in eligibilities
            ],
            "aggregate_outcomes": [o.to_dict() for o in aggregate_outcomes],
        }
        (tmp_release_dir / RELEASE_INDEX_FILE).write_bytes(canonical_bytes(release_index))

        verification_summary = {
            "release_version": release_version,
            "dry_run": dry_run,
            "eligibilities": [e.to_dict() for e in eligibilities],
            "all_eligible": all(e.eligible for e in eligibilities),
        }
        (tmp_release_dir / VERIFICATION_SUMMARY_FILE).write_bytes(canonical_bytes(verification_summary))

        (tmp_release_dir / README_FILE).write_text(
            _readme_text(
                release_version=release_version, release_tag=release_tag, source_commit_sha=source_commit_sha,
                ceremony_timestamp=ceremony_timestamp, production_issuer_id=production_issuer_id,
                dry_run=dry_run, eligibilities=tuple(eligibilities),
            ),
            encoding="utf-8",
        )

        _write_checksums(tmp_release_dir, tmp_release_dir / CHECKSUMS_FILE)

        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_release_dir), str(final_release_dir))

    return OfficialReleaseResult(
        release_dir=final_release_dir, release_version=release_version, dry_run=dry_run,
        eligibilities=tuple(eligibilities),
    )


__all__ = [
    "RELEASE_SCHEMA_VERSION",
    "RELEASE_INDEX_FILE",
    "CHECKSUMS_FILE",
    "VERIFICATION_SUMMARY_FILE",
    "README_FILE",
    "OfficialReleaseError",
    "OfficialReleaseResult",
    "build_official_release",
    "verify_release_checksums",
]
