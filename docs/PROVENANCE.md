# MCC-Core Project Provenance

MCC-Core is an independently developed project by Alexandr Ponomariov / AXLOGIQ. This document records the verifiable technical chronology of its architecture and implementation using dated repository evidence, including commits, specifications, pull requests, tests, assurance artifacts, and public technical records.

The purpose of this record is provenance and reproducibility: each material milestone should be independently traceable to its underlying artifact.

**Verified against:** `mcc-prior-art/mcc-layer`, `main` at commit [`a807304`](https://github.com/mcc-prior-art/mcc-layer/commit/a807304f028dd165d4854cd26b559b69d43507b8) (PR #107 merge commit). All PR numbers, commit SHAs, and dates below were independently checked against the GitHub API and local `git log` at the time this document was written, rather than copied from prior summaries.

---

## Provenance chain

```
Idea → Design → Implementation → Verification → Adversarial Validation → Governed Execution
```

Where supported by repository evidence:

> Intelligence can propose.
> Authority must verify.
> Execution must enforce.
>
> Proposal ≠ Permission.

---

## Evidence rule

Every material milestone below cites a real, checkable artifact — a pull request number, a commit SHA, or a specific file. Where an exact date or origin could not be established from repository evidence, that is stated explicitly rather than inferred. Dates asserted only by a document's own prose (not corroborated by a git commit timestamp or an independent, externally-timestamped source such as an archive service) are marked as such.

---

## 1. Origin / early project record

The repository's history contains several distinct kinds of "earliest evidence," and they must not be collapsed into one date. §1.1 below is given first and in the most detail, because it is the repository's own earliest disclosed-date record.

### 1.1 The Prior Art Archive record (`docs/exhibits/Prior_Art_Archive_2026-04.md`)

This repository file is a self-described "Defensive publication / prior-art evidence" record, currently present at `docs/exhibits/Prior_Art_Archive_2026-04.md` (protected under `CLAUDE.md`; read but not modified by this document). It asserts three internal dates and cites two external artifacts:

- **First disclosure: 20.04.2026** — a date claimed by the archived post's own text, per the exhibit's "Archived Record" section.
- **Archive date / spec expanded: 21.04.2026** — the exhibit's own self-declared header date, and the date it says the archived post's content was expanded.
- Archived page: `archive.ph/2026.04.21-195051/https://telegra.ph/MCC-v05--GPT-41-Features-21042026-04-21`, titled "MCC v0.5 + GPT-4.1 Features 21.04.2026."
- Original X post: `x.com/axlogiq_ai/status/2046674474452357490`, stated as posted 22:35 on 21.04.2026.
- Content described: "intent → policy → allow / deny / escalate, real-time policy patching, multi-agent consensus, hash-chain audit trail" — an early description of MCC execution-control architecture.

**Three distinct dates must not be collapsed into one, and this document keeps them separate:**

| # | Date | What it actually measures | Who controls that timestamp | Independently confirmed by this document? |
|---|---|---|---|---|
| 1 | 20.04.2026 | Claimed date of original public disclosure | The archived post's own text (self-reported by its author) | **No** — one step removed from any external timestamp; only as strong as the archived post's own claim |
| 2 | 21.04.2026, 19:50:51 UTC (per the `archive.ph` URL) | The external archiving service's snapshot timestamp | `archive.ph`, a third party independent of the repository owner | **Not by direct inspection** — see verification attempt below; the timestamp is embedded in `archive.ph`'s own URL convention, which this document treats as the service's claim, not as something this session rendered and read for itself |
| 3 | First git-observable **2026-07-25** (this exhibit file's earliest reachable commit); file's own internal "Archive date" header says 21.04.2026 | When this evidence *file* (not the event it describes) entered this repository's git history | This repository / GitHub | **Yes, for the git side** — confirmed by direct `git log` inspection (below); the file's own internal date is content-asserted, not git-timestamped, exactly like the doctrine files in §1.5 |

**Verification performed for this document:**

1. **The repository file and its git history** — confirmed directly:
   ```
   $ git log --all --follow --diff-filter=A --format="%H|%ad|%s" --date=short -- docs/exhibits/Prior_Art_Archive_2026-04.md
   abf3af9|2026-07-25|docs(review): Final Normative Acceptance Review — MCC Specification Program v1.0
   7a2c69f|2026-07-25|Merge pull request #57 from mcc-prior-art/fix/cp-001-define-conformance-result-and-report
   ```
   The file is already present, unchanged in content, at the repository's earliest locally-reachable commit (`7a2c69f`, §1.3 below) — the same parentless root commit that already contains the full accumulated tree through PR #57. No earlier commit for this specific file exists in the local git object graph, for the same structural reason given in §1.3: individual commits predating that squash point are not locally reachable at all. This means the file's presence is git-verifiable no earlier than 2026-07-25 — over three months after the 20–21 April 2026 dates it asserts internally.
2. **The external archived-page timestamp, where accessible** — this session attempted `WebFetch` on `https://archive.ph/2026.04.21-195051/https://telegra.ph/MCC-v05--GPT-41-Features-21042026-04-21` and on the underlying `https://telegra.ph/MCC-v05--GPT-41-Features-21042026-04-21` directly. Both attempts failed: `archive.ph` is refused by the fetch tool outright, and `telegra.ph` is blocked by this session's network egress policy (`EGRESS_BLOCKED`). A web search for the post's title alongside "telegra.ph" and "archive.ph" returned no matching results. **This document cannot independently confirm the rendered content or timestamp of either page from within this session** — only that the exhibit cites a specific, checkable URL whose own path format asserts a snapshot timestamp, which a party with unrestricted network access could verify directly.
3. **The original X URL, where accessible** — this session attempted `WebFetch` on `https://x.com/axlogiq_ai/status/2046674474452357490` directly. The attempt failed: `x.com` is blocked by this session's network egress policy (`EGRESS_BLOCKED`). A web search for the account name alongside MCC/ALLOW/DENY/Grok terms returned no matching results (X post content is generally not search-indexed, and this specific account is separately documented — §1.4 — as having been locked by the platform in the same period). **This document cannot independently confirm the original X post from within this session.**

**What this document therefore claims, precisely:** the *file* `docs/exhibits/Prior_Art_Archive_2026-04.md`, and the specific external URLs it cites, are real, checkable, present-tense artifacts of this repository, first git-observable on 2026-07-25. The *events* those citations describe (a disclosure on 20.04.2026, an archive snapshot on 21.04.2026, an X post at 22:35 on 21.04.2026) are exactly as credible as the cited external services' own record-keeping — which this session was not able to independently render and inspect — and no more. This document does not treat the 20/21 April dates as proven by the exhibit's presence in the repository; it treats them as claims the repository makes, citing sources a reader with different network access could check directly. No claim of legal priority is made on this basis (§15).

### 1.2 Earliest evidence reachable through the GitHub API

The earliest pull request on `mcc-prior-art/mcc-layer` is **[PR #1 — "add Grok acknowledgment proof"](https://github.com/mcc-prior-art/mcc-layer/pull/1)**, created and merged **2026-04-25T22:04–22:05 UTC** (GitHub-controlled timestamps). Its one-file diff renames `screenshot.png` to `proof/screenshot.png`. That image — still present in the repository at `proof/screenshot.png` — is a screenshot of a public X (Twitter) exchange in which the `@grok` (xAI) account replies to the `@axlogiq_ai` account's description of an "MCC layer" with ALLOW/DENY/ESCALATE semantics, fail-closed behavior, audit, and rollback, and a link to the `mcc-prior-art` GitHub repository. The card at the bottom of that exchange reads "MCC — MODEL CONTEXT CONTROL," an earlier public expansion of the "MCC" name than the "Meta-Cognitive Control (Core)" expansion used later.

This is the earliest artifact whose existence in this specific repository carries an independent, GitHub-controlled timestamp.

### 1.3 Earliest evidence reachable through local `git log`

The local git history of the default branch, as currently observable via `git log`, does **not** extend back to PR #1. Its earliest commit is a single, parentless (root) commit:

```
7a2c69f6c9f0a87a59c53a0dbd970ba5a7cab31f  2026-07-25  Merge pull request #57 from mcc-prior-art/fix/cp-001-define-conformance-result-and-report
```

This commit has no parent and already contains the full accumulated repository tree as of PR #57 (workflows, `CLAUDE.md`, doctrine files, `README.md` at 1,721 lines, `docs/exhibits/`, etc.). Individual commits for PRs #1 through #56 are **not present** in the current local git object graph — the repository's commit history was consolidated into this one root commit at or before that point. GitHub's PR API independently retains the metadata (title, author, created/merged timestamps) for PRs #1–56 even though their individual commits are not locally reachable; this document treats those API-reported timestamps as GitHub-controlled evidence distinct from, and less strong than, a directly reachable git commit.

**Practical consequence:** for PRs #1–56 and PRs #48–#55 (all pre-dating or contemporaneous with the squash point), this document cites PR number and GitHub's `created_at`/`merged_at` timestamps, and explicitly notes that no local commit SHA is available. From PR #57 onward, local commit SHAs exist — either as ordinary two-parent merge commits, or, for PRs #89 through #98, as single-parent squash-merge commits (each with a `(#NN)` suffix in its subject line) — and this document cites those SHAs directly.

### 1.4 Corroborating public/external evidence — the X account-lock exhibit

A second exhibit document, `docs/exhibits/X_Ban_Event_2026-04.md` (also present at least as of the 2026-07-25 root commit, protected, read but not modified here), is marked "Filed: June 2026" and asserts a timeline of a first public disclosure (20.04.2026, matching §1.1's archive record), a platform account action (23.04.2026), the Grok/xAI public response corroborated by PR #1's screenshot (25.04.2026, §1.2), and an X Support appeal response (29.04.2026). Only the 25.04.2026 entry is independently corroborated by a GitHub-timestamped artifact (PR #1, §1.2). The 23.04.2026 and 29.04.2026 entries rest on the exhibit's own retrospective account and an appeal-response screenshot (`X_Appeal_Response_2026-04-29.png`) whose filename asserts a date; **this document does not independently verify those dates beyond what the exhibit itself already discloses**.

### 1.5 Earliest formal doctrine record

The three root-level doctrine documents — `MCC-Core_Decision_Boundary_Doctrine_2026-06-02.md`, `MCC-Core_Doctrine_Lines_v1_0_2026-06-02.md`, `MCC-Core_Non-Post-Execution_Principle_2026-06-02.md` — carry a self-declared date of **2026-06-02** in their filenames (no separate "Date:" field in the document body). They are first git-verifiable at the same 2026-07-25 root commit as everything else in §1.3; their 2026-06-02 date is therefore a content-asserted date, not an independently git-timestamped one. `README.md`'s `Doctrine record:` metadata field has carried this same `2026-06-02` date since at least the earliest locally observable README revision.

### 1.6 Earliest terminology

The earliest available materials use **"MCC — Model Context Control"** (PR #1 screenshot) and, in `docs/exhibits/README.md`, **"MCC — Meta-Cognitive Control"** ("Architect of MCC — Meta-Cognitive Control"). The current top-level README canonical definition (added in PR #107) uses **"Meta-Cognitive Control Core."** The repository does not contain a dated document explaining the exact transition between these three expansions; this document records the terminology as found rather than inferring an origin story for the change.

### 1.7 Private design records (disclosed, not used as evidence)

The author has stated that private design notes predating the public record in §1.1–§1.4 exist and are preserved separately from this repository. As identified for this task, visible records include, among others:

- "MCC-CANON v.1" — 15.01.2026
- "MCC Reference Architecture v0.1" — 15.01.2026
- "CANON-2 Validation / Operational Protocol" — 17.01.2026
- "CANON III — Meta-Cognitive Governance Reference Architecture" — 02.04.2026

The author has also preserved a private design record titled **"MCC Reference Architecture v0.1,"** displaying the date **15.01.2026**. The material describes MCC as a control layer external to the cognitive/model layer, with policy/control functions governing action before execution and an execution-side gate rather than embedding authority inside the model. This private record is relevant to the documented design lineage because the same separation later appears in public and repository-backed MCC architecture: intelligence/model output is treated as a proposal, while authority verification and execution enforcement remain outside the model. **The 15.01.2026 date is not independently verified** — it is presented here exactly as classified above, as a PRIVATE DESIGN RECORD, not as a PUBLIC DISCLOSURE or REPOSITORY EVIDENCE date, and it is not converted into a public priority claim.

None of these records, or their content, are reproduced in this repository or this document beyond the minimal architectural characterization above — only their titles and stated dates, as disclosed for this task. This document:

- does **not** treat their stated dates as independently git-verifiable, archive-timestamped, or otherwise externally corroborated. They have no public artifact, timestamp service, or commit associated with them that this document (or any third party) could inspect, so they fall outside what the "Evidence rule" above can check;
- does **not** copy their content into this public repository;
- does **not** use them as the sole or primary basis for any public priority claim, here or elsewhere.

**Three categories, kept distinct throughout this document:**

| Category | What it means | Example in this document | Independently checkable by a third party? |
|---|---|---|---|
| **PRIVATE DESIGN RECORD** | Notes/drafts held privately by the author, never published or independently timestamped | The four titles above | **No** — existence and dates rest solely on the author's own record-keeping; not verified here |
| **PUBLIC DISCLOSURE** | Content made publicly visible at some point (a post, an archived page), whether or not independently re-renderable today | §1.1 (Prior Art Archive / archive.ph / X post), §1.2 (PR #1 / Grok exchange) | **Sometimes** — depends on whether an independent party's timestamp or archive exists and remains accessible; §1.1–§1.2 record exactly what could and could not be re-confirmed |
| **REPOSITORY EVIDENCE** | An artifact present in, and directly inspectable within, this git repository | Any commit SHA, PR number, or file cited elsewhere in this document | **Yes** — by construction; this is what every verified claim elsewhere in this document is restricted to |

The verified public chronology in this document (§1.1 onward, and every date-ordered table, including §12) is built only from public disclosure and repository evidence. Private design records are disclosed here, at the author's request, for completeness — they are not dated milestones in §12's chronology table, and no claim in this document depends on them being true.

---

## Public technical record

This section separates three distinct evidence classes for the April 2026 period, per the evidence-classification rule applied throughout this document:

- **Contemporaneous evidence** — an artifact independently timestamped at (or very near) the time of the event itself, by a party other than the repository owner (GitHub's PR API, an external archiving service).
- **Repository evidence** — an artifact present in this repository, checkable directly, but whose own internal date claim may or may not be independently corroborated.
- **Retrospective public record** — a later account of earlier events, written after the fact, offered as context but not as proof of the earlier date.

A LinkedIn article by Alexandr Ponomariov / AXLOGIQ was identified for this task as a retrospective account describing early MCC development and quoting architectural statements ("Execution capability is not execution authority," "Proposal ≠ Permission," "No verified authority. No execution," "Fail-closed by design"), and referencing the same 25 Apr 2026 X/Grok interaction documented in §1.2. Per the evidence rule applied throughout this document, **this article is not used as proof that the 25 Apr 2026 event occurred** — that date is instead supported independently, below, by a GitHub-API-timestamped repository artifact (PR #1) and direct inspection of its content.

This session attempted to independently locate the article using web search (multiple queries combining the author's name, "AXLOGIQ," "MCC," "MCC-Core," the quoted architectural statements, and the `axlogiq.ai`/`axlogiq.org`/`axlogiq.com` domains named in `docs/exhibits/README.md`) and could not locate a fetchable URL for it. A direct fetch of the underlying X post (`x.com/axlogiq_ai/status/2046674474452357490`, cited in `docs/exhibits/Prior_Art_Archive_2026-04.md`) was also attempted and blocked by this session's own network egress policy (`x.com` is not reachable from this environment), and a direct fetch of the `archive.ph` snapshot cited in the same exhibit was attempted and failed (the fetch tool could not retrieve `archive.ph` content). None of these attempts changes the verification status already established from the repository's own GitHub-API-checkable evidence (PR #1) in §1.2; they simply could not add independent corroboration beyond what the repository already provides, in the time available to this session.

| Date | Evidence type | Artifact | Claim supported | Verification status |
|---|---|---|---|---|
| 20.04.2026 | Retrospective (text claim inside an archived post) — full detail in §1.1 | `docs/exhibits/Prior_Art_Archive_2026-04.md`, citing the archived Telegra.ph post's own "First disclosure" field | First public MCC disclosure | Not independently verified — the date is asserted by text inside the archived post itself, one step removed from the archive's own timestamp; this session could not fetch the archive to inspect it directly |
| 21.04.2026, 22:35 | External, claimed timestamp — full detail in §1.1 | `archive.ph/2026.04.21-195051/...` snapshot of a Telegra.ph post ("MCC v0.5 + GPT-4.1 Features 21.04.2026"), X post `x.com/axlogiq_ai/status/2046674474452357490`, cited in `docs/exhibits/Prior_Art_Archive_2026-04.md` | Early MCC execution-control architecture (intent → policy → allow/deny/escalate, real-time policy patching, multi-agent consensus, hash-chain audit) publicly described before the June 2026 doctrine formalization | Not independently confirmed by direct inspection — the `archive.ph` URL's own path format encodes a snapshot timestamp (`2026.04.21-19:50:51`) as that service's own claim, but this session's fetch attempts against both `archive.ph` and `telegra.ph` failed (tool-refused / egress-blocked); repository-cited, not independently re-fetched here |
| 23.04.2026 | Retrospective (repository exhibit, filed June 2026) | `docs/exhibits/X_Ban_Event_2026-04.md` | `@axlogiq_ai` account locked by X platform systems | Not independently verified — rests on the exhibit's own account; no external corroboration located by this session |
| **25.04.2026** | **Contemporaneous (GitHub-API-timestamped) + repository evidence, directly inspected** | **[PR #1](https://github.com/mcc-prior-art/mcc-layer/pull/1)** (created/merged 2026-04-25T22:04–22:05 UTC) → `proof/screenshot.png` | Public X exchange: `@axlogiq_ai` describes an MCC layer with ALLOW/DENY/ESCALATE mode, fail-closed behavior, audit, and rollback; `@grok` (xAI) responds publicly, acknowledging the approach | **Verified** — GitHub's own PR-API timestamp is independent of the repository owner, and this session directly viewed the image content (not merely its filename) to confirm the claim it supports |
| 29.04.2026 | Repository evidence (image artifact) + retrospective narrative | `docs/exhibits/X_Appeal_Response_2026-04-29.png`, cited in `docs/exhibits/X_Ban_Event_2026-04.md` | X Support appeal response stated automated systems determined a rule violation occurred and declined to overturn the account action | Partially verified — the image is present in the repository (first git-observable at the same 2026-07-25 root commit as all other pre-#57 content, per §1.3); the 29.04.2026 date comes from the filename and the exhibit's own account, not from an independently re-checked source |
| Not established | Retrospective public record (this task's source material) | LinkedIn article by Alexandr Ponomariov / AXLOGIQ (no URL located) | Restates that MCC was already under execution-governance development by 25.04.2026; quotes "Execution capability is not execution authority," "Proposal ≠ Permission," "No verified authority. No execution," "Fail-closed by design" | **Not independently verified** — could not be located via web search in this session; not used to support any date claim in this document. The 25.04.2026 claim it restates is independently supported above by PR #1, without relying on this article. |

This document does not claim priority over any other party on the basis of any row above; it records what could and could not be independently checked, and by what means.

---

## 2. Core authority architecture

Repository-backed emergence of the core MCC-Core authority concepts (all PR numbers per §1.3's sourcing rule — #7 onward have local commit SHAs; #2–#6 are PR-API-only):

| Concept | First repository evidence |
|---|---|
| Signed decision tokens (Ed25519) | [PR #2](https://github.com/mcc-prior-art/mcc-layer/pull/2) — "Runtime: add signed MCC decision tokens and CI safety gates" (2026-06-11) |
| Decision authority / policy evaluation | [PR #7](https://github.com/mcc-prior-art/mcc-layer/pull/7) — "MVP: authority model + gateway service + egress-proxy enforcement" (2026-06-22) |
| Replay / nonce protection | [PR #8](https://github.com/mcc-prior-art/mcc-layer/pull/8) — "production RedisNonceRegistry for multi-instance replay protection" (2026-06-22) |
| Action/payload binding, idempotency, velocity limits | [PR #9](https://github.com/mcc-prior-art/mcc-layer/pull/9) — "transaction binding, business-operation idempotency, and atomic velocity controls" (2026-06-23) |
| Signed, revocable mandates; ESCALATE state machine; scope verification | [PR #10](https://github.com/mcc-prior-art/mcc-layer/pull/10) — "signed mandates, ESCALATE loop, non-payment profile" (2026-06-23) |
| Multi-issuer trust / identity verification over HTTP | [PR #11](https://github.com/mcc-prior-art/mcc-layer/pull/11) (2026-06-23) |
| Multi-Context Consensus (N-of-M signed evaluator votes) | [PR #13](https://github.com/mcc-prior-art/mcc-layer/pull/13) — "Multi-Context Consensus 3/3" (2026-06-23) |
| Consensus made mandatory in the execution path (fail-closed) | [PR #15](https://github.com/mcc-prior-art/mcc-layer/pull/15) (2026-06-24) |
| Gateway-issued one-time consensus challenge nonce | [PR #16](https://github.com/mcc-prior-art/mcc-layer/pull/16) (2026-06-24) |
| Controlled execution boundary (governed outbound HTTP egress) | [PR #25](https://github.com/mcc-prior-art/mcc-layer/pull/25) — "Enforced Outbound HTTP Egress Proxy" (2026-06-27) |
| Full governance stack wired into the public `/evaluate` entrypoint | [PR #19](https://github.com/mcc-prior-art/mcc-layer/pull/19) (2026-06-25); recorded contemporaneously in `RUNTIME_VALIDATION_RECORD.md` (branch `feat/wire-runtime-v1.11.0`, dated 2026-06-25) |
| Audit-before-actuation, fail-closed enforcement ordering (a–h) | `src/mcc_core/coordinator.py` (`EnforcementCoordinator`); current docstring documents the exact a–h order (gate → nonce → idempotency admission → velocity reservation → **audit-before-actuation** → dispatch-ownership commit → execute → outcome record) |

`Proposal ≠ Permission` as an explicit, repeated phrase is first visible in this repository's currently-tracked documents in the Phase 1/Phase 2 Universal Proposal Service design docs (§9) and is restated in the README canonical definition added by PR #107 (§10).

---

## 3. Protocol / specification development

Four normative specification documents exist under `specs/`, introduced as a baseline and then brought to a declared Normative v1.0 state:

| Spec | Title | Introduced |
|---|---|---|
| `specs/MCC-CP-001.md` | Official Certification Program Specification | [PR #56](https://github.com/mcc-prior-art/mcc-layer/pull/56) — "MCC Specification Program — Initial Four-Specification Baseline" (2026-07-25) |
| `specs/MCC-EB-001.md` | Evidence Bundle Specification | PR #56 |
| `specs/MCC-CM-001.md` | Certification Manifest Specification | PR #56 |
| `specs/MCC-TC-001.md` | Technical Certificate Specification | PR #56 |

Each is currently marked `Version: 1.0`, `Status: Normative`. Their conformance/remediation history is git-verifiable from PR #57 onward (local commit SHAs, chronological):

- PR #57 `7a2c69f` — MCC-CP-001: define Certification Result/Report outputs
- PR #58 `7c19c30` — Final Normative Acceptance Review, MCC Specification Program v1.0
- PR #59 `a65b2f3` — Normative v1.0 Declaration
- PR #60 `ef95b13` — Implementation Conformance Baseline
- PR #61 `b38b509` — Conformance Wave 1: Execution Boundary Methodology
- PR #62 `b6c34fa` — Conformance Extraction Coverage Correction
- PR #63 `b490274` — Conformance Remediation Wave A (Evidence Bundle)
- PR #64 `5c1ba2b` — Conformance Remediation Wave B (Certification Manifest)
- PR #65 `732e3f9` — Conformance Remediation Wave C (Technical Certificate)
- PR #66 `eee792b` — Certification Program Completion Audit & Coverage Reconciliation
- PR #67 `c5dfef9` — End-to-End Certification Pipeline
- PR #68 `467836c` — Certification Trust Anchor, Issuer Key Management & Publication Foundation
- PR #69 `f82eb2a` — Official Certification of the Five Reference Ecosystems
- PR #70 `e86234f` — MCC Official Certification Release & Production Signing Ceremony

A second, later specification series — `specs/MCC-AT-001.md` through `MCC-AT-004.md` (Attestation) — was introduced alongside the pre-execution attestation work (§6/§9 below, PRs #90–96).

---

## 4. Framework-neutral / interoperability development

Real (not simulated) framework integrations, each behind the same canonical ingress boundary, with local commit SHAs from PR #48 onward:

| Adapter | PR | Commit |
|---|---|---|
| Multi-adapter interoperability foundation + generic HTTP proof (48a) | [PR #48](https://github.com/mcc-prior-art/mcc-layer/pull/48) (2026-07-21) | — (pre-#57, no local SHA) |
| LangGraph (48b, 2/5) | [PR #49](https://github.com/mcc-prior-art/mcc-layer/pull/49) (2026-07-21) | — |
| AutoGen (48c, 3/5) | [PR #50](https://github.com/mcc-prior-art/mcc-layer/pull/50) (2026-07-21) | — |
| CrewAI (48d, 4/5) | [PR #51](https://github.com/mcc-prior-art/mcc-layer/pull/51) (2026-07-22) | — |
| VoltAgent (48e, 5/5 — "matrix complete") | [PR #52](https://github.com/mcc-prior-art/mcc-layer/pull/52) (2026-07-22) | — |
| Canonical Governance Protocol & Canonical Ingress Pipeline | [PR #53](https://github.com/mcc-prior-art/mcc-layer/pull/53) (titled "PR #49" internally) (2026-07-22) | — |
| Adapter SDK | [PR #54](https://github.com/mcc-prior-art/mcc-layer/pull/54) (titled "PR #50" internally) (2026-07-22) | — |
| Adapter SDK as canonical certification ingress | [PR #55](https://github.com/mcc-prior-art/mcc-layer/pull/55) (titled "PR #51" internally) (2026-07-22) | — |

Note the internal PR title numbering (48a–e, then "PR #49/#50/#51") does not match the GitHub-assigned PR numbers (#48–#55) one-to-one; both numbering schemes are reproduced here as found, without reconciling them, since GitHub's own PR number is the authoritative identifier used elsewhere in this document.

An earlier real third-party integration predates the five-adapter interoperability matrix: **[PR #36](https://github.com/mcc-prior-art/mcc-layer/pull/36) — "Real VoltAgent Governed Integration"** (2026-07-05), the first real (non-generic) framework integration in the repository, later followed by the AXFlow Clinic business pilot on the same integration (PR #38, 2026-07-06).

---

## 5. Assurance development

| Milestone | PR | Commit |
|---|---|---|
| Hermetic black-box assurance foundation (71A) | [PR #71](https://github.com/mcc-prior-art/mcc-layer/pull/71) | `59a1d2a` (2026-08-14) |
| Distributed replay & fault-injection assurance (71B) | [PR #72](https://github.com/mcc-prior-art/mcc-layer/pull/72) | `de54de9` (2026-08-14) |
| Model checking (TLA+) & security mutation testing (71C) | [PR #73](https://github.com/mcc-prior-art/mcc-layer/pull/73) | `545914e` (2026-08-14) |
| External independent runner & final evidence bundle (71D) | [PR #74](https://github.com/mcc-prior-art/mcc-layer/pull/74) | `a7fd5a0` (2026-08-14) |
| Reproducible assurance entry point | [PR #75](https://github.com/mcc-prior-art/mcc-layer/pull/75) | `807ccc7` (2026-08-14) |
| Public verification links / README assurance entry point | [PR #76](https://github.com/mcc-prior-art/mcc-layer/pull/76) | `514a1f7` (2026-08-15) |
| README assurance banner surfaced above the fold | [PR #77](https://github.com/mcc-prior-art/mcc-layer/pull/77) | `935baa0` (2026-08-15) |
| Multi-process audit-chain fork fix (inter-process lock) | [PR #83](https://github.com/mcc-prior-art/mcc-layer/pull/83) | `6b42842` (2026-08-20) |
| Audit-chain crash-recovery hardening (fsync-failure rollback) | [PR #84](https://github.com/mcc-prior-art/mcc-layer/pull/84) | `329fc04` (2026-08-20) |
| External checkpoint anchoring for the audit hash-chain (Scenario G) | [PR #85](https://github.com/mcc-prior-art/mcc-layer/pull/85) | `b079944` (2026-08-20) |

The model-checking and mutation-testing artifacts are concrete, checked-in components, not just PR titles: `model/MCCExecutionStateMachine.tla` and `model/AttestationEvidenceBinding.tla` (with `.cfg` configs and `model/run_tlc.sh`), and the `mutation/` package (`detectors.py`, `harness.py`, `defects.py`, a `python -m mutation` CLI). Negative-control / non-vacuity evidence (a defect deliberately reproduced, then shown to be caught) recurs as a named methodology across later PRs (§6, §9, §11).

---

## 6. Durable execution safety

| Milestone | PR | Commit / doc |
|---|---|---|
| Cumulative velocity limit bypass at window boundaries — fixed | [PR #92](https://github.com/mcc-prior-art/mcc-layer/pull/92) | `1433460` (2026-09-01, squash-merge commit) |
| Durable logical-operation safety (Rounds 17–24) | `docs/DURABLE_OPERATION_SAFETY.md` | Closes a gap identified in GPT-6 Astra's adversarial inspection (Round 16/17) in `EnforcementCoordinator.enforce` and the idempotency registries |
| "Durable safety" hardening (Rounds 26–27) | [PR #103](https://github.com/mcc-prior-art/mcc-layer/pull/103) | `3f44f9f` (2026-09-07) — commit messages on this branch include "Round 27: remove unsafe request_id fallback for logical_operation_id" and "Round 26: behavioral tests proving logical_operation_id propagation" |
| Atomic admission, dispatch ownership, exactly-once/duplicate-safe behavior, `UNKNOWN` preservation | `src/mcc_core/coordinator.py`, `src/mcc_core/idempotency.py` — the `EnforcementCoordinator` a–h order (§2) is the canonical implementation; `IdempotencyRegistry` states include `RESERVED`, `EXECUTED`, `UNKNOWN` ("actuation outcome indeterminate; no TTL recovery") |
| Reconciliation of ambiguous (`UNKNOWN`) outcomes | `gateway/proposal_execution_service.py::reconcile_proposal_operation` (Phase 2, §9) |

---

## 7. Tenant isolation

**[PR #105 — "Tenant-scoped durable execution identity"](https://github.com/mcc-prior-art/mcc-layer/pull/105)**, merge commit [`8b5651a`](https://github.com/mcc-prior-art/mcc-layer/commit/8b5651a98972aa33afccbcf3c46a9950bd62de99) (2026-09-08), is the primary milestone: it scopes durable execution identity to the composite key `(tenant_id, logical_operation_id)` rather than `logical_operation_id` alone.

Per `docs/TENANT_SCOPED_DURABLE_IDENTITY.md`, this closes a gap left by its own predecessor: PR #104 (`docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md`) had already added a tenant-scoped `ProposalRegistry` and an ownership-gate/binding check in front of `MCCProposalService.get_operation_status`, but the underlying durable-execution keyspace was not yet tenant-scoped. PR #105's own commit history on this repository (visible in local `git log`) documents the remaining pieces explicitly:

- `94c2920` — "Scope durable execution identity to (tenant_id, key), not key alone"
- `bee7655` — "Fix legacy/scoped keyspace aliasing and make migration atomic"

This is direct repository evidence for: cross-tenant status isolation, tenant-scoped durable state, collision prevention between tenants sharing an identical `logical_operation_id`, legacy (pre-migration) unscoped record handling, and Redis-backed migration behavior. Fail-closed handling of unmigrated legacy records is documented in the same commit (`bee7655`, "make migration atomic").

---

## 8. Astra adversarial validation

**Astra is documented here strictly as an adversarial validation / stress-test client of an architecture that already existed before it was introduced — never as the origin of that architecture.**

`docs/GPT6_ASTRA_REFERENCE_INTEGRATION.md` states this explicitly: "This is not a new architecture. It is a new *client* of the architecture PR-1 through PR-6 already built" — referring to the pre-execution attestation series (§6/§9: PRs #90–96, specs `MCC-AT-001`–`004`), which predates Astra's introduction.

| Milestone | PR | Commit |
|---|---|---|
| GPT-6 Astra Reference Integration (real proposal, real MCC chain, real safe actuator) | [PR #100](https://github.com/mcc-prior-art/mcc-layer/pull/100) | `da82dd6` (2026-09-06) |
| README updated with the Astra validation milestone | [PR #101](https://github.com/mcc-prior-art/mcc-layer/pull/101) | `3939bd7` (2026-09-06) |
| GPT-6 Astra Adversarial Execution-Boundary Validation | [PR #102](https://github.com/mcc-prior-art/mcc-layer/pull/102) | `777f02c` (2026-09-06) |

`docs/GPT6_ASTRA_ADVERSARIAL_EXECUTION_BOUNDARY.md` frames PR #102's purpose precisely: "a capable Intelligence layer, given room to adapt — retry, reword, substitute tools or resources, propose alternative execution paths — must never be able to cause execution authority to drift," under the heading "Intelligence may adapt. Authority must not drift."

During live runs against the GPT-6 Astra API (documented in the current `README.md`, unchanged by this document), two concrete defects were found and fixed by exact-match, no-aliasing contract checks (mismatched action name, then a mismatched resource identifier) — findings that strengthened the *proposal contract*, and did not touch the mandate's own action/resource scope or execution-authority semantics. This document does not restate that narrative in more detail than the existing `docs/GPT6_ASTRA_REFERENCE_INTEGRATION.md` and README sections already do, to avoid duplicating or drifting from the existing record.

---

## 9. Phase 2 — Proposal to Governed Execution

**[PR #106 — "Phase 2: Proposal -> Signed Authority -> Governed Execution"](https://github.com/mcc-prior-art/mcc-layer/pull/106)**

- Merge commit: [`f01f0d67733382630066d10d61db6c6f60580e7f`](https://github.com/mcc-prior-art/mcc-layer/commit/f01f0d67733382630066d10d61db6c6f60580e7f)
- **Verified:** this SHA was not trusted on assertion. `git log -1 --format="%H %ad %s" f01f0d67733382630066d10d61db6c6f60580e7f` confirms it is a real commit in this repository's history, dated 2026-09-08, with subject "Merge pull request #106 from mcc-prior-art/feat/proposal-authority-execution-bridge." At the time this document was written, `origin/main` was exactly this commit (later advanced by PR #107, `a807304`).
- Merged: 2026-09-08T10:14:41Z, base `main` at `8b5651a` (PR #105's own merge commit).
- Notably, PR #106's own description states "**DO NOT MERGE.** This PR is submitted for review only" — yet GitHub records it as merged. This document reports what the repository actually contains (PR #106's changes are in `main`), not the PR description's stated intent; it does not attempt to resolve or explain that discrepancy.

Adds exactly one new service boundary, `gateway/proposal_execution_service.py`, composing existing, unmodified primitives:

```
authenticated tenant -> tenant-owned proposal -> exact proposal binding
-> trusted authorization decision -> signed authority token
-> existing ExecutionGate / EnforcementCoordinator
-> existing tenant-scoped durable execution identity (tenant_id, logical_operation_id)
-> controlled actuator -> durable execution state
-> proposal/status composition -> trusted reconciliation
```

Repository-evidenced significance of each element (per PR #106's own change description and `docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE2.md`):

- **Tenant-owned proposal** — `ProposalRegistry.get(tenant_id=, logical_operation_id=)`: a non-owned lookup is tenant-safe `NOT_FOUND`.
- **Exact stored operation binding** — `compute_proposal_binding` is recomputed at authorization time and compared against the record's own stored binding before any token issuance (internal-consistency check).
- **Trusted authority evaluation** — `AuthorityModel.evaluate(identity=tenant_id, ...)`, keyed on the caller's authenticated `tenant_id`, never the proposal's caller-supplied `actor` field.
- **`EnforcementCoordinator`** — the same coordinator described in §2/§6; no second Gate/coordinator/durable-execution registry exists in this path (a static test guard, `tests/test_proposal_service_architecture_guards.py`, forbids `src/mcc_proposal/` from importing the Gate/coordinator/authority/mandate/approvals/consensus directly).
- **Tenant-scoped durable admission** — reuses the composite `(tenant_id, logical_operation_id)` identity from §7.
- **`ResourceBoundUpstream`** — the class defined in `gateway/proposal_execution_service.py` (§9's own new file) that binds the authorized `resource` argument to the same call that dispatches, so a caller cannot authorize one resource and actuate against another.
- **Trusted reconciliation** — `reconcile_proposal_operation`, which independently re-verifies proposal identity, binding, and outcome evidence before resolving an ambiguous (`UNKNOWN`) state; never calls the upstream/actuator itself.
- **Legacy proposal compatibility** — built directly on the Phase 1 `MCCProposalService` (PR #104) without modifying its existing submit/status surface.

Per PR #106's own reported test evidence (not independently re-run for this document, but part of the same PR record): 28 tests in `tests/test_proposal_execution_bridge.py` (adversarial matrix A–N + non-vacuity probes 1–4); a targeted run of 357 tests; a full-suite run of 3,060 passed / 18 skipped; a mutation score of 1.0 (39/39 detected, zero survivors) on files touched by that round; and a real-Redis smoke script (`scripts/redis_proposal_phase2_smoke.py`).

---

## 10. README / public provenance milestone

**[PR #107 — "README: add canonical MCC-Core definition, update baseline to PR #106"](https://github.com/mcc-prior-art/mcc-layer/pull/107)**

- Merge commit: [`a807304f028dd165d4854cd26b559b69d43507b8`](https://github.com/mcc-prior-art/mcc-layer/commit/a807304f028dd165d4854cd26b559b69d43507b8)
- **Verified:** `origin/main` was fetched and confirmed to be exactly this SHA before this document's branch was created, and `git log -1` on that SHA confirms subject "Merge pull request #107 from mcc-prior-art/docs/readme-canonical-definition," dated 2026-09-08.
- Merged: 2026-09-08T17:14:12Z.

This PR is the point at which the top-level `README.md` gained:

- a concise canonical MCC-Core definition line directly below the title;
- an updated "Current capability baseline" pointing at PR #106 (§9) instead of the prior PR #100 (§8) baseline;
- an explicit **"Project provenance"** section stating that MCC-Core is an independently developed project by Alexandr Ponomariov / AXLOGIQ, and that this repository is a verifiable chronology of dated commits, specs, PRs, tests, and assurance artifacts.

This document (`docs/PROVENANCE.md`) is linked from that "Project provenance" section (§16) and expands on it with the full evidence-backed chronology.

---

## 11. Live sandbox proof

**Status at the time this document was written: PR #108 is OPEN, not merged.**

> Pending milestone — Live external sandbox proof

**[PR #108 — "Phase 2 Live Sandbox Proof — real external side effect through the unmodified ProposalExecutionService path"](https://github.com/mcc-prior-art/mcc-layer/pull/108)**, branch `feat/phase2-live-sandbox-proof`, head commit `41db88dd2e7fa65978ca8a7a150bedc5ea520434`, created 2026-09-08T17:11:52Z. Its own description states its scope precisely: it adds 11 new files (2,046 insertions, 0 modifications to any existing file, including no changes to `src/mcc_core/`, `gateway/proposal_execution_service.py`, `mcc_proposal/`, or `mcc_client/`), and it explicitly reports:

> "LIVE EXTERNAL SANDBOX: NOT EXECUTED — CREDENTIALS NOT AVAILABLE."

per its own item V — no dedicated sandbox-repository credentials were available in that session, so the actual external side effect (one GitHub issue in an isolated sandbox repository) has not yet been produced; only the deterministic test suite, mutation run, model-check run, and real-Redis smoke script have been.

This document does not present PR #108 as completed, does not modify it, and does not touch its branch, per the constraints of this task.

---

## 12. Chronological evidence table

Major architectural transitions only (not every commit). PRs #1–56: PR number + GitHub-API date only, no local commit SHA available (§1.3). PRs #57 onward: local git commit SHA.

| Date | Stage | PR / Commit | Artifact | Technical significance |
|---|---|---|---|---|
| 20–21.04.2026 (claimed; not independently confirmed by this document — §1.1) | Origin | — (repository exhibit, not a commit for the event itself) | `docs/exhibits/Prior_Art_Archive_2026-04.md`, citing an `archive.ph`/Telegra.ph snapshot and an X post | Earliest *claimed* public disclosure of MCC execution-control architecture (intent → policy → allow/deny/escalate, real-time policy patching, multi-agent consensus, hash-chain audit); this session could not independently render the cited external pages (§1.1) |
| 2026-04-25 | Origin | PR #1 (no local SHA) | `proof/screenshot.png` | Earliest GitHub-timestamped (and directly inspected) artifact in this repository; public X exchange referencing an early "MCC — Model Context Control" ALLOW/DENY/ESCALATE layer |
| 2026-06-02 | Doctrine | — (content-dated, no local SHA before 2026-07-25) | `MCC-Core_Decision_Boundary_Doctrine_2026-06-02.md`, `MCC-Core_Doctrine_Lines_v1_0_2026-06-02.md`, `MCC-Core_Non-Post-Execution_Principle_2026-06-02.md` | Formal doctrine layer; canonical four-line formula |
| 2026-06-11 | Core authority | PR #2 (no local SHA) | signed decision tokens | Ed25519-signed decision tokens introduced |
| 2026-06-22 | Core authority | PR #7 (no local SHA) | authority model + gateway + egress-proxy | Decision authority and enforced execution boundary (MVP) |
| 2026-06-23 | Core authority | PR #10 (no local SHA) | signed mandates, ESCALATE | Signed/revocable mandates; four-verdict ESCALATE loop |
| 2026-06-23 | Core authority | PR #13 (no local SHA) | Multi-Context Consensus 3/3 | N-of-M independent signed evaluator votes |
| 2026-06-25 | Core authority | PR #19 (no local SHA) | `/evaluate` full governance wiring | Runtime v1.11.0; contemporaneous `RUNTIME_VALIDATION_RECORD.md` |
| 2026-07-05 | Interoperability | PR #33/#35/#36 (no local SHA) | Python SDK, reference agent, VoltAgent | Canonical integration path; first real third-party framework |
| 2026-07-21/22 | Interoperability | PR #48–#55 (no local SHA) | interoperability matrix, Canonical Ingress Pipeline, Adapter SDK | 5-adapter framework-neutral matrix; canonical protocol formalized |
| 2026-07-25 | Specification | PR #56 (no local SHA) | `specs/MCC-CP/EB/CM/TC-001.md` | Four-document Normative Specification baseline |
| 2026-07-25 | Specification | PR #57 `7a2c69f` | — | Earliest commit reachable from local `git log` |
| 2026-07-25 | Specification | PR #59 `a65b2f3` | — | Normative v1.0 declaration |
| 2026-07-26 | Certification | PR #70 `e86234f` | — | Official Certification Release & Production Signing Ceremony |
| 2026-08-14 | Assurance | PR #71–#74 `59a1d2a`…`a7fd5a0` | `model/*.tla`, `mutation/` | Hermetic assurance, distributed replay, model checking, mutation testing |
| 2026-08-20 | Assurance | PR #85 `b079944` | audit checkpoint anchoring | External checkpoint anchoring for the audit hash-chain |
| 2026-08-31/09-01 | Attestation | PR #90 `67770e8` … PR #96 `8130f19` (squash-merge commits) | `src/mcc_attestation/`, `specs/MCC-AT-*.md` | Pre-execution attestation foundation through independent assurance |
| 2026-09-05 | Trust hardening | PR #98 `98e8e89` | durable replay + Attester boundary | Production Trust Hardening Phase 1 |
| 2026-09-06 | Adversarial validation | PR #100 `da82dd6` | GPT-6 Astra reference integration | First real frontier-model client of the existing architecture |
| 2026-09-06 | Adversarial validation | PR #102 `777f02c` | GPT-6 Astra adversarial validation | Execution-authority-drift resistance under an adaptive Intelligence layer |
| 2026-09-07 | Durable execution | PR #104 `790060f` | Universal Proposal Service Phase 1 | Transport-neutral proposal/status contract |
| 2026-09-08 | Tenant isolation | PR #105 `8b5651a` | tenant-scoped durable execution identity | `(tenant_id, logical_operation_id)` composite identity |
| 2026-09-08 | Governed execution | PR #106 `f01f0d6` | Phase 2 bridge | Proposal → Signed Authority → Governed Execution |
| 2026-09-08 | Public record | PR #107 `a807304` | README canonical definition + provenance | Public-facing provenance statement |
| open | Pending | PR #108 (unmerged) | live sandbox proof | Real external side effect — not yet executed |

---

## 13. Current architectural lineage

Verified against `src/mcc_core/coordinator.py` and `gateway/proposal_execution_service.py` on current `main` (only components with a corresponding class, function, or documented state in those files are retained):

```
INTELLIGENCE
→ ATTESTATION / CONTROL              (src/mcc_attestation/, docs/ATTESTATION_CONTROL_INTEGRATION.md)
→ SIGNED AUTHORITY                   (DecisionEngine.issue_token — Ed25519)
→ AUTHORITY VERIFICATION             (AuthorityModel.evaluate; token/payload/binding re-verification)
→ GATE                               (ExecutionGate; EnforcementCoordinator steps a–b: token + nonce)
→ TENANT-SCOPED DURABLE EXECUTION ADMISSION   (EnforcementCoordinator step c; (tenant_id, logical_operation_id))
→ DISPATCH OWNERSHIP                 (EnforcementCoordinator step f — "the point of no return")
→ AUDIT-BEFORE-ACTUATION             (EnforcementCoordinator step e, durably recorded before step f)
→ RESOURCE-BOUND CONTROLLED ACTUATOR (ResourceBoundUpstream.execute — resource re-verified at dispatch)
→ EXECUTION                          (EnforcementCoordinator step g)
→ EXECUTED / UNKNOWN                 (EnforcementCoordinator step h; IdempotencyRegistry states)
→ TRUSTED RECONCILIATION             (reconcile_proposal_operation)
```

Every stage name above corresponds to a class, function, documented step, or named state literally present in `src/mcc_core/coordinator.py`, `src/mcc_core/idempotency.py`, or `gateway/proposal_execution_service.py` on current `main` — none are inferred or aspirational.

---

## 14. Evidence index

**Specifications:** `specs/MCC-CP-001.md`, `specs/MCC-EB-001.md`, `specs/MCC-CM-001.md`, `specs/MCC-TC-001.md`, `specs/MCC-AT-001.md`–`004.md`

**Doctrine:** `MCC-Core_Decision_Boundary_Doctrine_2026-06-02.md`, `MCC-Core_Doctrine_Lines_v1_0_2026-06-02.md`, `MCC-Core_Non-Post-Execution_Principle_2026-06-02.md`

**Core architecture docs:** `docs/EXECUTION_AUTHORITY_BOUNDARY.md`, `docs/EXECUTION_STATE_MACHINE.md`, `docs/EXCLUSIVE_EXECUTION_PATH.md`, `docs/DECISION_TOKEN.md`, `docs/AUDIT_MODEL.md`, `docs/CANONICAL_GOVERNANCE_PROTOCOL.md`

**Durable execution / tenancy:** `docs/DURABLE_OPERATION_SAFETY.md`, `docs/TENANT_SCOPED_DURABLE_IDENTITY.md`, `docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md`, `docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE2.md`

**Attestation:** `docs/ATTESTATION_ARCHITECTURE.md`, `docs/ATTESTATION_CONTROL_INTEGRATION.md`, `docs/ATTESTATION_INDEPENDENT_ASSURANCE.md`

**Astra:** `docs/GPT6_ASTRA_REFERENCE_INTEGRATION.md`, `docs/GPT6_ASTRA_ADVERSARIAL_EXECUTION_BOUNDARY.md`

**Assurance:** `docs/REPRODUCING_ASSURANCE.md`, `docs/ASSURANCE_INDEX.md`, `docs/ASSURANCE_CLAIMS.md`, `docs/ASSURANCE_COVERAGE_MATRIX.md`, `docs/AUDIT_CHECKPOINT_ANCHORING.md`, `docs/INDEPENDENT_ASSURANCE.md`, `model/MCCExecutionStateMachine.tla`, `model/AttestationEvidenceBinding.tla`, `mutation/`

**Certification:** `docs/CERTIFICATION.md`, `docs/CERTIFICATION_PIPELINE.md`, `docs/CERTIFICATION_TRUST_AND_PUBLICATION.md`, `docs/CERTIFICATION_FIVE_ECOSYSTEMS.md`, `certifications/manifest.json`

**Interoperability:** `docs/ADAPTER_SDK.md`, `docs/INTEGRATION_CONTRACT.md`, `docs/GOVERNANCE_CAPABILITY_PROFILE.md`, `tests/interoperability/`

**Test suites (representative, not exhaustive):** `tests/test_proposal_execution_bridge.py`, `tests/test_mcc_proposal_registry.py`, `tests/test_coordinator.py`, `tests/test_coordinator_mandatory_tenant_id.py`, `tests/test_authority.py`, `tests/test_gpt6_astra_durable_operation_safety.py`, `assurance/tests/`

**Exhibits (protected — not modified by this document):** `docs/exhibits/Prior_Art_Archive_2026-04.md`, `docs/exhibits/X_Ban_Event_2026-04.md`, `docs/exhibits/README.md`

---

## 15. Provenance limitations

- Git history establishes a repository-recorded chronology of what was committed, when, and (via GitHub's PR metadata) when each pull request was opened and merged. It does not, by itself, prove the date of every earlier private idea, design note, or draft that may have existed before it entered this repository.
- Earlier private records (design notes, drafts, local files never committed) are not part of this repository's evidence and should be preserved separately if they are to support any future claim; this document does not assert dates for anything it cannot point to a repository or independently-timestamped external artifact for. See §1.7 for the specific private design records disclosed for this task.
- This repository's own commit history is not fully continuous: local `git log` does not reach earlier than the 2026-07-25 root commit (§1.3); GitHub's PR-API records for PRs #1–56 are the only independently timestamped evidence available for that earlier period, and this document relies on GitHub's control of those timestamps rather than a locally reachable commit.
- This is a technical provenance record, not a legal opinion. It does not determine legal priority, inventorship, ownership, or any patent-related status, and it should not be read as one.
- Where a retrospective document (such as an exhibit "filed" months after the events it describes) and a contemporaneously-timestamped artifact (a commit, a PR-API timestamp, an externally timestamped archive link) disagree or one is unverifiable, this document prefers the contemporaneously-timestamped artifact and says so explicitly, per §1.
- This document was written in a session whose network access could not reach `archive.ph`, `telegra.ph`, or `x.com` (§1.1). A reviewer with unrestricted network access could independently render those pages and should treat this document's characterization of them as "cited, not independently rendered" rather than as a rendering failure specific to those services.

---

## 16. Related record

This document is linked from [`README.md`](../README.md)'s "Project provenance" section as `[Project Provenance — Verifiable Technical Chronology](docs/PROVENANCE.md)`. That section carries the summary statement this document expands on.
