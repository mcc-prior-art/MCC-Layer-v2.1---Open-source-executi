# GPT-6 Astra Reference Integration

A thin, real, reproducible reference integration demonstrating a frontier
Intelligence provider — GPT-6 Astra, or any OpenAI-compatible model — in
front of the existing, **unmodified** MCC-Core execution-authority chain.

This is not a new architecture. It is a new *client* of the architecture
PR-1 through PR-6 already built, wired through
`examples/gpt6_astra_reference/`.

---

## 1. Purpose

Astra is used here as a concrete, named frontier Intelligence provider.
MCC-Core remains framework- and model-neutral: nothing in
`src/mcc_core/`, `gateway/`, `src/mcc_attestation/`, or
`src/mcc_attester_service/` was changed, and nothing in those packages
knows Astra exists. The reference integration exists to make one claim
concretely demonstrable with a real model and a real (safe) side effect:

> A frontier model may decide what action appears useful. It still cannot
> mint its own execution authority.

---

## 2. Architecture

```
GPT-6 ASTRA (proposal only)
        |
        v
INDEPENDENT ATTESTER          <- mcc_attester_service.AttesterService (PR-4, unmodified)
        |
        v
CONTROL                       <- gateway.pre_execution_control.PreExecutionControl (PR-2, unmodified)
        |
        v
SIGNED EXECUTION AUTHORITY    <- mcc_core.core.DecisionEngine.issue_token (PR-3, unmodified)
        |
        v
AUTHORITY VERIFICATION + GATE <- mcc_core.gate.ExecutionGate, via
        |                        mcc_core.coordinator.EnforcementCoordinator.enforce
        v
EXECUTION                     <- examples.gpt6_astra_reference.github_actuator.GitHubIssueActuator
                                  (the ONE new safe real actuator this integration adds)
```

Doctrine is unchanged: *Proposal != Permission. No verified authority. No
execution.*

Every governed call in this integration goes through the same public
primitives every other governed path in this repository uses
(`GovernanceService.execute_with_mandate`, or the same
`MandateAuthority`/`PreExecutionControl`/`DecisionEngine`/
`EnforcementCoordinator` sequence exposed as explicit steps for the
adversarial scenarios — see `examples/gpt6_astra_reference/pipeline.py`'s
own module docstring). No second Gate, authority, token format, or replay
registry was introduced.

---

## 3. Trust boundaries

* Astra never possesses an MCC decision-token signing key, the Attester's
  Ed25519 signing key, or a pre-configured mandate. The operator-issued
  mandate authorizing `agent/astra-demo` for `create_github_issue` on the
  configured demo repository is issued once, ahead of time, by this
  reference integration's own demo harness — never by Astra.
* Astra's proposal is converted into a closed schema
  (`examples.gpt6_astra_reference.models.AstraProposal`) that carries
  exactly `action`/`resource`/`payload`/`reason`. Every trusted MCC field
  (`verified`, `authority`, a token, an attestation signature,
  `attester_id`, `kid`, `nonce`, any hash, `evidence_digest`,
  `policy_hash`, any validity timestamp, a mandate) is structurally
  rejected if present — see `models.FORBIDDEN_TRUSTED_FIELDS` and
  `tests/test_gpt6_astra_reference.py`'s parametrized rejection tests.
* The Independent Attester independently assesses whatever Astra proposes
  — a proposal is intentionally allowed to enter the assessment pipeline
  (see `docs/EXECUTION_AUTHORITY_BOUNDARY.md` §11) — but its assessment is
  evidence, never authority.
* The real external actuator (`GitHubIssueActuator`) is reachable **only**
  as the `upstream` callable a `GovernanceService`/`EnforcementCoordinator`
  invokes after a genuine ALLOW verdict has cleared the Gate. Astra has no
  reference to it, and the actuator module has no reference to Astra (see
  `tests/test_gpt6_astra_reference_architecture_guards.py`).

---

## 4. Alignment != Authority

Two entirely different systems can each say "no," and this integration
keeps their evidence visibly separate:

* **Model alignment / self-refusal** — Astra itself declines to propose an
  action (`ASTRA_SELF_REFUSAL`). MCC-Core is never invoked. This is a
  property of the model, not of MCC-Core, and MCC-Core is never credited
  for it.
* **Execution authority / MCC enforcement** — Astra proposes an action,
  and MCC-Core's independently verified authority chain refuses to let it
  execute (`MCC_ATTESTATION_DENY` / `MCC_CONTROL_DENY` /
  `MCC_AUTHORITY_DENY` / `MCC_GATE_DENY`).

> Model alignment influences what the model proposes. Execution authority
> determines whether a proposed action may execute.

"Astra chose not to act" (self-refusal) is observably different from
"Astra wanted to act, but MCC refused execution" (enforcement) — the
latter is the demonstration this integration exists to make. See
`examples/gpt6_astra_reference/cli.py::run_self_refusal` and
`tests/test_gpt6_astra_reference.py::test_7_self_refusal_is_not_reported_as_an_mcc_denial`.

---

## 5. Demo scenarios

