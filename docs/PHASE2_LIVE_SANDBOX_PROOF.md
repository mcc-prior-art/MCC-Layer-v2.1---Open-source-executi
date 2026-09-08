# Phase 2 Live Sandbox Proof

> **PROPOSAL != PERMISSION.**
> **MARKER != AUTHORITY.**
>
> No verified authority → no execution.

## 0. What this proves, and what it does not

This is a minimum, production-like proof that the existing, unmodified
`gateway.proposal_execution_service.ProposalExecutionService.authorize_and_execute`
path — the Phase 2 bridge landed in PR #106 — can reach a REAL external
side effect (one harmless GitHub issue, in an explicitly isolated sandbox
repository) without weakening or bypassing any existing authority,
durability, audit, tenant-isolation, or reconciliation guarantee.

**What it proves:**

* the full chain — authenticated tenant → tenant-owned proposal → exact
  stored action/resource/canonical payload → trusted `AuthorityModel`
  evaluation → signed authority token → `ExecutionGate` verification →
  tenant-scoped durable admission → durable dispatch ownership →
  audit-before-actuation → `ResourceBoundUpstream` → a real external side
  effect — is reachable end-to-end through code that already exists and
  was not modified for this proof;
* the authorized resource genuinely determines the real external
  destination, not merely a string checked once and discarded;
* the exact outbound payload sent externally is the exact payload MCC-Core
  authorized;
* replay, concurrency, cross-tenant, `UNKNOWN`, and reconciliation
  guarantees all hold when a REAL network call and REAL durable Redis
  state are involved, not only in an all-in-memory unit test.

**What it does NOT prove:**

* that GitHub (or any specific external system) is itself trustworthy or
  available — this proof's sandbox target is a convenience choice, not a
  claim about any particular vendor;
* organizational/operational independence of anything — same disclaimer
  this repository's other cryptographic-evidence claims already carry;
* production readiness of the sandbox actuator as a real product feature
  — `GitHubIssueActuator` (reused unchanged from
  `examples/gpt6_astra_reference/`) is a reference/demo actuator, not a
  hardened production integration;
* that a dispatcher implementation can be prevented, at the interface
  level, from ignoring the `resource` argument it is explicitly handed
  and hardcoding some other destination regardless — no Python interface
  change can guarantee that (see
  `docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE2.md` §5 for the identical,
  already-documented limitation).

## 1. Exact execution chain

```
authenticated tenant
    |
    v
MCCProposalService.submit_proposal            (tenant-scoped proposal,
    |                                          canonical payload already
    |                                          marked -- see §4)
    v
ProposalExecutionService.authorize_and_execute (the ONE new entry point
    |                                            this proof calls)
    v
ProposalRegistry.get(tenant_id=, logical_operation_id=)   (ownership +
    |                                                       own stored content)
    v
AuthorityModel.evaluate(identity=tenant_id, ...)           (trusted verdict)
    |
    v
DecisionEngine.issue_token                                 (signed authority)
    |
    v
EnforcementCoordinator.enforce                              (the ONE
    |                                                        execution path:
    |                                                        ExecutionGate +
    |                                                        tenant-scoped
    |                                                        IdempotencyRegistry +
    |                                                        audit-before-actuation)
    v
ResourceBoundUpstream.execute(resource=, action=, payload=)  (Phase 2's
    |                                                          existing
    |                                                          resource-
    |                                                          binding contract)
    v
GitHubSandboxUpstream -> GitHubIssueActuator                 (this proof's
    |                                                         ONE new wrapper
    |                                                         + a REUSED,
    |                                                         unmodified real
    |                                                         HTTP actuator)
    v
real (or, in deterministic CI, locally-mocked) external side effect
    |
    v
durable EXECUTED / UNKNOWN (mcc_core.idempotency, unchanged)
    |
    v
MCCProposalService.get_operation_status        (tenant-safe status read)
    |
    v
reconcile_proposal_operation                    (existing, unmodified
                                                  reconciliation entry point)
```

No alternate path exists. `examples/phase2_live_sandbox/` (this proof's
ONLY new code) contains no second `Gate`, no second
`EnforcementCoordinator`, no second durable execution registry, and no
duplicated authorization logic — every governance decision is made by the
SAME primitives every other production/reference caller in this
repository already uses.

## 2. Sandbox isolation

* **Default: fully disabled.** `SandboxConfig.from_env` (`examples/
  phase2_live_sandbox/config.py`) requires `MCC_PHASE2_LIVE_SANDBOX=1`
  before treating ANY other setting as meaningful; unset, every code path
  that could reach an actuator raises before any I/O.
