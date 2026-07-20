# Integration Contract — golden vectors

Framework-neutral, transport-neutral golden vectors for the MCC-Core Integration
Contract (`docs/INTEGRATION_CONTRACT.md`, contract version `1.0`).

These vectors are **derived from the canonical SDK models** (`mcc_client.Verdict`,
`mcc_client.Decision`) and the canonical normative layer (`mcc_client.contract`).
They do not depend on VoltAgent, HTTP, a running gateway, or repository checkout
state, so an external adapter author (and PR #44's Compliance & Certification
Suite) can replay them offline.

Each vector carries: an `id`, an input document, the expected validation outcome,
the expected stable error code where invalid, and a short mutation description.

| File | Exercised entry point |
|------|-----------------------|
| `decisions.json` | `mcc_client.Decision.from_response` (verdict binding, fail-closed) |
| `versions.json`  | `mcc_client.contract.check_version_compatibility` |
| `errors.json`    | `mcc_client.contract.error_code_for_exception` + `category_of` |

They are validated by `tests/test_integration_contract_layer.py`. `decisions.json`
is intentionally exercised through the **existing** `Decision.from_response`
model — the contract reuses that model as canonical rather than defining a second
one.
