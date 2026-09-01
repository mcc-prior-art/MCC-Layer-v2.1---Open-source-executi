# Pilot Acceptance Checklist

```
The model proposes. MCC decides. The gate enforces. The audit chain records.
```

This checklist accompanies [`docs/PILOT_RUNBOOK.md`](PILOT_RUNBOOK.md). It
separates what AXLOGIQ/MCC-Core can verify from this repository alone from
what only an external partner can confirm. **No section of this document
is a claim that a pilot has occurred, succeeded, or been externally
validated.** It is a checklist to be filled in and confirmed jointly with
a real pilot partner, not a report of a completed one.

---

## Pre-pilot technical checks

To be completed before any candidate action is submitted against a real
Gateway:

- [ ] Repository cloned at an exact, recorded commit SHA (`docs/PILOT_RUNBOOK.md` §4).
- [ ] `mcc_sdk` installed from that exact commit; `python3 -c "import mcc_sdk; print(mcc_sdk.__version__)"` succeeds.
- [ ] `pilot/reference_python` test suite (`tests/pilot/`) passes in this environment.
- [ ] A Gateway instance is reachable and reports `"status": "ok"` from `GET /health` (and `GET /ready` if the deployment exposes it).
- [ ] `MCC_PILOT_*` configuration reviewed; no real secret, partner name, or production endpoint is committed to this repository.
- [ ] `MCC_PILOT_MODE=observe` confirmed as the starting mode.
- [ ] The evidence output directory (`MCC_PILOT_EVIDENCE_DIR`) exists and is writable, and is not a tracked repository path.

## Partner responsibilities

- [ ] Provide (or approve use of) the Gateway instance the pilot will connect to, including its base URL and any required API key, communicated outside this repository.
- [ ] Define the specific candidate action(s) the pilot integration will submit, and confirm they contain no data the partner considers sensitive beyond what they've approved for this pilot.
- [ ] Review and approve the observe-mode evidence before agreeing to any transition to enforced mode.
- [ ] Designate a technical point of contact able to authorize the enforced-mode transition and any rollback.
- [ ] Independently review this repository's code (not just this document) before relying on any of its fail-closed claims.
- [ ] Confirm, in writing, whatever subset of "the pilot succeeded" they are willing to attest to — AXLOGIQ/MCC-Core does not make that determination on the partner's behalf.

## AXLOGIQ / MCC-Core responsibilities

- [ ] Keep this runbook and checklist synchronized with the actual code in `pilot/reference_python/` and `sdk/mcc-sdk/` (no undocumented behavior change).
- [ ] Not modify Gateway decision semantics, the `/evaluate` request/response contract, or the fail-closed default for the purposes of any single pilot.
- [ ] Not represent any pilot as completed, certified, audited, or externally validated without the partner's explicit, written confirmation.
- [ ] Provide the pinned commit SHA, evidence schema, and reference integration source for the partner's own independent review.
- [ ] Disclose known limitations of the reference integration (simulated actuator only, no production actuator, no retry semantics) before the pilot begins.

## Observe-mode exit criteria

All of the following should hold before considering a transition to
enforced mode:

- [ ] At least one full pilot run has completed in observe mode with `status: "PASS"` in its evidence bundle.
- [ ] Every candidate action the partner intends to submit in enforced mode has been exercised at least once in observe mode, and its decision (`ALLOW`/`DENY`/`ESCALATE`/`CONSTRAIN`) reviewed and understood by the partner.
- [ ] No `malformed_count`, `timeout_count`, or `unavailable_count` greater than zero remains unexplained.
- [ ] The partner has reviewed the observe-mode evidence bundle(s) and the correlated Gateway audit-log entries (`docs/PILOT_RUNBOOK.md` §14).
- [ ] The partner's technical point of contact has explicitly agreed, in writing, to proceed to enforced mode.

## Enforced-mode entry criteria

- [ ] All observe-mode exit criteria above are met.
- [ ] `MCC_PILOT_MODE=enforced` is set deliberately, not left over from a default, and the operator understands only `ALLOW`/`CONSTRAIN` decisions can reach the simulated actuator.
- [ ] The partner understands and accepts that the actuator is local and simulated — no real external system is called by this reference integration under any configuration.
- [ ] A rollback/emergency-disable procedure (`docs/PILOT_RUNBOOK.md` §10) has been reviewed and rehearsed by whoever will operate the pilot.
- [ ] An evidence output location is agreed and confirmed reachable/writable.

## Success criteria

A pilot run is technically successful when, and only when, all of the
following are objectively true of its exported evidence bundle:

