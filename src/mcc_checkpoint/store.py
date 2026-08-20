"""External anchor stores -- where signed checkpoints are durably recorded
outside the storage that holds the audit log itself.

Option A only (per task spec): a protected git branch on a git remote.
Recommended target: **a SEPARATE repository**,
``mcc-prior-art/mcc-audit-anchors`` -- not an orphan branch inside
``mcc-layer`` -- so the anchor store sits outside ``mcc-layer``'s own
storage/write-access trust boundary. This module never hardcodes that
repository; it takes ``remote_url``/``branch``/``workdir`` as explicit
configuration, so it works against any git remote (including a local
bare repository, as the test suite uses for Layer A validation). See
``docs/AUDIT_CHECKPOINT_ANCHORING.md`` for the manual repository-creation
and branch-protection steps required to bring the recommended remote
online, and for which of that document's properties are proven Layer A
(local, automated) versus Layer B (real GitHub infrastructure, PENDING
EXTERNAL-ANCHOR CONFIGURATION until performed).

Git's own commit history is an "externally persisted append-only
checkpoint history under separately configured repository protection" --
NOT an independently trusted timestamp authority (RFC 3161 or similar).
As long as the branch enforces linear history and rejects force-pushes
(server-side branch protection -- this module never assumes that, it only
ever performs fast-forward pushes and never passes ``--force``), a
full-storage rewrite of the audit log cannot also silently rewrite what
was already anchored: the rewrite is detectable, not prevented.

Option B (RFC 3161 TSA / public blockchain anchor -- a genuinely
independent timestamp authority) is explicitly deferred -- see
``docs/AUDIT_CHECKPOINT_ANCHORING.md`` roadmap section. Nothing here
implements it.

``InMemoryAnchorStore`` exists for tests and local development only --
mirrors the ``InMemory*`` / ``Redis*`` dual-backend convention already
used throughout ``src/mcc_core`` (``nonce.py``, ``idempotency.py``,
``mandate.py``): process-local, not durable, not shared across instances,
never silently substituted for the durable backend by
``anchor_store_from_env`` (selecting ``git`` without a usable remote/branch
raises ``AnchorStoreError`` instead of quietly falling back).
"""

from __future__ import annotations

import json
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from .errors import AnchorStoreError

#: Documentation only -- the recommended production remote (a SEPARATE
#: repository from ``mcc-layer``). Never read or defaulted-to by any code
#: path here; ``anchor_store_from_env``/``GitBranchAnchorStore`` always
#: require the remote to be configured explicitly.
RECOMMENDED_ANCHOR_REPO_SLUG = "mcc-prior-art/mcc-audit-anchors"

DEFAULT_CHECKPOINTS_FILENAME = "checkpoints.jsonl"
DEFAULT_GIT_USER_NAME = "MCC-Core Checkpoint Anchor"
DEFAULT_GIT_USER_EMAIL = "mcc-checkpoint-anchor@localhost"
_GIT_TIMEOUT_SECONDS = 30.0


