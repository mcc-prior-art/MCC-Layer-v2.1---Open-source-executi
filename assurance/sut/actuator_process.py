"""Real protected-actuator subprocess (PR #71, Workstream A).

Boots the existing, unmodified ``egress_proxy`` service -- the repository's
real "protected actuator": it accepts a governed action only bound to a
verified Decision Token, resolves credentials only after authorization,
and is the ONE place an external side effect (an HTTP call to the mock
notification service) actually happens. This is SUT (System Under Test)
provisioning code, not assurance-suite test code -- it may import
``egress_proxy`` internals to *construct* the real deployment, exactly as
``tests/interoperability/_gateway_process.py`` constructs the real Gateway.
No assurance test module imports this file's internals; every workstream
test in ``assurance/tests/`` reaches this actuator only over its real HTTP
API, exactly as an external attacker or a legitimate agent would.

    python -m assurance.sut.actuator_process --port N
"""

from __future__ import annotations

import argparse
import os

from egress_proxy.app import build_app
from egress_proxy.config import EgressSettings


def build(*, notify_base: str, trust_config_path: str, audit_log_path: str,
          require_consensus: bool = True, max_amount: "int | None" = None) -> "FastAPI":  # noqa: F821
    settings = EgressSettings(
        mcc_env="dev",
        api_key=os.environ.get("MCC_ASSURANCE_ACTUATOR_API_KEY", "assurance-actuator-key"),
        operator_api_key=os.environ.get("MCC_ASSURANCE_OPERATOR_KEY", "assurance-operator-key"),
        allowed_hosts="127.0.0.1",
        allowed_methods="get,post",
        allow_loopback=True,
        allow_http=True,  # loopback test upstream is plain HTTP
        require_consensus=require_consensus,
        consensus_threshold=int(os.environ.get("MCC_ASSURANCE_THRESHOLD", "3")),
        consensus_trust_config=trust_config_path,
        audit_log_path=audit_log_path,
        max_amount=max_amount,  # a body.amount CONSTRAIN cap, so Workstream F has a clampable constraint to attack
    )
    return build_app(settings, env={})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--notify-base", required=True)
    ap.add_argument("--trust-config", required=True)
    ap.add_argument("--audit-log", required=True)
    ap.add_argument("--max-amount", type=int, default=None)
    args = ap.parse_args()

    import uvicorn

    app = build(
        notify_base=args.notify_base, trust_config_path=args.trust_config,
        audit_log_path=args.audit_log, max_amount=args.max_amount,
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
