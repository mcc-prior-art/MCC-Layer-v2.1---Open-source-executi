#!/usr/bin/env python3
"""Deterministic release-artifact inspection and guards for ``mcc-core``.

Pure, testable Python (no ``unzip | grep`` chains) so the same logic runs in CI
and in ``tests/``. Nothing here publishes anything or needs credentials.

Provides:
  * ``inspect_wheel`` / ``inspect_sdist`` — open a built artifact and return facts.
  * ``validate_wheel`` / ``validate_sdist`` — enforce the content contract
    (returns a list of problems; empty == contract satisfied).
  * ``normalize_name`` — PEP 503 distribution-name normalization.
  * ``is_valid_pep440`` — PEP 440 version validity.
  * ``index_version_status`` — query PyPI/TestPyPI for a version (exists/absent).
  * ``confirm_release_inputs`` — validate the manual release target + version
    confirmation string.

CLI (used by CI):
    python -m scripts.release_checks inspect-wheel dist/mcc_core-*.whl --version 0.1.0
    python -m scripts.release_checks inspect-sdist dist/mcc_core-*.tar.gz --version 0.1.0
    python -m scripts.release_checks index-check --name mcc-core --version 0.1.0 --index pypi
"""

from __future__ import annotations

import argparse
import email.parser
import re
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from typing import Callable, Optional

DIST_NAME = "mcc-core"
PUBLIC_PACKAGE = "mcc"

INDEX_URLS = {
    "pypi": "https://pypi.org/pypi",
    "testpypi": "https://test.pypi.org/pypi",
}

# VCS internals, caches, virtualenvs and editor dirs — never valid in ANY
# artifact (wheel or sdist). Matched against path components (case-insensitive).
ALWAYS_FORBIDDEN_COMPONENTS = frozenset({
    ".git", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".idea", ".vscode", "node_modules",
})
# CI configuration — must not ship in the WHEEL. An sdist is a source tree, so
# `.github/` there is acceptable.
WHEEL_ONLY_FORBIDDEN_COMPONENTS = frozenset({".github"})

# Precise secret-file detection (a *file*, not a substring in a source name — so
# a test named ``test_egress_credentials.py`` is NOT flagged).
_SECRET_BASENAME = re.compile(
    r"^(secret|secrets|credential|credentials)\.(json|ya?ml|txt|ini|cfg|env|key|pem)$",
    re.IGNORECASE,
)


def _secret_reason(basename: str) -> Optional[str]:
    low = basename.lower()
    if low == ".env" or low.startswith(".env."):
        return "dotenv file"
    if low.endswith((".pem", ".key")):
        return "key/certificate material"
    if low in ("id_ed25519", "id_rsa"):
        return "private ssh key"
    if _SECRET_BASENAME.match(basename):
        return "secret/credential file"
    return None

_PEP440 = re.compile(
    r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*"
    r"((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?"
    r"(\+[a-z0-9]+(\.[a-z0-9]+)*)?$",
    re.IGNORECASE,
)


