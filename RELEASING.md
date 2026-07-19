# Releasing `mcc-core`

Operational runbook for building, validating, and publishing the **`mcc-core`**
Python distribution (the stable public `mcc` facade over the supported
`mcc-client` SDK). Publishing uses **GitHub OIDC Trusted Publishing** — there are
**no long-lived PyPI tokens**.

Governance is unaffected by releases: `mcc` remains a thin facade; the model
proposes, MCC decides, the gate enforces, the audit chain records.

- Build/validate CI (no publish): `.github/workflows/packaging.yml`
- Manual publish: `.github/workflows/release.yml`
- Artifact/version/guard logic: `scripts/release_checks.py`
- Version single source: `mcc/_version.py`

---

## A. Prerequisites (one-time, repository owner)

You need **maintainer/admin** on `mcc-prior-art/mcc-layer` and control of the
PyPI/TestPyPI projects.

### A.1 GitHub Environments

Create two environments (Settings → Environments):

| Environment | Purpose | Required reviewers |
|-------------|---------|--------------------|
| `testpypi`  | Publish to TestPyPI | optional |
| `pypi`      | Publish to production PyPI | **required** (add yourself / release approvers) |

> **Declaring `environment: pypi` does NOT by itself create a manual approval
> gate.** Production publishing is only protected once you add **required
> reviewers** to the `pypi` environment. Do this before the first production
> release.

### A.2 PyPI Trusted Publisher (production)

On <https://pypi.org> → the `mcc-core` project (or "pending publisher" if it does
not exist yet) → *Publishing* → add a GitHub Actions trusted publisher with
**exactly**:

| Field | Value |
|-------|-------|
| Owner | `mcc-prior-art` |
| Repository | `mcc-layer` |
| Workflow filename | `release.yml` |
| Environment | `pypi` |

### A.3 TestPyPI Trusted Publisher

Repeat on <https://test.pypi.org> with the same owner/repo/workflow and
Environment `testpypi`.

### A.4 No API tokens

Do **not** create or store any PyPI username/password/API token in GitHub
secrets. Trusted Publishing exchanges a short-lived GitHub OIDC token at publish
time. If you find a stored `PYPI_*` token, it is unnecessary and should be
removed.

---

## B. Version bump

The version has **one authoritative source**: `mcc/_version.py` (`__version__`).
The wheel/sdist metadata is generated from that attribute (setuptools dynamic
version), so `mcc.__version__ == importlib.metadata.version("mcc-core")`.

- Edit **only** `mcc/_version.py`. Do not add a version string anywhere else.
- Policy (semantic-ish, PEP 440):
  - **PATCH** (`0.1.0 → 0.1.1`): fixes, docs, packaging, no API change.
  - **MINOR** (`0.1.0 → 0.2.0`): additive public API (new re-exports).
  - **MAJOR** (`0.x → 1.0`): removal/rename/behavioral change of the public API.
  - **Prerelease** identifiers (`0.2.0rc1`, `0.2.0a1`) are valid PEP 440 and may
    be released to TestPyPI (and PyPI) for previews.
- **Published versions are immutable and can never be reused** — not even after a
  yank. A mistake means a new (higher) version.

`client_version` tracks the underlying `mcc-client` package and is bumped in that
distribution, separately from `mcc-core`.

---

## C. Local preflight

Run before any release (all offline, no publishing):

```bash
pip install -e ./sdk/python -e ".[dev,release]"

ruff check mcc/ scripts/ tests/
mypy mcc/
pytest tests/test_mcc_facade.py tests/test_version_contract.py \
       tests/test_release_guard.py tests/test_artifact_contract.py -q

rm -rf dist && python -m build --outdir dist
twine check --strict dist/*
python -m scripts.release_checks inspect-wheel dist/mcc_core-*.whl --version <VERSION>
python -m scripts.release_checks inspect-sdist dist/mcc_core-*.tar.gz --version <VERSION>
```

Genuine clean install outside the checkout (proves the wheel is self-contained):

```bash
python -m venv /tmp/relcheck
/tmp/relcheck/bin/pip install dist/mcc_core-*.whl ./sdk/python
cd /tmp && /tmp/relcheck/bin/python -c \
  "import mcc, mcc_client, importlib.metadata as im; \
   from mcc import MCCClient; from mcc_client import MCCClient as O; \
   assert MCCClient is O; assert mcc.__version__ == im.version('mcc-core'); \
   print('clean install OK', mcc.__version__)"
```

