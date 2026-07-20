"""Release guards: duplicate-version index check, input confirmation, and
artifact-contract validators failing closed on malformed input (PR #41).

No network: the index check is exercised with injected 200/404/HTTPError openers.
No publishing, no credentials.
"""

from __future__ import annotations

import io
import urllib.error
import zipfile

import pytest

from scripts.release_checks import (
    confirm_release_inputs,
    index_version_status,
    is_valid_pep440,
    normalize_name,
    validate_sdist,
    validate_wheel,
)


# ---- name / version primitives ------------------------------------------- #

def test_normalize_name_pep503():
    assert normalize_name("mcc-core") == "mcc-core"
    assert normalize_name("mcc_core") == "mcc-core"
    assert normalize_name("MCC.Core") == "mcc-core"


@pytest.mark.parametrize("v", ["0.1.0", "1.2.3", "1.0.0a1", "2.0.0rc1", "1.0.0.post1", "1.0.0.dev3"])
def test_pep440_valid(v):
    assert is_valid_pep440(v)


@pytest.mark.parametrize("v", ["not-a-version", "1.0.0.0.0.x", "", "1..0", "abc", "1 2 3"])
def test_pep440_invalid(v):
    # Note: packaging.version.Version is lenient (accepts "1", "v1.0", "01.2"),
    # so only genuinely malformed strings are asserted invalid here.
    assert not is_valid_pep440(v)


# ---- duplicate-version / immutability guard ------------------------------ #

class _Resp:
    def __init__(self, status): self.status = status
    def getcode(self): return self.status
    def close(self): pass


def _opener_status(status):
    return lambda url: _Resp(status)


def _opener_http_error(code):
    def _o(url):
        raise urllib.error.HTTPError(url, code, "err", hdrs=None, fp=None)
    return _o


def test_index_check_200_means_exists():
    assert index_version_status("mcc-core", "0.1.0", index="pypi",
                                opener=_opener_status(200)) == "exists"


def test_index_check_404_means_absent():
    # A version-specific 404 (or the project not existing yet) => absent.
    assert index_version_status("mcc-core", "9.9.9", index="testpypi",
                                opener=_opener_http_error(404)) == "absent"


def test_index_check_distinguishes_indexes():
    seen = {}

    def opener(url):
        seen["url"] = url
        return _Resp(404)

    index_version_status("mcc-core", "0.1.0", index="testpypi", opener=opener)
    assert "test.pypi.org" in seen["url"]
    index_version_status("mcc-core", "0.1.0", index="pypi", opener=opener)
    assert seen["url"].startswith("https://pypi.org/")


def test_index_check_other_http_error_propagates():
    # A 500 is not "absent"; it must not be swallowed into a false success.
    with pytest.raises(urllib.error.HTTPError):
        index_version_status("mcc-core", "0.1.0", index="pypi", opener=_opener_http_error(500))


def test_index_check_unknown_index_rejected():
    with pytest.raises(ValueError):
        index_version_status("mcc-core", "0.1.0", index="nexus", opener=_opener_status(404))


# ---- manual release input confirmation ----------------------------------- #

def test_confirm_inputs_ok():
    confirm_release_inputs("pypi", "0.1.0", "0.1.0")  # no raise


def test_confirm_inputs_mismatched_version_fails():
    with pytest.raises(ValueError):
        confirm_release_inputs("pypi", "0.1.1", "0.1.0")


def test_confirm_inputs_bad_target_fails():
    with pytest.raises(ValueError):
        confirm_release_inputs("nexus", "0.1.0", "0.1.0")


def test_confirm_inputs_bad_version_fails():
    with pytest.raises(ValueError):
        confirm_release_inputs("testpypi", "banana", "banana")


# ---- validators fail closed on malformed artifacts ----------------------- #

