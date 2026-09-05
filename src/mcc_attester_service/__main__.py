"""Reference standalone entrypoint: ``python -m mcc_attester_service``.

Runs the Independent Attester Service as its own OS process. Provider
selection is delegated to :mod:`mcc_attester_service.provider_loader`, per
``MCC_DEPLOYMENT_MODE`` (Production Trust Hardening Phase 1, Workstream 2):

* ``MCC_DEPLOYMENT_MODE=reference`` (default) -- wired to the DETERMINISTIC
  TEST PROVIDER only (see ``provider.py``'s own explicit warning: that
  provider is a reference/test harness, never a production assessment
  source). This is unchanged from the module's original behavior and is
  what ``tests/test_attester_service_process_isolation.py`` boots as a real
  subprocess to prove PR-4's independence claim (a genuinely separate,
  separately runnable process, not two Python objects sharing an
  interpreter).
* ``MCC_DEPLOYMENT_MODE=enforcement`` -- refuses the test provider outright
  and requires ``MCC_ATTESTER_PROVIDER_CLASS`` to name the operator's own
  trusted :class:`~mcc_attester_service.provider.AssessmentProvider`
  implementation (see ``provider_loader.py`` for the exact contract). This
  module still never ships or endorses a concrete production provider.

Configuration (all via environment variables; every one of these is
REQUIRED -- see ``config.py`` for the fail-closed rationale):

* every ``config.attester_service_config_from_env`` variable
  (``MCC_ATTESTER_ID``, ``MCC_ATTESTER_SIGNING_KEY_PATH``,
  ``MCC_ATTESTER_KEY_ID``, ``MCC_ATTESTER_SERVICE_AUTH_SECRET``,
  ``MCC_ATTESTER_SCOPE_TEMPLATE``, optionally
  ``MCC_ATTESTER_VALIDITY_SECONDS``/``MCC_ATTESTER_POLICY_HASH``/
  ``MCC_ATTESTER_POLICY_VERSION``);
* reference mode: ``MCC_ATTESTER_TEST_ASSESSMENT_TABLE`` -- path to a JSON
  file mapping ``fnmatch`` action patterns to ``{"evidence_type": ...,
  "claims": {...}, "provenance": {...}}``, loaded into a
  ``DeterministicTestProvider``;
* enforcement mode: ``MCC_ATTESTER_PROVIDER_CLASS`` -- dotted import path to
  the operator's trusted ``AssessmentProvider`` subclass;
* ``MCC_ATTESTER_HOST`` (default ``127.0.0.1``), ``MCC_ATTESTER_PORT``
  (required).
"""

from __future__ import annotations

import os
import sys

from mcc_core.deployment_mode import DeploymentModeConfigError

from .config import attester_service_config_from_env
from .errors import AttesterServiceConfigError
from .provider_loader import assessment_provider_from_env


def main() -> None:
    import uvicorn

    from .app import build_attester_app

    env = os.environ
    try:
        config = attester_service_config_from_env(env)
        provider = assessment_provider_from_env(env)
    except (AttesterServiceConfigError, DeploymentModeConfigError) as exc:
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
