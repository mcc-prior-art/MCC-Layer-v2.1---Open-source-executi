# MCC (Meta-Cognitive Control)

A control layer between AI-generated intent and real-world execution. **Non-Production Use only.**

MCC introduces a formal decision boundary that evaluates whether an action proposed by an AI system should be executed, modified, or denied.

This repository contains a minimal reference implementation (PoC) of the MCC pattern and serves as a public prior art record of this control-layer architecture.

## What This Is

- A **reference implementation** of the MCC control layer
- A **prior art publication** of the control-boundary pattern
- A **foundation for enterprise-grade control systems**

## What This Is Not

- Not a full production system
- Not a plug-and-play safety solution
- Not a replacement for governance, policy, or compliance layers

## Quick Start (Conceptual)

MCC sits between intent and execution.

Example flow:

1. AI system generates an action
   - `send_payment`, amount: `50000`

2. MCC evaluates the request against policy
   - checks limits, recipient, context

3. Decision
   - **ALLOW** → execution proceeds
   - **DENY** → execution is blocked

Minimal example:

```json
{
  "intent": "send_payment",
  "amount": 50000,
  "recipient": "external_vendor"
}
```

Result:

```text
DENY
reason: amount exceeds policy threshold
```

No external action is executed.

## Licensing, Commercial Use, Canon & Authorship Record

This repository is published to establish prior art and authorship timeline for the MCC (Meta-Cognitive Control) pattern — a control layer between AI-generated intent and real-world execution.

The code provided here is a minimal reference implementation (PoC) intended for research, evaluation, and architectural demonstration purposes only.
It is not a complete production system and is provided without guarantees.

### License (PoC Code)

Use of the code in this repository is governed by the **MCC Evaluation License 1.0**.

In summary:

- The code may be used, modified, and tested for **Non-Production Use only**
- **Production Use is not permitted** under this license and requires a separate commercial agreement

For full terms, see:
- [`LICENSE`](./LICENSE)
- https://github.com/mcc-prior-art/mcc-policy-engine/blob/main/LICENSE

### Commercial Use

Production deployment, enterprise usage, or integration of MCC-style control systems is available under separate commercial terms.

This typically includes controlled access to the MCC Canon specifications:

- **Canon-1 — Core Principles & Control Model**
- **Canon-2 — Validation & Operational Protocol**
- **Canon-3 — Governance & Control Architecture**

Additional scope:

- Production-grade policy design
- Audit, governance, and safety guarantees
- Integration and certification support

For commercial licensing and enterprise use, contact:
**mcc.prior.art.2026@proton.me**

Early enterprise partnerships and pilot integrations are currently open.

### Proof of Prior Art (Private Materials)

The following hashes attest to the existence of private Canon materials at the time of publication:

- Canon-2 SHA-256: `PASTE_REAL_HASH`
- Canon-3 SHA-256: `PASTE_REAL_HASH`

These materials are not public and may be verified upon request by matching the hash against the original documents.

### Timestamp & Authorship Record

Git commit (HEAD at time of publication):
`PASTE_COMMIT_HASH_HERE`

Commit date (UTC):
`PASTE_REAL_COMMIT_DATE`

Wayback snapshot:
https://web.archive.org/web/PASTE_TIMESTAMP/https://github.com/mcc-prior-art/mcc-policy-engine

These records provide verifiable evidence of public availability and authorship timeline at the time of publication.

### References & Context

The MCC (Meta-Cognitive Control) pattern builds on and formalizes concepts related to:

- AI system safety and alignment
- Policy enforcement layers in distributed systems
- Decision boundaries between intent generation and action execution
- Auditability and control in real-world AI deployments

Relevant context includes:

- LLM-based agent architectures and tool execution frameworks
- Safety and alignment research in modern AI systems
- Policy engines and rule-based enforcement systems in software infrastructure

MCC extends these directions by introducing a formal control boundary between AI-generated intent and real-world execution, with explicit validation, governance, and audit layers.

This repository represents an early public formalization of this control pattern as a distinct architectural layer.

### Notice

This repository documents a control architecture pattern.

Public availability of this PoC does not grant rights to proprietary extensions, private Canon materials, or production implementations.

All rights not expressly granted are reserved.