def _make_wheel(tmp_path, names, metadata):
    p = tmp_path / "mcc_core-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(p, "w") as z:
        for n in names:
            z.writestr(n, b"")
        z.writestr("mcc_core-0.1.0.dist-info/METADATA", metadata)
        z.writestr("mcc_core-0.1.0.dist-info/WHEEL", "Wheel-Version: 1.0\n")
        z.writestr("mcc_core-0.1.0.dist-info/RECORD", "")
    return str(p)


_GOOD_META = "Metadata-Version: 2.1\nName: mcc-core\nVersion: 0.1.0\nRequires-Dist: mcc-client<0.2,>=0.1\n"


def test_wheel_validator_accepts_good_wheel(tmp_path):
    whl = _make_wheel(tmp_path, ["mcc/__init__.py", "mcc/py.typed"], _GOOD_META)
    assert validate_wheel(whl, expected_version="0.1.0") == []


def test_wheel_validator_flags_vendored_mcc_client(tmp_path):
    whl = _make_wheel(tmp_path, ["mcc/__init__.py", "mcc/py.typed",
                                 "mcc_client/__init__.py"], _GOOD_META)
    problems = validate_wheel(whl, expected_version="0.1.0")
    assert any("mcc_client" in p for p in problems)


def test_wheel_validator_flags_missing_py_typed(tmp_path):
    whl = _make_wheel(tmp_path, ["mcc/__init__.py"], _GOOD_META)
    assert any("py.typed" in p for p in validate_wheel(whl, expected_version="0.1.0"))


def test_wheel_validator_flags_shipped_tests_and_secrets(tmp_path):
    whl = _make_wheel(tmp_path, ["mcc/__init__.py", "mcc/py.typed",
                                 "tests/test_x.py", ".env", "credentials.json"], _GOOD_META)
    problems = validate_wheel(whl, expected_version="0.1.0")
    assert any("tests" in p for p in problems)
    assert any(".env" in p or "dotenv" in p for p in problems)
    assert any("credential" in p.lower() for p in problems)


def test_wheel_validator_flags_version_mismatch(tmp_path):
    whl = _make_wheel(tmp_path, ["mcc/__init__.py", "mcc/py.typed"], _GOOD_META)
    assert any("version" in p for p in validate_wheel(whl, expected_version="9.9.9"))


def test_wheel_validator_flags_missing_dependency(tmp_path):
    meta = "Metadata-Version: 2.1\nName: mcc-core\nVersion: 0.1.0\n"  # no Requires-Dist
    whl = _make_wheel(tmp_path, ["mcc/__init__.py", "mcc/py.typed"], meta)
    assert any("mcc-client" in p for p in validate_wheel(whl, expected_version="0.1.0"))


def test_sdist_validator_allows_tests_but_flags_caches(tmp_path):
    import tarfile
    p = tmp_path / "mcc_core-0.1.0.tar.gz"
    with tarfile.open(p, "w:gz") as t:
        for name in ["mcc_core-0.1.0/mcc/__init__.py",
                     "mcc_core-0.1.0/tests/test_egress_credentials.py",  # legit test — NOT a secret
                     "mcc_core-0.1.0/PKG-INFO"]:
            data = b"Metadata-Version: 2.1\nName: mcc-core\nVersion: 0.1.0\n" if name.endswith("PKG-INFO") else b""
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
    assert validate_sdist(str(p), expected_version="0.1.0") == []

    # A cache dir inside the sdist must be rejected.
    p2 = tmp_path / "mcc_core-0.1.0.tar.gz"  # rebuild with a cache entry
    with tarfile.open(p2, "w:gz") as t:
        for name in ["mcc_core-0.1.0/mcc/__pycache__/x.pyc", "mcc_core-0.1.0/PKG-INFO"]:
            data = b"Name: mcc-core\nVersion: 0.1.0\n" if name.endswith("PKG-INFO") else b""
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
    assert any("__pycache__" in pr for pr in validate_sdist(str(p2), expected_version="0.1.0"))