---

## D. TestPyPI release

1. GitHub → **Actions** → **Release (manual, Trusted Publishing)** → **Run workflow**.
2. Inputs:
   - `target`: `testpypi`
   - `version_confirmation`: the exact version (e.g. `0.1.0`) — must match the
     built artifact or the run fails fast.
   - `dry_run`: `false` (use `true` to validate/guard without publishing).
3. The `build` job builds, `twine check --strict`s, enforces the content
   contract, and runs the **duplicate-version guard** against TestPyPI. The
   `publish-testpypi` job publishes the exact built artifact via OIDC.
4. Verify:

   ```bash
   python -m venv /tmp/tp && /tmp/tp/bin/pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     "mcc-core==<VERSION>"
   /tmp/tp/bin/python -c "import mcc; print(mcc.__version__)"
   ```

> **Dependency-confusion note:** `mcc-core` depends on `mcc-client`. TestPyPI does
> not mirror PyPI, so installing from TestPyPI needs `mcc-client` reachable via an
> `--extra-index-url` (PyPI, once `mcc-client` is published there). Mixing indexes
> has dependency-confusion implications — only add extra indexes you trust, and
> prefer verifying against production PyPI once both packages are published there.

---

## E. Production release

1. Ensure `main` is at the commit you intend to release and preflight (§C) is green.
2. GitHub → **Actions** → **Release (manual, Trusted Publishing)** → **Run workflow**,
   with the workflow ref set to the default branch (`main`).
3. Inputs: `target` = `pypi`; `version_confirmation` = exact version; `dry_run` = `false`.
4. The `build` job validates + runs the duplicate guard against **production**
   PyPI. The `publish-pypi` job additionally:
   - refuses to run unless the workflow ref is the repository's default branch;
   - waits on the protected **`pypi` environment approval** (if reviewers are
     configured per §A.1).
5. Approve the environment when prompted.
6. Verify in a fresh environment:

   ```bash
   python -m venv /tmp/pp && /tmp/pp/bin/pip install "mcc-core==<VERSION>"
   /tmp/pp/bin/python -c \
     "import mcc, mcc_client, importlib.metadata as im; \
      from mcc import MCCClient; from mcc_client import MCCClient as O; \
      assert MCCClient is O; assert mcc.__version__ == im.version('mcc-core'); \
      print('published OK', mcc.__version__, '| client', mcc.client_version)"
   ```

---

## F. Emergency response (defective release)

Python package files and versions on PyPI are **immutable** — you cannot
overwrite or edit a published file, and there is **no `twine --yank` command**.

1. **Yank** the bad version via the PyPI web UI: the `mcc-core` project →
   *Manage* → *Releases* → the version → *Options* → **Yank**. Record a clear
   reason (yanking hides it from normal resolution but keeps pinned installs
   working).
2. **Bump PATCH** in `mcc/_version.py` and publish a corrected version (§E).
3. **Never reuse** the yanked version number.
4. Do **not** delete a release except for genuine security/legal necessity —
   deletion breaks existing pins and the number still cannot be reused.

---

## G. Failed release recovery

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `build` job fails at build | source/packaging error | fix, re-run; nothing was published |
| `version confirmation … does not match` | typo in the input | re-run with the exact built version |
| Duplicate-version guard fails (`exists`) | version already on the index (incl. yanked) | bump `mcc/_version.py`, rebuild |
| OIDC error at publish | Trusted Publisher / environment mismatch | verify §A.2–A.3 fields match owner/repo/`release.yml`/environment exactly |
| `environment protection rules` block | `pypi` reviewers not approved | approve the environment, or configure reviewers (§A.1) |
| Upload failed after a partial publish | network/index issue mid-upload | investigate the index; an immutable version that partially published usually requires a **new** version |

Distinguish **build failure** (safe to re-run), **OIDC/environment mismatch**
(fix config, re-run), **duplicate version** (bump), and **upload failure**
(investigate; may need a new version). A version that reached the index is
immutable — recovery is a new version, never an overwrite.
