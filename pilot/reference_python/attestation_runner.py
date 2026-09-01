"""Runnable demo/CLI for the attestation-aware full-chain reference pilot
(PR-6).

Connects to TWO already-running services (see ``docs/PILOT_RUNBOOK.md``
§18 for how to start them):

  * a real, separate Independent Attester Service process
    (``python -m mcc_attester_service``);
  * a real MCC-Core Gateway process (``uvicorn gateway.app:app``),
    configured to require this attestation for the demo action.

This script performs NO real external action -- the Gateway's own
governed executor in this demo configuration is a local/loopback mock (see
``docs/PILOT_RUNBOOK.md`` §18). It does not claim, and must never be
presented as, a completed or externally validated pilot -- see
``docs/PILOT_ACCEPTANCE_CHECKLIST.md``.

Usage::

    # 1. generate demo keys/config (once):
    python -m pilot.reference_python.generate_attestation_demo_config

    # 2. start the Attester and Gateway per docs/PILOT_RUNBOOK.md §18
    #    (each in its own terminal, using the env printed by step 1).

    # 3. observe mode (default; obtains an attestation, never executes):
    python -m pilot.reference_python.attestation_runner \\
        --gateway-url http://127.0.0.1:8001 --attester-url http://127.0.0.1:8100 \\
        --api-key demo-key --attester-auth-secret <printed-secret> --mode observe

    # 4. enforced mode (requires the demo mandate from step 1):
    python -m pilot.reference_python.attestation_runner \\
        --mode enforced \\
        --mandate-file pilot/reference_python/.secrets-attestation-demo/demo_mandate.json \\
        ...
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .attestation_config import AttestationChainConfig, AttestationChainConfigError
from .attestation_integration import AttestationChainPilot
from .attester_client import AttesterClientError


def _parse_args(argv: "list[str] | None") -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Attestation-aware full-chain reference pilot demo runner (PR-6). "
        "Connects to already-running Attester and Gateway processes; does not itself "
        "constitute a completed pilot."
    )
    parser.add_argument("--gateway-url", default=None)
    parser.add_argument("--attester-url", default=None)
    parser.add_argument("--api-key", default=None, help="Gateway X-API-Key")
    parser.add_argument("--attester-auth-secret", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    parser.add_argument("--mode", choices=["observe", "enforced"], default=None)
    parser.add_argument("--action", default=None)
    parser.add_argument("--resource", default=None)
    parser.add_argument("--mandate-file", default=None,
                         help="Path to a JSON-encoded signed mandate (required in enforced mode)")
    parser.add_argument("--actor", default="pilot-demo-partner")
    parser.add_argument("--evidence-dir", default="./artifacts/pilot-evidence")
    return parser.parse_args(argv)


def _build_config(args: argparse.Namespace) -> AttestationChainConfig:
    try:
        base = AttestationChainConfig.from_env()
    except AttestationChainConfigError:
        required = {
            "gateway_url": args.gateway_url, "attester_url": args.attester_url,
            "attester_auth_secret": args.attester_auth_secret, "gateway_api_key": args.api_key,
        }
        missing = [k for k, v in required.items() if v is None]
        if missing:
            raise AttestationChainConfigError(
                "no attestation-chain environment configuration found, and these "
                f"required CLI flags are also missing: {', '.join(missing)}"
            ) from None
        base = AttestationChainConfig(**required)  # type: ignore[arg-type]

    from dataclasses import replace

    overrides: "dict[str, Any]" = {}
    if args.gateway_url is not None:
        overrides["gateway_url"] = args.gateway_url
    if args.attester_url is not None:
        overrides["attester_url"] = args.attester_url
    if args.api_key is not None:
        overrides["gateway_api_key"] = args.api_key
    if args.attester_auth_secret is not None:
        overrides["attester_auth_secret"] = args.attester_auth_secret
    if args.timeout_seconds is not None:
        overrides["timeout_seconds"] = args.timeout_seconds
    if args.mode is not None:
        overrides["mode"] = args.mode
    if args.action is not None:
        overrides["action"] = args.action
    if args.resource is not None:
        overrides["resource"] = args.resource
    return replace(base, **overrides) if overrides else base


def run(argv: "list[str] | None" = None) -> int:
    args = _parse_args(argv)
    try:
        config = _build_config(args)
    except AttestationChainConfigError as exc:
        print(f"attestation-chain pilot configuration error: {exc}", file=sys.stderr)
        return 2

    mandate = None
    if config.mode == "enforced":
        if not args.mandate_file:
            print(
                "enforced mode requires --mandate-file (see "
                "pilot.reference_python.generate_attestation_demo_config)",
                file=sys.stderr,
            )
            return 2
        with open(args.mandate_file, "r", encoding="utf-8") as fh:
            mandate = json.load(fh)

    print(
        f"attestation-chain pilot run starting: mode={config.mode!r} "
        f"gateway={config.gateway_url!r} attester={config.attester_url!r} "
        f"action={config.action!r}"
    )

    with AttestationChainPilot(config, evidence_dir=args.evidence_dir) as pilot:
        try:
            outcome = pilot.submit(
                actor=args.actor, context={"channel": "email", "recipient": "demo@example.invalid"},
                mandate=mandate, export_evidence=True,
            )
        except AttesterClientError as exc:
            print(f"FAILED CLOSED: attester unavailable: {exc}", file=sys.stderr)
            return 1

    print(f"  attestation: attester_id={outcome.attestation.get('attester_id')!r} "
          f"attestation_id={outcome.attestation.get('attestation_id')!r}")
    if outcome.execution is not None:
        print(f"  gateway: status={outcome.execution.status!r} "
              f"decision={outcome.execution.decision!r} actuated={outcome.actuated}")
    else:
        print("  gateway: not called (observe mode)")
    print(f"\nevidence written to: {outcome.evidence_path}")
    print(json.dumps(outcome.evidence, indent=2, sort_keys=True))
    print(
        "\nNOTE: this run is a reference-integration demo against a locally "
        "reachable Gateway and Attester. It is not, and must not be presented "
        "as, a completed or externally validated production pilot -- see "
        "docs/PILOT_ACCEPTANCE_CHECKLIST.md."
    )
    return 0 if outcome.evidence["status"] == "PASS" else 1


if __name__ == "__main__":  # pragma: no cover -- manual/CI invocation only
    raise SystemExit(run())