def normalize_name(name: str) -> str:
    """PEP 503 normalized distribution name (lowercase, runs of -_. -> single -)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def is_valid_pep440(version: str) -> bool:
    """True if ``version`` is a valid PEP 440 version. Prefer the packaging lib."""
    try:
        from packaging.version import Version  # type: ignore[import-not-found]

        Version(version)
        return True
    except ModuleNotFoundError:
        return bool(_PEP440.match(version.strip()))
    except Exception:
        return False


def _forbidden_reason(path: str, *, scope: str) -> Optional[str]:
    """Reason ``path`` is disallowed in an artifact of ``scope`` ('wheel'|'sdist')."""
    parts = [p for p in re.split(r"[\\/]", path) if p]
    forbidden = ALWAYS_FORBIDDEN_COMPONENTS
    if scope == "wheel":
        forbidden = forbidden | WHEEL_ONLY_FORBIDDEN_COMPONENTS
    for p in parts:
        if p.lower() in forbidden:
            return f"forbidden path component {p!r}"
    if parts:
        secret = _secret_reason(parts[-1])
        if secret:
            return secret
    return None


def _parse_metadata(text: str) -> dict:
    msg = email.parser.Parser().parsestr(text)
    return {
        "name": msg.get("Name", ""),
        "version": msg.get("Version", ""),
        "requires_dist": [v.strip() for v in msg.get_all("Requires-Dist", [])],
    }


@dataclass
class WheelInfo:
    path: str
    names: list = field(default_factory=list)
    top_level: set = field(default_factory=set)
    metadata: dict = field(default_factory=dict)
    has_py_typed: bool = False
    filename_version: str = ""


def wheel_filename_version(path: str) -> str:
    # mcc_core-0.1.0-py3-none-any.whl -> 0.1.0
    base = path.rsplit("/", 1)[-1]
    m = re.match(r"[A-Za-z0-9_.]+?-([^-]+)-", base)
    return m.group(1) if m else ""


def sdist_filename_version(path: str) -> str:
    # mcc_core-0.1.0.tar.gz -> 0.1.0
    base = path.rsplit("/", 1)[-1]
    m = re.match(r"[A-Za-z0-9_.]+?-(.+)\.tar\.gz$", base)
    return m.group(1) if m else ""


def inspect_wheel(path: str) -> WheelInfo:
    info = WheelInfo(path=path, filename_version=wheel_filename_version(path))
    with zipfile.ZipFile(path) as z:
        info.names = z.namelist()
        for n in info.names:
            top = n.split("/", 1)[0]
            if top.endswith(".dist-info") or top.endswith(".data"):
                continue
            info.top_level.add(top)
            if n == f"{PUBLIC_PACKAGE}/py.typed":
                info.has_py_typed = True
        meta_name = next((n for n in info.names if n.endswith(".dist-info/METADATA")), None)
        if meta_name:
            info.metadata = _parse_metadata(z.read(meta_name).decode("utf-8"))
    return info


@dataclass
class SdistInfo:
    path: str
    names: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    filename_version: str = ""


def inspect_sdist(path: str) -> SdistInfo:
    info = SdistInfo(path=path, filename_version=sdist_filename_version(path))
    with tarfile.open(path, "r:gz") as t:
        members = t.getmembers()
        info.names = [m.name for m in members]
        pkg_info = next((m for m in members if m.name.endswith("/PKG-INFO")), None)
        if pkg_info is not None:
            f = t.extractfile(pkg_info)
            if f is not None:
                info.metadata = _parse_metadata(f.read().decode("utf-8"))
    return info


def _requires_mcc_client(requires_dist: list) -> bool:
    return any(normalize_name(r.split()[0].split(";")[0].split("(")[0].split(">")[0]
                                .split("<")[0].split("=")[0].split("!")[0].split("~")[0].strip())
               == "mcc-client"
               for r in requires_dist)


def validate_wheel(path: str, *, expected_version: str, expect_py_typed: bool = True) -> list:
    """Return a list of contract violations for the wheel (empty == OK)."""
    problems: list = []
    info = inspect_wheel(path)

    if info.top_level != {PUBLIC_PACKAGE}:
        problems.append(f"wheel top-level packages must be exactly {{{PUBLIC_PACKAGE!r}}}, "
                        f"got {sorted(info.top_level)}")
    if "mcc_client" in info.top_level:
        problems.append("wheel vendors mcc_client (must depend on it, not ship it)")
    if expect_py_typed and not info.has_py_typed:
        problems.append("wheel is missing mcc/py.typed but claims typed support")

    for required in (".dist-info/METADATA", ".dist-info/WHEEL", ".dist-info/RECORD"):
        if not any(n.endswith(required) for n in info.names):
            problems.append(f"wheel missing {required}")

    for n in info.names:
        reason = _forbidden_reason(n, scope="wheel")
        if reason:
            problems.append(f"wheel ships disallowed entry {n!r}: {reason}")
        if n.split("/", 1)[0] in ("tests", "test"):
            problems.append(f"wheel ships tests entry {n!r} (packaging policy: no tests in wheel)")

    meta = info.metadata
    if normalize_name(meta.get("name", "")) != normalize_name(DIST_NAME):
        problems.append(f"wheel metadata name normalizes to {normalize_name(meta.get('name',''))!r}, "
                        f"expected {normalize_name(DIST_NAME)!r}")
    if meta.get("version", "") != expected_version:
        problems.append(f"wheel metadata version {meta.get('version','')!r} != expected {expected_version!r}")
    if info.filename_version != expected_version:
        problems.append(f"wheel filename version {info.filename_version!r} != expected {expected_version!r}")
    if not _requires_mcc_client(meta.get("requires_dist", [])):
        problems.append("wheel metadata does not declare the mcc-client runtime dependency")
    return problems


def validate_sdist(path: str, *, expected_version: str) -> list:
    """Return a list of contract violations for the sdist (empty == OK).

    The sdist may legitimately include source + tests; it must not include VCS
    internals, caches, virtualenvs, secrets, or nested build output.
    """
    problems: list = []
    info = inspect_sdist(path)
    for n in info.names:
        reason = _forbidden_reason(n, scope="sdist")
        if reason:
            problems.append(f"sdist ships disallowed entry {n!r}: {reason}")
        # Nested build output (dist/ or build/ inside the sdist) must not appear.
        parts = [p for p in re.split(r"[\\/]", n) if p]
        if len(parts) > 1 and parts[1] in ("dist", "build"):
            problems.append(f"sdist contains nested build output {n!r}")
    if info.filename_version != expected_version:
        problems.append(f"sdist filename version {info.filename_version!r} != expected {expected_version!r}")
    if info.metadata and info.metadata.get("version", "") != expected_version:
        problems.append(f"sdist PKG-INFO version {info.metadata.get('version','')!r} != {expected_version!r}")
    return problems


def index_version_status(
    name: str,
    version: str,
    *,
    index: str,
    opener: Callable[[str], object] = urllib.request.urlopen,
) -> str:
    """Return "exists" or "absent" for ``name==version`` on the selected index.

    A version-specific 200 means the version is present (including yanked — it may
    not be reused). 404 means it is absent. The project not existing at all also
    surfaces as 404 -> "absent". Other HTTP/network errors raise.
    """
    if index not in INDEX_URLS:
        raise ValueError(f"unknown index {index!r}; expected one of {sorted(INDEX_URLS)}")
    url = f"{INDEX_URLS[index]}/{normalize_name(name)}/{version}/json"
    try:
        resp = opener(url)  # type: ignore[call-arg]
        status = getattr(resp, "status", None) or resp.getcode()  # type: ignore[attr-defined]
        close = getattr(resp, "close", None)
        if close:
            close()
        return "exists" if int(status) == 200 else "absent"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "absent"
        raise


def confirm_release_inputs(target: str, version_confirmation: str, artifact_version: str) -> None:
    """Validate the manual-release inputs; raise ValueError on any mismatch."""
    if target not in ("testpypi", "pypi"):
        raise ValueError(f"target must be 'testpypi' or 'pypi', got {target!r}")
    if not is_valid_pep440(artifact_version):
        raise ValueError(f"artifact version {artifact_version!r} is not valid PEP 440")
    if version_confirmation.strip() != artifact_version:
        raise ValueError(
            f"version confirmation {version_confirmation!r} does not match the built "
            f"artifact version {artifact_version!r}; bump/retype and retry"
        )


def _cli(argv: Optional[list] = None) -> int:
    p = argparse.ArgumentParser(description="mcc-core release artifact checks")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("inspect-wheel")
    w.add_argument("path")
    w.add_argument("--version", required=True)
    s = sub.add_parser("inspect-sdist")
    s.add_argument("path")
    s.add_argument("--version", required=True)
    ic = sub.add_parser("index-check")
    ic.add_argument("--name", default=DIST_NAME)
    ic.add_argument("--version", required=True)
    ic.add_argument("--index", required=True, choices=sorted(INDEX_URLS))
    args = p.parse_args(argv)

    if args.cmd == "inspect-wheel":
        problems = validate_wheel(args.path, expected_version=args.version)
        _report(f"wheel {args.path}", problems, inspect_wheel(args.path))
        return 1 if problems else 0
    if args.cmd == "inspect-sdist":
        problems = validate_sdist(args.path, expected_version=args.version)
        _report(f"sdist {args.path}", problems, inspect_sdist(args.path))
        return 1 if problems else 0
    if args.cmd == "index-check":
        status = index_version_status(args.name, args.version, index=args.index)
        print(f"{normalize_name(args.name)}=={args.version} on {args.index}: {status}")
        if status == "exists":
            print("ERROR: version already published (immutable). Bump the version in "
                  "mcc/_version.py and rebuild.", file=sys.stderr)
            return 1
        return 0
    return 2


def _report(label: str, problems: list, info: object) -> None:
    print(f"== {label} ==")
    for k in ("filename_version", "top_level", "has_py_typed", "metadata"):
        if hasattr(info, k):
            print(f"  {k}: {getattr(info, k)}")
    if problems:
        print("  CONTRACT VIOLATIONS:")
        for pr in problems:
            print(f"   - {pr}")
    else:
        print("  contract: OK")


if __name__ == "__main__":
    raise SystemExit(_cli())
