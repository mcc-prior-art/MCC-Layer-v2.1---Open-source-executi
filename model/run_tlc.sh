#!/usr/bin/env bash
# PR #71 Workstream I -- run TLC against MCCExecutionStateMachine.tla.
#
# Downloads tla2tools.jar into model/tools/ (git-ignored, never vendored)
# if not already present, then exhaustively checks every INVARIANT and
# PROPERTY declared in MCCExecutionStateMachine.cfg. Exits non-zero (TLC's
# own exit code) if any property is violated -- CI (or a developer) treats
# a non-zero exit here as a real, machine-checked failure, not advisory
# output to eyeball.
#
#   model/run_tlc.sh                    # the small, default 2-operation config
#   model/run_tlc.sh path/to/other.cfg  # a different, e.g. larger, config

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${1:-$SCRIPT_DIR/MCCExecutionStateMachine.cfg}"
SPEC="$SCRIPT_DIR/MCCExecutionStateMachine.tla"
TOOLS_DIR="$SCRIPT_DIR/tools"
JAR="$TOOLS_DIR/tla2tools.jar"
JAR_URL="https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar"

if ! command -v java >/dev/null 2>&1; then
    echo "ERROR: java is required to run TLC (Java 11+; this repo was validated on Java 21)" >&2
    exit 2
fi

if [ ! -f "$JAR" ]; then
    echo "tla2tools.jar not found -- downloading to $JAR"
    mkdir -p "$TOOLS_DIR"
    if ! curl -sS -L --max-time 120 -o "$JAR" "$JAR_URL"; then
        echo "TLC_JAR_DOWNLOAD_FAILED: could not download $JAR_URL (no network access?)" >&2
        rm -f "$JAR"
        exit 3
    fi
fi

cd "$SCRIPT_DIR"
exec java -cp "$JAR" tlc2.TLC -config "$CONFIG" "$SPEC"
