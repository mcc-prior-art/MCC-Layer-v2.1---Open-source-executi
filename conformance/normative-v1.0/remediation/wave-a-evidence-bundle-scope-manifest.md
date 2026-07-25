# Wave A Scope Manifest — Evidence Bundle Structure & Hash Reference

Machine-readable form: [`wave-a-evidence-bundle-scope-manifest.json`](./wave-a-evidence-bundle-scope-manifest.json).
Deterministic evidence backing every selected requirement:
[`wave-a-evidence.json`](./wave-a-evidence.json) (regenerate with
`PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_a_evidence.py`).

## Objective

Align `src/mcc_evidence/` with the exact structural and integrity
requirements of MCC-EB-001, and implement the structured Hash Reference
MCC-CM-001 requires as a reusable integrity primitive — extending the
existing package, not creating a second Evidence Bundle subsystem.

## Selected requirement IDs (13, all promoted CONFORMANT)

| ID | Obligation (summary) | Source |
|---|---|---|
| `EB-STR-001` | Exactly one Bundle Root | §10.1 / §10.5 |
| `EB-STR-002` | Root contains exactly one Descriptor/Integrity/Provenance/Evidence-Dir | §10.2 / §10.5 |
| `EB-STR-003` | Deterministic structure for equivalent input | §10.5 |
| `EB-STR-004` | Stable naming across regeneration | §10.4 / §10.5 |
| `EB-STR-005` | Directory and archive forms structurally equivalent | §9.2 / §10.5 |
| `EB-FILE-001` | Bundle Descriptor present, declares required fields | §11.1 / §11.5 |
| `EB-FILE-002` | Integrity Record present | §11.2 / §11.5 |
| `EB-FILE-003` | Provenance Record present, declares origin | §11.3 / §11.5 |
| `EB-FILE-004` | Every non-Integrity-Record file enumerated | §11.2 / §13.4 / §11.5 |
| `EB-FILE-005` | Required files never omitted | §11.5 |
| `CM-HASH-001` | Hash Reference identifies Digest + algorithm + content | §13.2 / §13.5 |
| `CM-HASH-002` | Algorithm must be collision-resistant | §13.3 / §13.5 |
| `CM-HASH-004` | Independently recomputable/verifiable | §13.4 / §13.5 |

Full per-requirement detail (exact obligation, source span, reused
implementation, production change, positive/negative tests, evidence
pointer, dependencies, files affected) is in the JSON manifest.

## Excluded candidate: `CM-HASH-003`

**"Every Evidence Bundle Reference MUST include at least one Hash
Reference."** This obligation is on the *Evidence Bundle Reference*, a
structured field of the Certification Manifest defined by MCC-CM-001
§14 (`CM-EBREF-001..004`, all currently `GAP`). No Evidence Bundle
Reference object exists in this repository — there is nothing to attach a
Hash Reference to, and no honest test can exercise this requirement without
first building that object, which is explicitly Wave B's scope (PR #64).
`HashReference` itself is fully implemented and `CONFORMANT` in this wave
(`CM-HASH-001/002/004`) specifically so Wave B can attach it to the
Evidence Bundle Reference without re-implementing it. Promoting `CM-HASH-003`
now would require either fabricating a fictitious Evidence Bundle Reference
solely to claim conformance, or claiming conformance for an object that
doesn't exist — both excluded by this PR's constraints.

## No additional requirement IDs were pulled in

All 14 originally-listed candidates were verified against the corrected
810-requirement baseline before any code was written; all 14 exist with
materially matching normative meaning. 13 were selected, 1 excluded (above).
No requirement outside this list was added as a dependency.

## Global status delta

| Metric | Before | After |
|---|---|---|
| `CONFORMANT` | 0 | **13** |
| `PARTIAL` | 606 | 593 |
| `GAP` | 114 | 114 |
| `NOT_APPLICABLE` | 90 | 90 |
| Total | 810 | 810 |

No transition occurred outside the 13 selected IDs — verified directly
against every other requirement sharing the same three categories
("10. Bundle Directory Structure", "11. Required Files", "13. Hash
References"), all of which remain at their pre-existing status.

## Explicitly not implemented in this PR

- MCC-CM-001 Evidence Bundle Reference (`CM-EBREF-001..004`) — Wave B.
- MCC-TC-001 Technical Certificate model, signature, trust, validity,
  revocation — Wave C.
- The executable MCC Normative v1.0 Certification Suite.
- Adapter certification against these four specifications.
- `MCC-RG-001` / Integration Contract normative integration.
- Any change to runtime Decision Token / Execution Gate / Policy Bundle /
  Canonical Ingress Pipeline / nonce / audit-chain / adapter-authorization
  behavior.