```
python -m examples.gpt6_astra_reference.cli positive
python -m examples.gpt6_astra_reference.cli tamper
python -m examples.gpt6_astra_reference.cli replay
python -m examples.gpt6_astra_reference.cli expired
python -m examples.gpt6_astra_reference.cli wrong-scope
python -m examples.gpt6_astra_reference.cli autonomous-expansion
python -m examples.gpt6_astra_reference.cli self-refusal
python -m examples.gpt6_astra_reference.cli all
```

By default every scenario uses the offline `DeterministicAstraProvider`
(no OpenAI credentials) and the local mock GitHub service (no real GitHub
mutation) — see §7. Pass `--live-astra` to use a real OpenAI-compatible
endpoint for the Astra side only (requires `OPENAI_API_KEY`/`OPENAI_MODEL`);
the actuator remains pointed at the local mock regardless, unless an
operator independently configures a real repository (see §6).

| Scenario | What it proves | Terminal source | Actuator invocations |
|---|---|---|---|
| `positive` | A legitimately authorized proposal executes | `EXECUTED` | 1 |
| `tamper` | A payload mutated after authority issuance is rejected by the Gate's action/payload-hash binding | `MCC_GATE_DENY` (`PAYLOAD_HASH_MISMATCH`) | 0 |
| `replay` | The same signed authority cannot be used twice | `MCC_GATE_DENY` (`NONCE_REJECTED`) on the 2nd attempt | exactly 1 (from the 1st) |
| `expired` | Authority stops being usable after its real validity window elapses | `MCC_GATE_DENY` (`TOKEN_EXPIRED`) | 0 |
| `wrong-scope` | A proposal for a resource outside the granted mandate is refused before any attempt to execute | `MCC_AUTHORITY_DENY` (`RESOURCE_SCOPE_MISMATCH`) | 0 |
| `autonomous-expansion` | A model deciding, unprompted, that an *additional* action would be useful still lacks authority for it — even though the Attester independently assessed and verified that additional action too | `MCC_AUTHORITY_DENY` (`ACTION_SCOPE_MISMATCH`) on the extra action | 1 (from the primary action only) |

Every denial is attributed to the REAL component that returned it — see
`examples/gpt6_astra_reference/evidence.py::classify_exec_outcome`, which
classifies the exact reason string `PreExecutionControl`/
`MandateVerifier`/`ExecutionGate` already return, inventing no new deny
code.

### On `autonomous-expansion`

The goal of this scenario is not to compromise Astra. It demonstrates a
capable, plausibly well-intentioned model deciding that an additional
action is logically useful, despite lacking authorization for it. The
model may not be malicious or compromised at all — the extra action may
even have been a reasonable judgment call. It still did not have execution
authority for it, and MCC-Core's mandate-scope check refuses it before any
external side effect, regardless of how reasonable the model's judgment
was.

---

## 6. The real actuator, and its safety boundary

`GitHubIssueActuator` performs a real `POST /repos/{owner}/{repo}/issues`
HTTP call. It is disabled by default (`MCC_ASTRA_DEMO_MODE` unset ->
`"disabled"`; every call raises, no HTTP request is ever made). Enabling
it (`MCC_ASTRA_DEMO_MODE=live`) additionally requires
`MCC_ASTRA_GITHUB_REPO=owner/repo` to be explicitly set — there is no
default repository, and the MCC-Core repository itself
(`mcc-prior-art/mcc-layer`) is refused outright even if misconfigured.
`MCC_ASTRA_GITHUB_BASE_URL` defaults to the real GitHub API; the demo
runner overrides it to point at its own local mock service for every
built-in scenario, so the demo never mutates a real GitHub repository
unless an operator deliberately reconfigures it outside the runner's own
defaults.

---

## 7. Dual oracle

Every scenario's evidence trail carries two independent observations:
what MCC-Core itself reports (`ExecOutcome.status`/`.reason`), and an
independent actuator-invocation counter plus, for `positive` and the
primary action of `autonomous-expansion`, the actual issue recorded by the
mock GitHub service (`GET /repos/{owner}/{repo}/issues`). A denial is
never considered proven by MCC's own reported status alone — every
adversarial scenario's test additionally asserts the actuator invocation
count independently.

---

## 8. Claim hygiene

This reference integration does **not** claim:

* external certification, a completed third-party security audit, or bank
  production readiness;
* that GPT-6 Astra (or OpenAI's own model controls) is unsafe or
  inadequate;
* that this demo proves every real-world deployment of MCC-Core, or of
  any Intelligence provider in front of it, is secure.

The correct claim is:

> This reference integration demonstrates that a frontier model's
> proposed actions can be placed behind independently verifiable,
> action-bound execution authority and deterministic pre-execution
> enforcement.

---

## 9. Non-goals

This integration does not redesign MCC-Core, change doctrine, add
Astra-specific behavior to core authorization semantics, trust Astra more
than any other Intelligence provider, or implement a new policy engine, a
second Attester, a second Gate, a second authority-token format, or a
second replay registry. It adds no production payment execution, exposes
no credentials, and does not enable autonomous live mutation of arbitrary
GitHub repositories.
