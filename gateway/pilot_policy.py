"""Hardcoded authority configuration for the first pilot client.

Deliberately not a YAML/DSL file and not a database — on a pilot the policy
is small, reviewed, and shipped as code so it can be read in one screen and
versioned with the runtime. When the second client arrives, this is the file
that forks; the engine, gateway, and interceptor do not.

Shape consumed by ``mcc_core.AuthorityModel.from_config``:

    mandates:  identity -> list of granted authorities (+ optional constraints)
    policies:  ordered list of action patterns -> required authority -> verdicts
    default:   verdict when no policy matches (fail-closed: DENY)
"""

from __future__ import annotations

from typing import Any, Dict

PILOT_POLICY: Dict[str, Any] = {
    # ---- Who holds what authority -------------------------------------
    "mandates": {
        # The payments agent may move money, but only up to a ceiling.
        "agent/payments-bot": [
            {"authority": "payments.send", "constraints": {"max_amount": 5000}},
        ],
        # The ops agent may read infrastructure state. It holds no mandate to
        # destroy anything — so destructive actions will not find authority.
        "agent/ops-bot": [
            {"authority": "infra.read"},
        ],
        # The notifications agent may send customer notifications, bounded by a
        # priority cap (clampable -> CONSTRAIN) and an allowed-channel set
        # (not clampable -> a disallowed channel fails closed to DENY).
        "agent/notify-bot": [
            {"authority": "notify.send",
             "constraints": {"max_priority": 3, "allowed_channel": ["email", "sms"]}},
        ],
        # The AXFlow clinic revenue/booking agent (PR #38 business pilot):
        #   * book/confirm appointments + message/qualify patients  -> ALLOW
        #   * offer a discount up to 20% (clampable)                -> CONSTRAIN
        #   * set priority up to 'routine' (level 1, clampable)     -> CONSTRAIN
        #   * NO refund/complaint authority                         -> ESCALATE
        #   * NO medical-advice authority                           -> DENY
        "agent/axflow-clinic": [
            {"authority": "clinic.book"},
            {"authority": "clinic.message"},
            {"authority": "clinic.discount",
             "constraints": {"max_requested_discount_percent": 20}},
            {"authority": "clinic.priority",
             "constraints": {"max_priority_level": 1}},
        ],
    },
    # ---- What each action requires, and the verdict that follows ------
    #
    # Order matters: first matching pattern wins. Most-specific first.
    "policies": [
        {
            # Within mandate + within the amount cap -> ALLOW.
            # Mandate held but amount over the cap     -> CONSTRAIN (cap binds).
            # No payments.send mandate                 -> ESCALATE (ask a human).
            "action": "send_payment",
            "requires": "payments.send",
            "on_mandate": "ALLOW",
            "on_violation": "CONSTRAIN",
            "without_mandate": "ESCALATE",
        },
        {
            # Reading infra is allowed for a holder of infra.read, else escalate.
            "action": "read_*",
            "requires": "infra.read",
            "on_mandate": "ALLOW",
            "without_mandate": "ESCALATE",
        },
        {
            # Send a customer notification (a safe, non-financial pilot action).
            #   within mandate + priority within cap + allowed channel -> ALLOW
            #   priority over the cap                                   -> CONSTRAIN (clamp)
            #   channel not in the allowed set (not clampable)          -> DENY
            #   no notify.send mandate                                  -> ESCALATE
            "action": "send_notification",
            "requires": "notify.send",
            "on_mandate": "ALLOW",
            "on_violation": "CONSTRAIN",
            "without_mandate": "ESCALATE",
        },
        # ---- AXFlow clinic pilot (PR #38): business-domain governed actions ----
        # Normal booking/messaging within the clinic mandate -> ALLOW; no mandate
        # (a different actor) -> ESCALATE.
        {"action": "appointment_book", "requires": "clinic.book",
         "on_mandate": "ALLOW", "without_mandate": "ESCALATE"},
        {"action": "appointment_confirm", "requires": "clinic.book",
         "on_mandate": "ALLOW", "without_mandate": "ESCALATE"},
        {"action": "patient_message_send", "requires": "clinic.message",
         "on_mandate": "ALLOW", "without_mandate": "ESCALATE"},
        {"action": "lead_qualify", "requires": "clinic.message",
         "on_mandate": "ALLOW", "without_mandate": "ESCALATE"},
        # Excessive discount -> clamp to the cap (CONSTRAIN); within cap -> ALLOW.
        {"action": "discount_offer", "requires": "clinic.discount",
         "on_mandate": "ALLOW", "on_violation": "CONSTRAIN", "without_mandate": "ESCALATE"},
        # Unauthorized priority bump -> clamp to routine (CONSTRAIN).
        {"action": "priority_mark", "requires": "clinic.priority",
         "on_mandate": "ALLOW", "on_violation": "CONSTRAIN", "without_mandate": "ESCALATE"},
        # Refunds, complaints, high-risk handling need human clinic approval. The
        # clinic agent holds no 'clinic.refund' authority -> ESCALATE.
        {"action": "refund_request", "requires": "clinic.refund",
         "on_mandate": "ALLOW", "without_mandate": "ESCALATE"},
        {"action": "complaint_escalate", "requires": "clinic.refund",
         "on_mandate": "ALLOW", "without_mandate": "ESCALATE"},
        # Unsafe medical advice / diagnosis / prescription: no authority can
        # authorize it on the pilot. requires=None -> without_mandate=DENY.
        {"action": "medical_advice_request", "requires": None, "without_mandate": "DENY"},
        {
            # Irreversible destruction: no mandate can authorize it on the
            # pilot. requires=None routes straight to without_mandate=DENY.
            "action": "delete_*",
            "requires": None,
            "without_mandate": "DENY",
        },
    ],
    # No policy matched -> no authority -> DENY.
    "default": "DENY",
}


# Velocity / aggregate ceilings enforced at actuation time (the coordinator),
# distinct from the per-decision authority above. Action pattern -> list of
# limits. Hardcoded for the pilot, like the authority policy.
PILOT_VELOCITY: Dict[str, Any] = {
    "send_payment": [
        # No more than 3 payments per actor per minute.
        {"name": "payment_count", "window_seconds": 60, "max_count": 3,
         "aggregate_by": ["actor"], "on_exceed": "DENY"},
        # No more than 10,000 cumulative per actor per minute — this is the
        # ceiling that four split payments cannot bypass.
        {"name": "payment_amount", "window_seconds": 60, "max_amount": 10000,
         "aggregate_by": ["actor"], "on_exceed": "DENY"},
        # No more than 2 new beneficiaries per actor per minute.
        {"name": "payment_new_beneficiaries", "window_seconds": 60,
         "max_new_destinations": 2, "aggregate_by": ["actor"], "on_exceed": "ESCALATE"},
    ],
}
