#!/usr/bin/env bash
# Reproducible Assurance Entry Point.
#
# Runs, in order: `make independent-assurance` (assurance/tests/, Workstreams
# A-K + negative control), `model/run_tlc.sh` (Workstream I, TLA+ model
# checking), `make mutation-test` (Workstream J, the mutation/defects.py
# corpus). Fails immediately on the first stage that fails. Never cleans,
# resets, restores, checks out, or deletes anything -- if a stage leaves the
# tracked working tree different from how it started, that is reported as a
# hard failure, not silently repaired.
#
# See docs/REPRODUCING_ASSURANCE.md for the full reproduction procedure.
#
# Exit codes of THIS SCRIPT when run directly (e.g. `bash
# scripts/verify_assurance.sh`, NOT through `make`):
#   0    all three stages passed; tracked working tree unchanged throughout.
#   1    the tracked working tree was not clean BEFORE this script started
#        (this is not a genuinely clean checkout -- see docs/REPRODUCING_ASSURANCE.md).
#   <n>  the exact, unmodified exit code of whichever stage failed first --
#        e.g. `make independent-assurance`/`make mutation-test` return 1 on
#        a genuine test/mutation failure; `model/run_tlc.sh` returns 2 if
#        `java` is missing, 3 if the TLC jar download failed, or TLC's own
#        code if a checked property was violated.
#   9    a stage exited 0 but left tracked files modified -- reserved for
#        this script's own tracked-tree-mutation guard (see below).
#
# IMPORTANT -- `make verify-assurance`'s OWN exit code is NOT the same as
# this script's exit code above. GNU Make has a fixed, hard-coded exit-code
# convention (0 = success, 2 = a recipe command failed) and does not, and
# structurally cannot, propagate an arbitrary underlying command's numeric
# exit code as `make`'s own top-level process exit status -- this is true
# of every Makefile, not specific to this one. `make verify-assurance`
# reliably tells you PASS (exit 0) or FAIL (exit 2), which is what shell
# `&&`/`if`/CI systems check; if you need the *exact* originating exit code
# from the table above, invoke this script directly instead of through
# `make`.

set -u

cd "$(git rev-parse --show-toplevel)"

echo "== verify-assurance: pre-flight: tracked working tree must be clean =="
pre="$(git status --porcelain --untracked-files=no)"
if [ -n "$pre" ]; then
    echo "verify-assurance: ABORT -- tracked working tree is not clean before starting." >&2
    echo "This entry point must run from a genuinely clean checkout (see" >&2
    echo "docs/REPRODUCING_ASSURANCE.md). Refusing to reset/clean it for you." >&2
    echo "$pre" >&2
    exit 1
fi
echo "== verify-assurance: pre-flight OK (git status --short is empty) =="

run_stage() {
    local name="$1"
    shift
    echo "== verify-assurance: running: $name =="
    "$@"
    local code=$?
    if [ "$code" -ne 0 ]; then
        echo "verify-assurance: FAIL -- $name exited $code" >&2
        exit "$code"
    fi
    echo "== verify-assurance: $name: PASS =="
}

run_stage "independent-assurance (Workstreams A-K + negative control)" make independent-assurance
run_stage "model/run_tlc.sh (Workstream I: TLA+ model checking)" model/run_tlc.sh
run_stage "mutation-test (Workstream J: mutation/defects.py corpus)" make mutation-test

echo "== verify-assurance: post-flight: tracked working tree must still be clean =="
post="$(git status --porcelain --untracked-files=no)"
if [ -n "$post" ]; then
    echo "verify-assurance: FAIL -- a verification stage modified tracked files:" >&2
    echo "$post" >&2
    echo "verify-assurance: refusing to silently clean/reset/restore/delete." >&2
    echo "This is a regression in one of the three stages above -- report it," >&2
    echo "do not work around it by cleaning the tree." >&2
    exit 9
fi
echo "== verify-assurance: post-flight OK (git status --short is empty) =="

echo
echo "== verify-assurance: PASS =="
echo "independent-assurance + model/run_tlc.sh + mutation-test all succeeded."
echo "Tracked working tree was empty (git status --short) before and after."
exit 0