* **No default sandbox repository.** `MCC_PHASE2_SANDBOX_REPO=owner/repo`
  must be explicitly set when live mode is enabled.
* **The MCC-Core repository is refused by construction.**
  `mcc-prior-art/mcc-layer` is in `FORBIDDEN_SANDBOX_REPOS`; configuring it
  as the sandbox target raises `SandboxConfigError` at config-construction
  time, before a stack is even built, let alone a token issued. There is a
  theoretical override (`MCC_PHASE2_ALLOW_CORE_REPO=1`) purely so the
  refusal itself is testable — no workflow in this repository sets it, and
  operators should not either.
* **The actuator's destination never comes from proposal content.** The
  sandbox repository is fixed once, at actuator-construction time, from
  `SandboxConfig` — never from a proposal's payload/resource field (which
  is instead independently *verified against* that fixed value; see §3).

## 3. Proof: authorized resource determines the actual destination

`GitHubSandboxUpstream` (`examples/phase2_live_sandbox/actuator.py`) wraps
the reused, unmodified `GitHubIssueActuator`. Its `.resource` attribute IS
`actuator.config.repo` — the ONE value the real HTTP call
(`GitHubIssueActuator.__call__`, unchanged) can ever POST to
(`{base_url}/repos/{actuator.config.repo}/issues`). There is no second,
independently-settable destination anywhere in this wrapper.