class AnchorStore(ABC):
    """Durable, append-only, external store for signed checkpoints."""

    @abstractmethod
    def append_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Durably record one signed checkpoint. Raises ``AnchorStoreError``
        on any failure -- including a rejected push (fast-forward failure,
        branch protection). Never partially succeeds silently."""

    @abstractmethod
    def read_all_checkpoints(self) -> List[Dict[str, Any]]:
        """Return every anchored checkpoint, oldest first."""

    def read_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        checkpoints = self.read_all_checkpoints()
        return checkpoints[-1] if checkpoints else None


class InMemoryAnchorStore(AnchorStore):
    """Process-local only. Never durable, never shared across processes --
    for tests and local development, exactly like
    ``mcc_core.nonce.InMemoryNonceRegistry``."""

    def __init__(self) -> None:
        self._checkpoints: List[Dict[str, Any]] = []

    def append_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        self._checkpoints.append(dict(checkpoint))

    def read_all_checkpoints(self) -> List[Dict[str, Any]]:
        return [dict(c) for c in self._checkpoints]


class GitBranchAnchorStore(AnchorStore):
    """Anchors checkpoints as commits on a dedicated branch of a git
    remote (Option A). Each checkpoint is appended as one JSON line to
    ``checkpoints_filename`` and committed+pushed individually, so the
    branch's own commit history is a second, independent, append-only
    record of every checkpoint ever issued -- an attacker who can rewrite
    the audit log's storage still cannot rewrite already-pushed commits on
    a branch with server-side protection (linear history, no force-push)
    without that push being rejected (see ``append_checkpoint``, which
    never passes ``--force`` and treats a rejected push as
    ``AnchorStoreError``, not a fallback).

    ``workdir`` is a dedicated local clone used ONLY by this store --
    never the caller's own working tree. It is created on first use if it
    does not already contain a clone.
    """

    def __init__(
        self,
        *,
        remote_url: str,
        branch: str,
        workdir: str,
        checkpoints_filename: str = DEFAULT_CHECKPOINTS_FILENAME,
        git_user_name: str = DEFAULT_GIT_USER_NAME,
        git_user_email: str = DEFAULT_GIT_USER_EMAIL,
    ) -> None:
        if not remote_url:
            raise AnchorStoreError("GitBranchAnchorStore requires a non-empty remote_url")
        if not branch:
            raise AnchorStoreError("GitBranchAnchorStore requires a non-empty branch")
        if not workdir:
            raise AnchorStoreError("GitBranchAnchorStore requires a non-empty workdir")
        self.remote_url = remote_url
        self.branch = branch
        self.workdir = workdir
        self.checkpoints_filename = checkpoints_filename
        self.git_user_name = git_user_name
        self.git_user_email = git_user_email

    def _run(self, args: List[str], *, check: bool = True) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=self.workdir,
                capture_output=True,
                text=True,
                timeout=_GIT_TIMEOUT_SECONDS,
                check=check,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            raise AnchorStoreError(f"git {' '.join(args)!r} failed: {exc}") from exc

    def _configure_identity(self) -> None:
        self._run(["config", "user.name", self.git_user_name])
        self._run(["config", "user.email", self.git_user_email])
        # Deliberate: this identity/commit-signing override applies ONLY to
        # this dedicated checkpoint-anchor workdir's local git config, never
        # the main repository checkout or any of its commits.
        self._run(["config", "commit.gpgsign", "false"])

    def _ensure_local_clone(self) -> None:
        git_dir = Path(self.workdir, ".git")
        if not git_dir.exists():
            os.makedirs(self.workdir, exist_ok=True)
            self._run(["init"])
            self._run(["remote", "add", "origin", self.remote_url])
            self._configure_identity()

        self._run(["fetch", "origin"], check=False)
        remote_has_branch = self._run(
            ["rev-parse", "--verify", f"refs/remotes/origin/{self.branch}"], check=False
        ).returncode == 0

        if remote_has_branch:
            checkout = self._run(["checkout", "-B", self.branch, f"origin/{self.branch}"], check=False)
            if checkout.returncode != 0:
                raise AnchorStoreError(
                    f"could not check out anchor branch {self.branch!r} from origin: "
                    f"{checkout.stderr.strip()}"
                )
            self._run(["reset", "--hard", f"origin/{self.branch}"])
        else:
            # Orphan branch: no shared history with main, by design -- the
            # anchor branch's own linear commit history is the record, not
            # its relationship to the product branches.
            current = self._run(["symbolic-ref", "--short", "HEAD"], check=False)
            if current.returncode != 0 or current.stdout.strip() != self.branch:
                self._run(["checkout", "--orphan", self.branch])
            self._run(["rm", "-rf", "--", "."], check=False)
            readme = Path(self.workdir, "README.md")
            readme.write_text(
                "# MCC-Core Audit Checkpoint Anchors\n\n"
                "This branch is an append-only external anchor store for "
                "MCC-Core checkpoint records. See "
                "docs/AUDIT_CHECKPOINT_ANCHORING.md on main. Do not rebase, "
                "amend, or force-push this branch.\n",
                encoding="utf-8",
            )
            self._run(["add", "README.md"])
            self._run(["commit", "-m", "Initialize audit checkpoint anchor branch"])
            push = self._run(["push", "-u", "origin", self.branch], check=False)
            if push.returncode != 0:
                raise AnchorStoreError(
                    f"could not create/push anchor branch {self.branch!r}: {push.stderr.strip()}"
                )

    def append_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        self._ensure_local_clone()
        checkpoints_path = Path(self.workdir, self.checkpoints_filename)
        line = json.dumps(checkpoint, sort_keys=True)
        with checkpoints_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        self._run(["add", self.checkpoints_filename])
        record_count = checkpoint.get("record_count")
        head = str(checkpoint.get("chain_head_hash", ""))[:12]
        commit = self._run(
            ["commit", "-m", f"Anchor checkpoint: record_count={record_count} head={head}"],
            check=False,
        )
        if commit.returncode != 0:
            raise AnchorStoreError(f"git commit failed: {commit.stderr.strip()}")
        # Fast-forward only -- NEVER --force. A rejected push (branch
        # protection, or a concurrent anchor writer that got there first)
        # is a hard failure, not something this method silently retries by
        # force-pushing over it.
        push = self._run(["push", "origin", self.branch], check=False)
        if push.returncode != 0:
            raise AnchorStoreError(
                f"push of anchored checkpoint to {self.branch!r} was rejected "
                f"(not force-pushing): {push.stderr.strip()}"
            )

    def read_all_checkpoints(self) -> List[Dict[str, Any]]:
        self._ensure_local_clone()
        checkpoints_path = Path(self.workdir, self.checkpoints_filename)
        if not checkpoints_path.exists():
            return []
        checkpoints: List[Dict[str, Any]] = []
        with checkpoints_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    checkpoints.append(json.loads(line))
        return checkpoints


def anchor_store_from_env(env: Optional[Mapping[str, str]] = None) -> AnchorStore:
    """Select an anchor store from configuration, mirroring
    ``mcc_core.nonce.nonce_registry_from_env``'s no-silent-fallback
    discipline.

    * ``MCC_CHECKPOINT_ANCHOR_BACKEND=memory`` (default) -> ``InMemoryAnchorStore``.
    * ``MCC_CHECKPOINT_ANCHOR_BACKEND=git``               -> ``GitBranchAnchorStore``
      built from ``MCC_CHECKPOINT_ANCHOR_REMOTE_URL``, ``MCC_CHECKPOINT_ANCHOR_BRANCH``
      (default ``audit-checkpoint-anchors``), and ``MCC_CHECKPOINT_ANCHOR_WORKDIR``.

    Selecting ``git`` without the required configuration raises
    ``AnchorStoreError`` rather than quietly running with a non-durable,
    process-local store.
    """
    env = os.environ if env is None else env
    backend = env.get("MCC_CHECKPOINT_ANCHOR_BACKEND", "memory").strip().lower()

    if backend in ("memory", "inmemory", "in-memory"):
        return InMemoryAnchorStore()

    if backend == "git":
        remote_url = env.get("MCC_CHECKPOINT_ANCHOR_REMOTE_URL", "").strip()
        workdir = env.get("MCC_CHECKPOINT_ANCHOR_WORKDIR", "").strip()
        branch = env.get("MCC_CHECKPOINT_ANCHOR_BRANCH", "audit-checkpoint-anchors").strip()
        if not remote_url or not workdir:
            raise AnchorStoreError(
                "MCC_CHECKPOINT_ANCHOR_BACKEND=git requires "
                "MCC_CHECKPOINT_ANCHOR_REMOTE_URL and MCC_CHECKPOINT_ANCHOR_WORKDIR; "
                "refusing to fall back to a non-durable in-memory anchor store"
            )
        return GitBranchAnchorStore(remote_url=remote_url, branch=branch, workdir=workdir)

    raise AnchorStoreError(
        f"unknown MCC_CHECKPOINT_ANCHOR_BACKEND={backend!r}; expected 'memory' or 'git'"
    )
