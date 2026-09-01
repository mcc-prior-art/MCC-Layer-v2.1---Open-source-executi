"""Reference standalone entrypoint: ``python -m mcc_attester_service``.

Runs the Independent Attester Service as its own OS process, wired to the
DETERMINISTIC TEST PROVIDER only (see ``provider.py``'s own explicit
warning: that provider is a reference/test harness, never a production
assessment source). A real deployment supplies its own
:class:`~mcc_attester_service.provider.AssessmentProvider` implementation
and, if useful, its own process entrypoint calling
:func:`~mcc_attester_service.app.build_attester_app` directly -- this
module exists so PR-4's independence claim (a genuinely separate,
separately runnable process, not two Python objects sharing an
interpreter) has a real, runnable reference implementation and a real
subprocess test target (``tests/test_attester_service_process_isolation.py``).

Configuration (all via environment variables; every one of these is
REQUIRED -- see ``config.py`` for the fail-closed rationale):

* every ``config.attester_service_config_from_env`` variable
  (``MCC_ATTESTER_ID``, ``MCC_ATTESTER_SIGNING_KEY_PATH``,
  ``MCC_ATTESTER_KEY_ID``, ``MCC_ATTESTER_SERVICE_AUTH_SECRET``,
  ``MCC_ATTESTER_SCOPE_TEMPLATE``, optionally
  ``MCC_ATTESTER_VALIDITY_SECONDS``/``MCC_ATTESTER_POLICY_HASH``/
  ``MCC_ATTESTER_POLICY_VERSION``);
* ``MCC_ATTESTER_TEST_ASSESSMENT_TABLE`` -- path to a JSON file mapping
  ``fnmatch`` action patterns to ``{"evidence_type": ..., "claims": {...},
  "provenance": {...}}``, loaded into a ``DeterministicTestProvider``;
* ``MCC_ATTESTER_HOST`` (default ``127.0.0.1``), ``MCC_ATTESTER_PORT``
  (required).
"""

from __future__ import annotations

import json
import os
import sys

from .config import attester_service_config_from_env
from .errors import AttesterServiceConfigError
from .provider import AssessmentResult, DeterministicTestProvider


def _load_test_provider(env) -> DeterministicTestProvider:
    table_path = env.get("MCC_ATTESTER_TEST_ASSESSMENT_TABLE", "").strip()
    if not table_path:
        raise AttesterServiceConfigError(
            "MCC_ATTESTER_TEST_ASSESSMENT_TABLE is required to run this reference "
            "entrypoint (it wires the DeterministicTestProvider ONLY) -- a "
            "production deployment must supply its own AssessmentProvider and "
            "its own process entrypoint instead of this module"
        )
    with open(table_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        raise AttesterServiceConfigError(
            f"{table_path!r} must contain a JSON object mapping action patterns "
            f"to assessment entries"
        )
    table = {}
    for pattern, item in raw.items():
        table[pattern] = AssessmentResult(
            evidence_type=item["evidence_type"],
            claims=item.get("claims", {}),
            provenance=item.get("provenance", {}),
        )
    return DeterministicTestProvider(table)


def main() -> None:
    import uvicorn

    from .app import build_attester_app

    env = os.environ
    try:
        config = attester_service_config_from_env(env)
        provider = _load_test_provider(env)
    except AttesterServiceConfigError as exc:
        sys.exit(f"mcc_attester_service: refusing to start: {exc}")

    app = build_attester_app(config=config, provider=provider)

    host = env.get("MCC_ATTESTER_HOST", "127.0.0.1")
    port_raw = env.get("MCC_ATTESTER_PORT", "").strip()
    if not port_raw:
        sys.exit("mcc_attester_service: refusing to start: MCC_ATTESTER_PORT is required")
    port = int(port_raw)

    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