- [ ] The evidence bundle validates against `pilot/schema/pilot_evidence.schema.json`.
- [ ] `status: "PASS"` with a `status_reason` that is understood and accepted by the partner.
- [ ] `malformed_count == 0`, `unavailable_count == 0`, and `attempted_bypass_count == 0`.
- [ ] `total_evaluated > 0` — at least one real candidate action was actually evaluated.
- [ ] Every `correlation_refs` entry's `audit_id`/`trace_id` is independently found in the Gateway's own audit log export (`docs/PILOT_RUNBOOK.md` §14).
- [ ] If `final_mode == "enforced"`, `executed_count` matches the partner's own independent count of expected simulated actuations (no more, no fewer).

Meeting these criteria demonstrates the reference integration behaved as
documented against a real Gateway. It does **not**, by itself, establish
that the underlying candidate actions were the right ones for the
partner's real workflow, or that the pilot should proceed to any further
stage — those are partner decisions.

## Stop conditions

Any of the following is sufficient reason to immediately stop the pilot
and, if in enforced mode, revert to observe mode or fully disconnect
(`docs/PILOT_RUNBOOK.md` §10):

- [ ] `attempted_bypass_count > 0` in any evidence bundle.
- [ ] Any evidence bundle fails to validate against the published schema.
- [ ] An actuated (`executed=True`) receipt's payload does not exactly match the Gateway's own `forward_context` for that decision.
- [ ] Repeated, unexplained `malformed_count`, `timeout_count`, or `unavailable_count`.
- [ ] Any indication the Gateway instance in use is not the one the partner approved.
- [ ] The partner's technical point of contact requests a stop, for any reason.

## Evidence required for an externally attributable pilot result

A result can be described as externally attributable only when all of the
following exist and are retained:

- [ ] The exact commit SHA the pilot ran (`mcc_commit_sha` in the evidence bundle, cross-checked against the partner's own clone).
- [ ] The full set of evidence bundles produced during the pilot, unmodified since export.
- [ ] The corresponding Gateway audit-log export (`docs/PILOT_RUNBOOK.md` §14), independently retained by (or accessible to) the partner — not only by AXLOGIQ/MCC-Core.
- [ ] A written statement from the partner's own technical point of contact confirming the pilot ran against their environment and describing what they observed, in their own words.
- [ ] Explicit documentation of what the pilot did and did not test (e.g. "simulated actuator only; no production actuator was exercised").

## Attestation-aware full-chain mode — additional checks (PR-6)

Everything above applies unchanged to the legacy evaluate-only mode. The
following applies **only** when a partner opts into the attestation-aware
full-chain mode (`docs/PILOT_RUNBOOK.md` Part II, §18-24) — it does not
replace any check above.

- [ ] The Independent Attester Service used is a genuinely separate
      process from the Gateway (`docs/PILOT_RUNBOOK.md` §20) — not merely
      two Python objects in one interpreter (see
      `tests/test_attester_service_process_isolation.py` for the proof
      this claim rests on).
- [ ] The partner understands the Attester's assessment provider in this
      reference deployment is the **deterministic test provider**, never a
      production risk-assessment source (`specs/MCC-AT-004.md`).
- [ ] The partner has reviewed which claims the demo attestation carries
      (`risk_class: low`, fixed) and understands this is a fixture, not a
      real risk assessment of their candidate action.
- [ ] Observe-mode exit criteria (above) are also met for the full-chain
      mode's own evidence bundles (`pilot_attestation_evidence.schema.json`)
      before any transition to its enforced mode.
- [ ] The partner understands enforced full-chain mode still performs no
      real external action — the governed actuator is the same
      loopback/simulated upstream used elsewhere in this repository's
      pilot deployments, never a production actuator.
- [ ] The `known_limitations` field of every full-chain evidence bundle has
      been read, not skipped (`docs/PILOT_RUNBOOK.md` §23) — it states
      what this bundle deliberately does not include and why.
- [ ] The partner understands `docs/ATTESTATION_INDEPENDENT_ASSURANCE.md`
      (PR-5) is assurance evidence for the underlying chain's security
      properties, self-administered and reproducible by anyone — it is
      **not** a substitute for, and does not itself constitute, a
      completed external pilot or third-party audit of this partner's own
      deployment.

## Items that cannot be claimed until confirmed by the external partner

The following must never be asserted by AXLOGIQ/MCC-Core — in this
repository, in marketing material, or anywhere else — without the
partner's own explicit, written, and dated confirmation:

- [ ] That a pilot with this partner occurred at all.
- [ ] That a pilot "succeeded," in any sense beyond the technical success
      criteria above being met on infrastructure AXLOGIQ/MCC-Core
      controlled or observed alone.
- [ ] That the partner has adopted, endorsed, or intends to adopt
      MCC-Core in production.
- [ ] Any specific volume, value, or business outcome attributable to the
      pilot.
- [ ] That the partner has reviewed or approved any AXLOGIQ/MCC-Core
      public communication referencing them.
- [ ] Third-party validation, certification, or audit of MCC-Core arising
      from this pilot.
