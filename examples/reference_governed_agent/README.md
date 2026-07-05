# Framework-Neutral Reference Governed Agent

The canonical reference AI agent for MCC-Core. It proves that a real agent can:

1. reason about a natural-language request and **propose** a structured action,
2. submit that proposal to MCC-Core through the supported SDK and receive a
   **governance decision** (`ALLOW` / `DENY` / `ESCALATE` / `CONSTRAIN`),
3. obtain **human approval** when the decision escalates,
4. **execute only through the governed path** — never directly — and only the
   payload MCC-Core authorizes,
5. receive a **verified external receipt**, and
6. produce a **verifiable audit trail**.

> The model proposes. MCC-Core decides. The gate enforces. The audit chain records.

## Canonical path

```
Natural-language request
   │
   ▼
ReasoningProvider          (what to propose — reasoning, never authority)
   │  ProposedAction
   ▼
ReferenceGovernedAgent ──▶ mcc_client (SDK) ──▶ MCC Gateway
                                                   │  decision: ALLOW/DENY/ESCALATE/CONSTRAIN
                                                   ▼
                              Operator (ESCALATE) │ Execution Gate (governed /…/execute)
                                                   ▼
                                             Governed Executor
                                                   ▼
                                        External System + Receipt
                                                   ▼
                                        Append-only audit chain
```

## Design invariants

- **Framework-neutral.** No VoltAgent, LangGraph, CrewAI, or OpenAI Agents SDK
  anywhere in the loop. Any of them can integrate later as an *adapter* that
  produces a `ProposedAction` and hands it to this same SDK boundary.
- **Reasoning is not authority.** A `ReasoningProvider` only decides *what to
  propose*. It never executes, calls the gateway, or reaches an external system.
- **Proposal is not permission.** Nothing runs without an MCC-Core decision.
- **No direct execution path.** The agent holds no HTTP/notification/socket
  client. Every side effect flows agent → MCC SDK → gateway → governed executor →
  external system. A provider or operator failure cannot bypass this — it just
  means there is nothing to submit. A static test enforces the absence of any
  direct networking/execution route in the agent modules.
- **Fail-closed.** Any error, denial, or missing authorization yields a
  non-executed result; the external service is never called.

## Package layout

| Module | Responsibility |
|--------|----------------|
| `agent.py` | `ReferenceGovernedAgent` — propose → evaluate → (approve) → governed execute → verify. SDK-only. |
| `providers.py` | `DeterministicProvider` (default, offline, reproducible) + `OptionalLLMProvider` (opt-in, no mandatory LLM dep; failure ⇒ `ProviderError`, never a bypass). |
| `operator.py` | `Operator` protocol + `ProgrammaticOperator` (tests/headless) + `CLIOperator` (human prompt). |
| `actions.py` | The `send_notification` payload builder + a deterministic NL parser. |
| `authorizers.py` | `ConsensusAuthorizer` — obtains the N-of-M evaluator votes an executable verdict needs; the gate still verifies everything. |
| `models.py` | Typed `ProposedAction`, `AgentRunResult`, `ProviderError`. |
| `cli.py` | The command-line demo. |
| `_localstack.py` | Private demo harness: an in-process governed stack for the CLI (not the agent). |

## Reasoning providers

`DeterministicProvider` is the default. It requires **no external API key, no
network, and no LLM dependency**, and is used by every test, the default demo,
CI, and the Docker E2E so the whole pipeline is reproducible offline.

`OptionalLLMProvider` is an opt-in extension point (`MCC_AGENT_LLM=1` plus an
injected model callable). It ships no hard dependency on any LLM client. If the
model is unconfigured or fails, it raises `ProviderError`: the agent then has no
proposal to submit — a reasoning failure can never produce an ungoverned action.

## Quick start (local, zero setup)

The CLI stands up a self-contained, in-process governed stack (real MCC gateway +
mock notification service + receipt-verifying governed executor):

```bash
export PYTHONPATH="$PWD/src:$PWD:$PWD/sdk/python/src"

python -m examples.reference_governed_agent.cli --scenario allow
python -m examples.reference_governed_agent.cli --scenario deny
python -m examples.reference_governed_agent.cli --scenario constrain
python -m examples.reference_governed_agent.cli \
    --scenario escalate --operator prompt \
    --request "Notify customer-123 that the appointment is confirmed"
```

Each run prints the request, the structured proposal, the MCC verdict and reason,
any applied constraints, the approval status (when required), the execution
result, the external receipt summary, and the audit verification result.

## Docker Compose (real containers)

```bash
docker compose -f docker-compose.reference-agent.yml up --build \
    --abort-on-container-exit --exit-code-from reference-agent
```

This runs redis + the mock notification service + the MCC gateway (with the
receipt-verifying governed executor) + the reference agent. It demonstrates
`DENY` (blocked, service never called) and the genuine `ESCALATE → operator
approval → governed execution → verified external receipt → EXECUTED → valid
audit chain`. The agent shares a network with the gateway only; the mock service
is reachable by the governed executor, not by the agent — there is no bypass path.

`ALLOW`/`CONSTRAIN` genuine execution needs consensus authorization material a
remote agent does not hold; those flows are proven end-to-end in the deterministic
tests (`tests/test_reference_governed_agent.py`).

## Tests

```bash
PYTHONPATH="$PWD/src:$PWD:$PWD/sdk/python/src" \
  python -m pytest tests/test_reference_governed_agent.py -v
```

20 deterministic tests cover all four verdict flows, receipt verification,
approval fail-closed cases, payload preservation/constraint authority, Redis
fail-closed, audit verification, the no-direct-execution static guard, and the
provider invariants.
