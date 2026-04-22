COMMIT=$(git rev-parse HEAD)
CANON2=$(sha256sum canon-2.pdf | cut -d' ' -f1)
CANON3=$(sha256sum canon-3.pdf | cut -d' ' -f1)

cat > README.md << 'EOF'
# MCC (Meta-Cognitive Control)

A control layer between AI-generated intent and real-world execution.  
**Non-Production Use only.**

MCC introduces a formal decision boundary between **intent generation** (LLMs, agents) and **execution authority** (systems, APIs, workflows).

Instead of trusting AI outputs, MCC enforces a single invariant:

> **Execution requires a decision.**

---

## Why This Matters

AI systems can generate actions.  
They cannot reliably decide whether those actions should be executed.

As soon as systems:

- call APIs  
- move money  
- trigger workflows  
- control external systems  

the absence of a control boundary becomes a **systemic risk**.

MCC defines that boundary.

---

## Core Architecture

AI Model → Intent → MCC → Decision → Execution (or Denial)

- AI proposes an action  
- MCC evaluates it against policy  
- Only approved actions are executed  

MCC acts as a **hard execution gate** between AI and the real world.

---

## Example

Input (AI-generated intent):

    {
      "intent": "send_payment",
      "amount": 50000,
      "recipient": "external_vendor"
    }

MCC decision:

    DENY
    reason: amount exceeds policy threshold

Result:

- No API call  
- No execution  
- System remains safe  

---

## Minimal Integration Pattern

    def mcc_evaluate(request):
        if request["intent"] == "send_payment" and request["amount"] > 10000:
            return "DENY"
        return "ALLOW"

    decision = mcc_evaluate({
        "intent": "send_payment",
        "amount": 50000,
        "recipient": "external_vendor"
    })

    if decision == "ALLOW":
        execute_payment()
    else:
        block_execution()

MCC enforces strict separation:

- AI → proposes  
- MCC → decides  
- System → executes  

---

## Reference Implementation

This repository provides a minimal PoC demonstrating:

- deny-by-default execution model  
- structured intent validation  
- policy-based decision logic  
- strict separation of intent and execution  

Intended for:

- research  
- evaluation  
- architectural understanding  

---

## Where MCC Fits

MCC applies wherever AI systems can act:

- AI agents with tool execution  
- financial / transactional systems  
- API-driven automation  
- robotics and real-world control systems  
- enterprise AI governance layers  

---

## Proof of Existence

Canonical materials are hashed to establish timestamped existence.

- Canon-2 SHA-256: __CANON2__  
- Canon-3 SHA-256: __CANON3__  

These hashes correspond to privately held canonical documents not included in this repository.

---

## Authorship Record

Git commit (HEAD):  
__COMMIT__  

Commit date (UTC):  
2026-04-22T16:14:12Z  

Wayback snapshot:  
https://web.archive.org/web/20260422161412/https://github.com/mcc-prior-art/mcc-policy-engine  

---

## Prior Art

This repository establishes public prior art for:

- the MCC control-layer pattern  
- fail-closed execution gating  
- separation of intent and execution authority  

Private Canon materials are not included.

---

## Licensing

Use of this repository is governed by the MCC Evaluation License 1.0.

- Non-Production Use only  
- Production use requires a separate commercial agreement  

Full license:

- LICENSE file in this repository  
- https://github.com/mcc-prior-art/mcc-policy-engine/blob/main/LICENSE  

---

## Commercial Use

Production deployment and enterprise integration are available under separate terms.

Includes:

- access to MCC Canon specifications (Canon-1, Canon-2, Canon-3)  
- production-grade policy design  
- governance, audit, and safety guarantees  
- integration and certification support  

Contact:  
mcc.prior.art.2026@proton.me  

---

## Context

MCC builds on:

- AI safety and alignment  
- policy enforcement systems  
- agent execution frameworks  
- distributed system governance  

It formalizes a missing layer:

> a control boundary between AI-generated intent and real-world execution.

---

## Notice

This repository documents a control architecture pattern.

Public availability does not grant rights to:

- proprietary extensions  
- private Canon materials  
- production implementations  

All rights not expressly granted are reserved.
EOF

sed -i '' "s|__COMMIT__|$COMMIT|g" README.md
sed -i '' "s|__CANON2__|$CANON2|g" README.md
sed -i '' "s|__CANON3__|$CANON3|g" README.md

git add README.md
git commit -m "docs: add cryptographic timestamps"
git push

echo "Done. Verify: https://web.archive.org/web/20260422161412/https://github.com/mcc-prior-art/mcc-policy-engine"
