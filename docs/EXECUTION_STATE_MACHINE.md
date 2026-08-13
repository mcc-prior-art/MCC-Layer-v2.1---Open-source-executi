# Execution State Machine — Workstream B/I reference (PR #71)

> **PR #71C scope note:** this PR completes this document -- Workstream B
> (the black-box half: `assurance/state_machine.py`, `assurance/tests/
> test_execution_atomicity.py`) landed in #71B; the "Formal model
> (Workstream I)" section below, describing `model/MCCExecutionStateMachine
> .tla`, lands in THIS PR. See `docs/ASSURANCE_COVERAGE_MATRIX.md`.

Part of the **MCC-Core Independent Adversarial Assurance Baseline**. This
document is the normative description of the eight-state execution
lifecycle checked two independent ways: black-box, against the real
running system (`assurance/state_machine.py`,
`assurance/tests/test_execution_atomicity.py`), and formally, via
exhaustive model checking (`model/MCCExecutionStateMachine.tla`).

## The eight states

```
PREPARED ──► AUTHORIZED ──► EVIDENCE_COMMITTED ──► DISPATCHED ──┬─► EXECUTED
    │                                                            │
    └─► DENIED                                                   └─► EXECUTION_UNKNOWN ──► RECONCILED
```

| State | Meaning |
|---|---|
| `PREPARED` | The canonical action has been built and hashed; no authority decision has been made yet. |
| `AUTHORIZED` | A verified decision (consensus / mandate) grants execution; nothing has happened in the world yet. |
| `EVIDENCE_COMMITTED` | The audit entry for this authorization is durably written (`fsync`'d) **before** any attempt to act — audit-before-actuation. |
| `DISPATCHED` | The governed side effect (the outbound call) has been attempted. |
| `EXECUTED` | A verified receipt confirms the side effect happened exactly as authorized. Terminal. |
| `DENIED` | No authority was granted; nothing was dispatched. Terminal. |
| `EXECUTION_UNKNOWN` | Dispatched, but no receipt was confirmed (the upstream call failed, timed out, or the connection dropped). |
| `RECONCILED` | A later process determined the true outcome of an `EXECUTION_UNKNOWN` operation. Terminal. |

Only two transitions leave `PREPARED` (`AUTHORIZED` or `DENIED`); only two
leave `DISPATCHED` (`EXECUTED` or `EXECUTION_UNKNOWN`). Every other edge is
a strict, single successor. `assurance/state_machine.py`'s
`ALLOWED_TRANSITIONS` is the executable form of the diagram above —
`validate_transition_sequence` raises on anything not in that edge set.

## Honesty note: what this repository's actuator actually exposes

`egress_proxy`'s receipt-verifying executor
(`pilot_notify.governed_upstream.receipt_verifying_upstream`) never reports
`executed=true` without an independently confirmed receipt. Concretely,
this collapses the caller-visible surface: a transport failure between
`DISPATCHED` and receipt confirmation is reported **synchronously**, within
the same request/response cycle, as `executed=false` (outcome
`UPSTREAM_ERROR`) — the caller never sees a distinct, persistent "unknown,
come back later" status over the API.

`EXECUTION_UNKNOWN` is a real internal possibility (a request may have
reached the upstream before the connection dropped) but is never a
directly observable, persistent terminal state of this implementation; it
resolves eagerly to "not executed, safe to retry" — the idempotency
registry's `RESERVED`/`EXECUTED`/`FAILED` lifecycle then permits exactly
one further attempt on the same idempotency key. `RECONCILED` in this
implementation is therefore reached implicitly, via a fresh retry, not via
an explicit reconciliation endpoint or a separate caller-visible status.

`assurance/tests/test_execution_atomicity.py`'s fault-injection test
(`test_b5`/`test_b6`) verifies this directly: it hard-kills the real
external-effect-sink OS process mid-scenario (a genuine severed
connection, not a mock), confirms the actuator reports `executed=false`
and no phantom receipt survives, then confirms a same-idempotency-key
retry after recovery executes exactly once.

## Two independent checks, two different questions

| | Black-box (`test_execution_atomicity.py`) | Formal (`model/MCCExecutionStateMachine.tla`) |
|---|---|---|
| Asks | "Does the REAL system's observable behavior land on a state the reference model allows?" | "Can the model's own eight-state, nonce-sharing rules ever reach an illegal configuration, across EVERY possible interleaving?" |
| Method | Real HTTP calls + real process kill against a live 3-process deployment | Exhaustive breadth-first state-space search (TLC) over a small, bounded, abstract model |
| Proves | This implementation, at this commit, in this environment, behaves as classified | The RULES themselves (as written in the .tla module) are internally consistent — no combination of prepare/authorize/deny/dispatch/execute/reconcile/backend-toggle actions violates the six required properties |
| Does NOT prove | That every input, not just the ones tested, behaves this way | That the Python implementation actually follows these rules (that's what the black-box tests are for) |

Neither check substitutes for the other; both are necessary and neither is
sufficient on its own. See `docs/ASSUMPTIONS_AND_LIMITS.md` for the full,
combined statement of what this baseline does and does not establish.

## The formal model (Workstream I)

`model/MCCExecutionStateMachine.tla` models the state machine plus a
one-time-nonce authorization pool and a togglable shared-backend-
availability flag, and checks six properties via `model/run_tlc.sh`
(downloads `tla2tools.jar` on first run; never vendored):

1. **`Inv_TypeOK`** — every reachable state is well-typed.
2. **`Inv_NoDoubleNonceConsumption`** — no two distinct operations are ever
   simultaneously past `AUTHORIZED` holding the same nonce.
3. **`Prop_TerminalStability`** — once an operation reaches a terminal
   state, it never changes again (the standard `P ~> []P` idiom).
4. **`Inv_FailClosedWhileBackendDown`** — every recorded authorization
   event, across the entire explored state space, occurred while the
   shared backend was reachable.
5. **`Inv_ExecutedImpliesAuthorizedPath`** — `EXECUTED` implies the
   operation's nonce was legitimately consumed via `Authorize`.
6. **`Prop_EventualTermination`** — every prepared operation eventually
   reaches a terminal state, under fairness.

Property 6 required *strong* fairness (`SF_vars`), not weak (`WF_vars`),
on the `Authorize`/`Deny` actions — TLC's own counterexample search caught
this: under weak fairness, the model's `ToggleBackend` environment action
can repeatedly enable-then-disable `Authorize`/`Deny` forever without
either ever being *continuously* enabled, so weak fairness never forces
progress; strong fairness (progress guaranteed for an action enabled
*infinitely often*, even if repeatedly interrupted) is the correct
assumption for "the outage is not permanent." This is documented here
because it is a genuine example of the model checker finding a real flaw
in an earlier draft of the specification itself — not the Python system,
the .tla file — which is exactly the kind of error class formal methods
exist to catch.

The default configuration (`MCCExecutionStateMachine.cfg`) uses two
operations and one shared nonce (720 reachable states) specifically to
force the nonce-contention case; a validation run with three operations
and two nonces (76,440 states) was also checked clean. Both are small,
deliberately bounded instances — see `docs/ASSUMPTIONS_AND_LIMITS.md` for
why exhaustive model checking is inherently bounded like this, and what
that does and does not mean for confidence in the result.
