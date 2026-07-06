"""Mock clinic / booking / notification service for the AXFlow clinic pilot.

A real, separate HTTP service with NO governance logic. The governed executor
(inside the MCC gateway) makes the outbound call here; this service records the
clinic action and returns a deterministic receipt bound to the executed payload.
It is reachable only by the governed executor, never by the agent.

Not medical advice, not a medical device — a controlled mock for a governed
business workflow pilot.
"""

from .service import app, build_clinic_service, recorded_actions, reset_actions

__all__ = ["app", "build_clinic_service", "recorded_actions", "reset_actions"]