`execute(*, resource, action, payload)` — Phase 2's existing
`ResourceBoundUpstream` contract (PR #106) — compares the AUTHORIZED
`resource` against this one fixed value before ever delegating; on
mismatch it raises `ResourceMismatchError`, zero HTTP call. On match,
delegation reaches an actuator instance that structurally has no other
destination to send to. This is the SAME "authorized resource is part of
the actual invocation, not separate discarded metadata" design PR #106's
final remediation round established — reused here unchanged, applied to a
real external actuator instead of a test double.

Proven directly: `tests/test_phase2_live_sandbox.py::
test_d_resource_mismatch_zero_external_requests` (authorized for a
different repo than the actuator is configured for → `RESOURCE_MISMATCH`,
zero HTTP calls) and the non-vacuity probe
`test_non_vacuity_2_resource_metadata_checked_but_not_used_to_select_destination`
(reproduces the PR #106-era defect with a raw, disconnected wrapper —
shows it WOULD diverge; the real `GitHubSandboxUpstream` cannot express
that divergence at all).

## 4. Exact outbound payload binding

`examples/phase2_live_sandbox/marker.py::prepare_sandbox_issue_payload`
performs the ONE normalization step this action's schema requires
(`title`/`body`, `body` defaulted to `""` if absent — reused unchanged
from `examples/gpt6_astra_reference/issue_contract.py`) and embeds the
reconciliation marker (§6) — **both BEFORE** the payload is ever handed to
`MCCProposalService.submit_proposal`, i.e. before canonicalization,
binding, or authorization (Section 4: "that normalization must happen
BEFORE proposal binding and authorization"). From that point forward,
nothing downstream adds, removes, or rewrites a field — the SAME dict
(deep-copied, never mutated, per PR #106's own Round-24-style hardening
already present in `ProposalExecutionService`) is what gets hashed into
`payload_hash`, signed into the token, and — byte for byte — what
`GitHubIssueActuator` POSTs.

Proven directly: `tests/test_phase2_live_sandbox.py::
test_a_successful_proposal_authority_real_sandbox_dispatch` asserts the
real, recorded external issue's body carries the exact expected composite
marker; `test_e_payload_mismatch_zero_external_requests` proves a payload
tampered AFTER proposal registration (without recomputing its binding) is
refused with zero external calls.

## 5. Durable execution identity

Unchanged: `(tenant_id, logical_operation_id)`, enforced entirely inside
`mcc_core.idempotency`/`mcc_core.coordinator` — this proof introduces no
new durable state, no new identity scheme, and reuses the SAME
`RedisIdempotencyRegistry` every other production/reference caller uses.

`examples/phase2_live_sandbox/stack.py::build_live_sandbox_stack` fails
closed (`RedisUnavailableError`, itself a `SandboxConfigError`) if the
configured Redis cannot be reached — checked via `PING` before ANY
registry, proposal, or actuator object is even constructed. No unscoped
in-memory fallback exists in this module.

## 6. `UNKNOWN` semantics

The proof's own controlled failure mode
(`tests/test_phase2_live_sandbox.py::_crash_after_real_dispatch`) sends a
REAL HTTP request to the sandbox target (so an external side effect
genuinely occurs) and then raises inside the coordinator's executor —
exactly "connection reset/timeout after the request may have reached the
server" (Section 8's own examples). `EnforcementCoordinator.enforce`
(unchanged) durably marks the operation `UNKNOWN`; a second
`authorize_and_execute` call for the identical `(tenant_id,
logical_operation_id)` is blocked, never retried, never causing a second
real side effect (`test_j_unknown_replay_zero_new_external_side_effect`).

## 7. Reconciliation

Uses `gateway.proposal_execution_service.reconcile_proposal_operation`
unchanged (PR #106). The ONE new piece is
`examples/phase2_live_sandbox/evidence.py::make_sandbox_evidence_verifier`
— an `EvidenceVerifier` that queries the sandbox's `GET /repos/{owner}/{repo}/issues`
endpoint for the tenant-scoped composite marker (§6 below... see §8 for the
marker itself) and returns evidence in the EXACT operation-bound shape
`reconcile_proposal_operation` independently re-verifies (`tenant_id`,
`logical_operation_id`, `action`, `resource`, and a `payload` whose hash
must equal the authority-reconstructed `payload_hash`) — never a bare
`{"found": true}`.

Proven directly (`tests/test_phase2_live_sandbox.py`):

* `test_k_unrelated_reconciliation_evidence_no_resolution` — a genuinely
  unrelated real issue exists; reconciliation does not resolve;
* `test_l_cross_tenant_reconciliation_no_resolution` — two tenants use the
  IDENTICAL `logical_operation_id`; tenant-B's reconciliation cannot
  resolve using tenant-A's real issue (see §8: the composite marker is
  what makes this possible against a tenant-blind external system);
* `test_m_exact_reconciliation_evidence_unknown_to_executed` — exact
  matching evidence correctly resolves `UNKNOWN` → `EXECUTED`;
* `test_n_reconciliation_never_invokes_actuator` — reconciliation performs
  zero actuator calls, proven by installing a spy actuator and observing
  it is never invoked.

## 8. The composite marker (`MARKER != AUTHORITY`)

`examples/gpt6_astra_reference/issue_contract.py`'s marker machinery
(reserved delimiters, safety validation, single-occurrence extraction
regex, the payload-preparation helper) is reused COMPLETELY unchanged
(Section 10: "reuse existing marker logic if possible"). The ONE thing
`examples/phase2_live_sandbox/marker.py` adds is WHAT identifier gets
embedded: a composite `"tenant_id::logical_operation_id"` identity, rather
than a bare `logical_operation_id`.

This is a deliberate, necessary departure from the bare format: GitHub
issues carry no tenant concept at all. If two tenants used the IDENTICAL
`logical_operation_id` (Phase 2's own adversarial cross-tenant scenario,
proven independent at the durable-state level throughout PR #105/#106) AND
happened to propose byte-identical content, a bare-`logical_operation_id`
marker would be genuinely ambiguous between them from the external
system's point of view — reconciliation would have no way to tell whose
crashed attempt a matching real issue actually belongs to. Embedding
`tenant_id` into the SAME reserved marker syntax (same functions, same
delimiters, same safety validation — just a different string handed to
them) closes that ambiguity structurally: the two tenants' markers are
different strings, so their real issues are distinguishable, and a
cross-tenant reconciliation attempt searches for a marker that provably
cannot exist.

The marker is evidence only. Finding it is necessary, but never
sufficient, for reconciliation to resolve anything —
`reconcile_proposal_operation`'s own independent field-by-field
verification (§7) is what actually authorizes the `UNKNOWN → EXECUTED`
transition; a marker match with a mismatched `tenant_id`/
`logical_operation_id`/`action`/`resource`/`payload` is refused exactly
like no evidence at all.

## 9. Replay proof

`tests/test_phase2_live_sandbox.py::test_f_replay_exactly_one_external_side_effect`
calls `authorize_and_execute` three times for the identical `(tenant_id,
logical_operation_id)` and asserts, by directly counting the mock
service's recorded issues (never only an internal status), that exactly
one real side effect occurred. `test_g_concurrent_duplicate_at_most_one_external_side_effect`
proves the same property under genuine `asyncio.gather` concurrency.

## 10. Why `PROPOSAL != PERMISSION` still holds

Nothing in this proof lets a proposal mint its own authority.
`ProposalRegistry`/`MCCProposalService` remain exactly as non-actuating as
Phase 1 left them (`tests/test_proposal_service_architecture_guards.py`,
untouched, still passes). `AuthorityModel.evaluate` — the SAME trusted,
tenant-identity-keyed policy engine PR #106 already used — is the ONLY
thing that ever converts a registered proposal into a verdict; a tenant
with no configured grant is denied by default, proven directly
(`test_b_no_authority_zero_external_requests`).

## 11. Why this does not introduce a second execution authority

`examples/phase2_live_sandbox/` contains exactly:

* `config.py` — configuration/safety gating only, no decision logic;
* `actuator.py` — a thin adapter from the existing `GitHubIssueActuator` to
  the existing `ResourceBoundUpstream` contract, no new HTTP-call
  implementation;
* `marker.py` — a thin wrapper choosing a composite identity string for
  the existing marker functions, no new marker syntax;
* `evidence.py` — an `EvidenceVerifier` implementation (a plug-in point
  Phase 2's `reconcile_proposal_operation` already defines), no
  reconciliation logic of its own;
* `stack.py` — wiring (constructs the SAME `DecisionEngine`/
  `ExecutionGate`/`EnforcementCoordinator`/`AuthorityModel`/
  `MCCProposalService`/`ProposalExecutionService` classes every other
  caller constructs), no decision logic;
* `run_live_proof.py` — a thin runner script, calls only
  `ProposalExecutionService.authorize_and_execute` and
  `reconcile_proposal_operation`.

No file in this package imports or reimplements `mcc_core.gate`,
`mcc_core.coordinator`'s decision logic, `mcc_core.authority`'s evaluation
logic, or `mcc_core.idempotency`'s admission logic — it only ever
constructs and calls the real, existing classes.

## 12. Required environment variables

| variable | required when | purpose |
|---|---|---|
| `MCC_PHASE2_LIVE_SANDBOX` | always, to enable anything live | must be `1`/`true`/`yes`; unset = fully disabled |
| `MCC_PHASE2_SANDBOX_REPO` | live mode | `owner/repo`; never `mcc-prior-art/mcc-layer` |
| `GITHUB_TOKEN` | live mode | a token scoped to the sandbox repo only |
| `MCC_REDIS_URL` | live mode | a real, reachable Redis instance |
| `MCC_PHASE2_SANDBOX_GITHUB_BASE_URL` | optional | defaults to `https://api.github.com`; deterministic tests point this at a local mock server instead |
| `MCC_PHASE2_ALLOW_CORE_REPO` | never, in practice | a documented, discouraged override of the core-repo refusal; no workflow in this repository sets it |

## 13. CI design

* **Normal pull-request CI** (`mcc-runtime-ci.yml`'s existing `tests` job)
  runs `tests/test_phase2_live_sandbox.py` as part of `pytest tests/ -v` —
  entirely deterministic: a local mock GitHub HTTP server
  (`examples/gpt6_astra_reference/mock_github_service.py`, reused
  unchanged) and the real local Redis that job already installs. Zero live
  GitHub credentials, zero external network access, zero dependency on
  this proof's optional manual workflow.
* **The manual live proof**
  (`.github/workflows/phase2-live-sandbox-manual.yml`) runs ONLY on
  `workflow_dispatch`, never on `push`/`pull_request`. It requires a
  `PHASE2_SANDBOX_REPO` repository variable and a
  `PHASE2_SANDBOX_GITHUB_TOKEN` repository secret; if either is unset, the
  job fails fast with `LIVE EXTERNAL SANDBOX: NOT EXECUTED — CREDENTIALS
  NOT AVAILABLE` and makes zero external requests. It never targets
  `mcc-prior-art/mcc-layer` (enforced in code, not merely by workflow
  configuration).

## 14. Remaining limitations

* `GitHubIssueActuator` is a reference/demo actuator (reused unchanged
  from `examples/gpt6_astra_reference/`), not a hardened production
  integration — no rate-limit handling, no retry policy beyond what
  `httpx`'s defaults provide.
* As documented in `docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE2.md` §5,
  this proof (like PR #106's own final remediation) cannot cryptographically
  prevent an adversarially/incompetently-written dispatcher from ignoring
  the `resource` parameter it is explicitly handed — this is an inherent
  property of any pluggable-actuator architecture, not something specific
  to this proof.
* The composite tenant-scoped marker (§8) is specific to this sandbox
  proof; it is not (yet) a general-purpose primitive other Phase 2
  reconciliation integrations are required to adopt, though any future
  tenant-aware external evidence source would face the identical
  tenant-blindness problem and likely want the same solution.
* ESCALATE approval consumption, HTTP transport for
  `authorize_and_execute`, and Multi-Context Consensus remain out of scope
  here, exactly as documented in PR #106's own remaining-limitations list
  — this proof does not change that scope.
