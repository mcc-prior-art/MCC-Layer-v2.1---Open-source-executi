# MCC Official Certification of the Five Reference Ecosystems

PR #69 (production issuer, official-eligibility gate, and release
publication added in PR #70 — see
[`docs/certification/OFFICIAL_SIGNING_CEREMONY.md`](certification/OFFICIAL_SIGNING_CEREMONY.md)
and [`docs/certification/OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md`](certification/OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md)).
Builds on [`CERTIFICATION_PIPELINE.md`](CERTIFICATION_PIPELINE.md)
(PR #67, the one certification pipeline) and
[`CERTIFICATION_TRUST_AND_PUBLICATION.md`](CERTIFICATION_TRUST_AND_PUBLICATION.md)
(PR #68, Issuer Identity / Trust Store / Signing-Key Provider / Publication).
This PR registers the five production reference ecosystems as real
Certification Targets and produces a candidate, all-or-nothing five-
ecosystem Publication Set. **It does not, by itself, produce OFFICIAL
certificates** — see "Candidate versus official status" below.

> **OFFICIAL SIGNING PENDING — PRODUCTION ISSUER KEY NOT PROVIDED.** No real
> Issuer private key exists anywhere in this repository or in the
> environment this PR was built in. Every artifact this PR's own CI
> produces is signed by an explicit, disclosed, deterministic **CI
> candidate issuer** (`mcc-ci-candidate-issuer`) and is NON_OFFICIAL by
> construction. PR #70 implements the full production-issuer activation,
> centralized official-eligibility gate, and protected signing/release
> workflow (`.github/workflows/mcc-official-certification.yml`) — but an
> authorized operator (AX) must still generate the real production key,
> configure the `mcc-production-signing` GitHub Environment, and run the
> protected ceremony for real before any ecosystem is OFFICIALLY CERTIFIED.
> See the Signing Ceremony runbook for the exact manual steps. This
> milestone is therefore code-complete and candidate-certification-complete,
> **not** officially-certification-complete.

## 1. The five certified reference ecosystems

| target_id | Ecosystem | Native boundary |
|---|---|---|
| `generic-http` | Generic HTTP | real `httpx` client → real loopback TCP → shared MCC Gateway |
| `langgraph` | LangGraph | native `langgraph.graph.StateGraph` → `CompiledStateGraph.invoke` |
| `crewai` | CrewAI | native `crewai.flow.flow.Flow.kickoff` (`@start`/`@listen`) |
| `autogen` | AutoGen | native `autogen_core.RoutedAgent` on a `SingleThreadedAgentRuntime` |
| `voltagent` | VoltAgent | native `@voltagent/core` `Agent` in a real Node subprocess |

All five reuse, unmodified, the real adapters built for the Multi-Adapter
Interoperability Proof (PR #48, `tests/interoperability/adapters/`) — this
PR adds no new adapter and redesigns none of the existing five.

## 2. Certification subjects, not certification authorities

Each ecosystem's adapter implements only `AdapterProof.proposal_for` (PR
#48) — it originates a `CanonicalProposal` from its native framework
object and stops. None of the five adapters imports `mcc_certify`, signs a
Technical Certificate, verifies Issuer trust, writes a Publication Record,
or defines its own certificate/evidence/manifest format (enforced by
`tests/test_mcc_certify_ecosystem_guards.py`). Certification decisions,
signing, trust resolution, and publication all happen exclusively in
`mcc_certify` — the ecosystems are evaluated, they never evaluate
themselves.

## 3. One identical certification pipeline

Every ecosystem is certified through the exact same, unmodified PR #67/#68
pipeline and CLI contract:

```bash
python -m mcc_certify certify generic-http --output ... --run-id ... --timestamp ...
python -m mcc_certify certify langgraph    --output ... --run-id ... --timestamp ...
python -m mcc_certify certify crewai       --output ... --run-id ... --timestamp ...
python -m mcc_certify certify autogen      --output ... --run-id ... --timestamp ...
python -m mcc_certify certify voltagent    --output ... --run-id ... --timestamp ...

# official mode (PR #68's existing flags — nothing new invented):
python -m mcc_certify certify <target> \
  --issuer-config <issuer.json> --signing-key <private-key.pem> \
  --trust-store <trust-store.json> --publication-dir <dir>
```

`pipeline.py` contains no per-ecosystem branch anywhere (statically
guarded: `test_all_five_ecosystem_targets_share_the_same_pipeline_and_verifier`)
— the only thing that differs between ecosystems is the
`CertificationTarget` descriptor each resolves to.

## 4. Target IDs and target descriptors

`src/mcc_certify/ecosystems.py` builds one `CertificationTarget` per
ecosystem (`build_generic_http_target`, `build_langgraph_target`,
`build_crewai_target`, `build_autogen_target`, `build_voltagent_target`),
registered in `src/mcc_certify/target.py`'s `_KNOWN_TARGETS` alongside
`reference-fixture`. Registration is unconditional — resolving any of the
five never raises `UnknownCertificationTargetError`, regardless of whether
that ecosystem's real package is installed (CP-001 Section 7.2: identity
is independent of evaluation success). Each descriptor's `provenance` dict
carries: `ecosystem_name`, `ecosystem_package`, `ecosystem_version`,
`adapter_module`, `adapter_version`, `native_api_entrypoint`,
`mcc_facade_version`, `integration_contract_version`,
`canonical_protocol_version`, `adapter_sdk_version`,
`normative_specification_version`, `certification_code_source`,
`execution_environment.*`, and a `target_config_hash` (a `sha256:` digest
over the target's own declared identity fields, so a substituted
descriptor is independently detectable). No field depends on a filesystem
path, PID, random value, or unverified environment variable.

## 5. Native framework execution boundaries

Each target's `conformance_entry_point` **lazily** imports the real
framework only when actually invoked (never at package import time — `import
mcc_certify` never requires any of the five frameworks), boots one
dedicated, isolated `SharedGovernedGateway` subprocess (PR #48's real
out-of-process MCC Gateway; no Redis, no external service) for that single
conformance run, builds the real adapter, and runs the real, unmodified
`run_common_scenarios` — the same seven governance scenarios
(ALLOW/DENY/REPLAY/MISMATCH/AUDIT/GATEWAY_UNAVAILABLE/INVALID_OR_EXPIRED)
every adapter in the interoperability proof already runs. A missing
framework raises `EcosystemDependencyUnavailableError` (a
`MalformedCertificationTargetError`) — never a fabricated pass.

## 6. Exact ecosystem and adapter provenance

See the certification report matrix (§19 below) for concrete values from
this environment. `adapter_module`/`adapter_version`/`ecosystem_package`
are static per ecosystem; `ecosystem_version` is resolved at run time via
`importlib.metadata.version(...)` against whatever package is actually
installed — never hardcoded, so a version mismatch between what's declared
and what's installed is impossible by construction.

## 7. Capability profiles

Each target's real adapter's own `capability_profile()` (PR #47/#48 shape)
is validated via the existing, unmodified
`mcc_compliance.capability_profile.validate_profile` and folded into a
`ECO-CAP-PROFILE-001` requirement result. No new capability-profile schema
or validator is introduced.

## 8. Applicability and NOT_APPLICABLE handling

Every one of the seven common scenarios plus the capability-profile check
plus a provenance check are REQUIRED for all five ecosystems (universal
applicability, CP-001 Section 12.3). ESCALATE (`ECO-GOV-ESCALATE-001`) and
CONSTRAIN (`ECO-GOV-CONSTRAIN-001`) are CONDITIONAL: NOT_APPLICABLE unless
the adapter's own capability profile declares
`human_in_the_loop_escalation`/`constraint_enforcement` as an optional
capability (none of the five currently do), consistent with CP-001 Section
11.6 ("unverified capability claims SHALL NOT appear"). If an adapter ever
does declare either without the harness having a scenario to verify it,
certification FAILs closed rather than silently passing an unverified claim.

## 9. Artifact layout

Identical to the existing PR #67/#68 layout
(`docs/CERTIFICATION_PIPELINE.md`, "Output artifacts") — one tree per
ecosystem under `<output>/<target_id>/<run_id>/`, containing Conformance
Run result, Evidence Bundle, Certification Manifest, Technical Certificate,
Publication Record (official mode), Offline Verification report, and a
human-readable `README.txt`/`certification-result.json`. No new file
format is introduced by this PR.

## 10. Five separate Technical Certificates

Each ecosystem's Technical Certificate binds, through the unchanged
MCC-TC-001 model: its own `certificate_id` (`<target_id>-<run_id>-certificate`),
`subject_id` (= `target_id`), `certified_capability_profiles`, its own
Manifest Reference and Evidence Bundle Reference (each an independent Hash
Reference), `issuer_id`/`kid`, `signature_algorithm` (`Ed25519` only),
`issuance_timestamp`. Certificates are never clones — every Hash Reference
is computed from that ecosystem's own, distinct Evidence Bundle/Manifest
bytes, and cross-target substitution is rejected both by the Certificate's
own verification (`verify_technical_certificate`) and, at the aggregate
layer, by an explicit `record.target_id != target_id` check (see
`tests/test_mcc_certify_pr69.py::test_aggregate_publication_set_rejects_cross_target_publication_record_substitution`).

## 11. Aggregate publication set

`src/mcc_certify/aggregate.py`'s `build_five_ecosystem_publication_set`
reads five already-completed, official-mode run directories (each produced
by an independent `mcc certify <target> --issuer-config ...` invocation —
the five ecosystems' Python dependencies are mutually incompatible and can
never coexist in one process, exactly like PR #48's own isolated
`interop-langgraph`/`interop-autogen`/`interop-crewai`/`interop-voltagent`
CI jobs), re-verifies each with `verify_certification_run_trusted` against
one shared explicit Trust Store, and merges their existing Publication
Records into one aggregate `PublicationIndex` — reusing PR #68's
`PublicationRecord`/`PublicationIndex` unchanged; no new publication
format. **All-or-nothing**: missing/duplicate/unexpected/unverifiable/
non-official ecosystems raise `AggregatePublicationError` and no aggregate
index is ever written.

## 12. Trusted offline-verification commands

```bash
# One ecosystem
python -m mcc_certify verify <run-dir> --trust-store <trust-store.json>

# The aggregate set
python -m mcc_certify verify-aggregate \
  --trust-store <trust-store.json> --publication-dir <aggregate-dir> \
  --run generic-http=<run-dir> --run langgraph=<run-dir> --run crewai=<run-dir> \
  --run autogen=<run-dir> --run voltagent=<run-dir>
```

## 13. Candidate versus official status

An ecosystem is **CANDIDATE / NON_OFFICIAL** (the state produced by the
`certification-<ecosystem>` CI jobs) when its Technical Certificate is
signed by the disclosed, deterministic CI candidate issuer
(`mcc-ci-candidate-issuer`, `scripts/generate_ci_candidate_issuer.py`) — a
real, non-fixture Ed25519 key (so the full official-mode code path
genuinely runs), but one whose `issuer_id` unambiguously identifies it as
non-production. An ecosystem is **OFFICIALLY CERTIFIED** only when
`mcc_certify.official.evaluate_official_eligibility` (PR #70 — the one
centralized, cryptographic eligibility gate) reports `eligible: True`,
which requires: (a) it was signed via the protected
`mcc-official-certification.yml` workflow using the real, separately-held
production Issuer key; (b) that Issuer (`mcc-official-certification-issuer-v1`)
is present and active in the committed, real production Trust Store; (c)
trusted offline verification against that real Trust Store passes; (d) a
`publication-record.json` exists (official mode only); (e) the run's
recorded `source_commit_sha` matches the ceremony's requested commit. **No
ecosystem reaches this state yet** — see the banner at the top of this
document, §19 below, and the certification report matrix.

## 14. Secure signing ceremony

Fully implemented in PR #70 —
[`docs/certification/OFFICIAL_SIGNING_CEREMONY.md`](certification/OFFICIAL_SIGNING_CEREMONY.md)
is the complete operator runbook. Summary:
`.github/workflows/mcc-official-certification.yml` runs `workflow_dispatch`
only, only from `main`, gated by the GitHub Environment
`mcc-production-signing` (required reviewers); validates the requested
commit is an exact 40-character SHA already merged into `main`; runs the
five ecosystems in isolated jobs (mirroring the candidate jobs' dependency
isolation), each independently decoding the real Issuer private key from
the `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` secret into a `0600` temp file
(never a command-line argument, deleted `if: always()`); rejects a
non-production issuer configuration before signing; only proceeds to
`official-release-publish` once all five succeed; supports `dry_run: true`
(default) to run the complete real signing chain without ever publishing a
GitHub Release; refuses to overwrite an existing release tag.

## 15. How the production Issuer key stays outside the repository

No PEM, private key, or key-shaped secret is committed anywhere in this
repository (verified by the repo-wide `grep -R "PRIVATE KEY"` scan in the
final validation checklist, plus `tests/test_mcc_certify_pr70.py::test_production_only_claims_remain_disabled_without_real_key_material`,
which asserts `config/official-issuer.json` itself does not exist yet).
The real Issuer key lives only in the GitHub Environment secret
`MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64`, provisioned out-of-band by an
authorized operator — this repository neither generates nor requests one
automatically. See §7 of the Signing Ceremony runbook for the exact manual
GitHub configuration steps.

## 16. How to reproduce the non-official certification candidates

```bash
export PYTHONPATH=src:.:sdk/python/src
pip install -r requirements.txt -r requirements-dev.txt
# plus, per ecosystem: tests/interoperability/requirements-{langgraph,crewai,autogen}.txt,
# or `npm ci` in integrations/voltagent for voltagent.

python scripts/generate_ci_candidate_issuer.py --output-dir /tmp/mcc-ci-trust
python -m mcc_certify certify generic-http \
  --output artifacts/certification-candidate --run-id ci-candidate-run \
  --timestamp 2026-07-26T00:00:00Z \
  --issuer-config /tmp/mcc-ci-trust/issuer.json --signing-key /tmp/mcc-ci-trust/issuer-key.pem \
  --trust-store /tmp/mcc-ci-trust/trust-store.json \
  --publication-dir artifacts/certification-candidate/publication
```

Repeat per ecosystem, each with the SAME deterministic candidate issuer
(so the aggregate Trust Store recognizes every signature), then:

```bash
python -m mcc_certify aggregate-publish --trust-store /tmp/mcc-ci-trust/trust-store.json \
  --publication-dir artifacts/aggregate-candidate \
  --run generic-http=... --run langgraph=... --run crewai=... --run autogen=... --run voltagent=...
```

## 17. How authorized operators issue the official certificates

See [`docs/certification/OFFICIAL_SIGNING_CEREMONY.md`](certification/OFFICIAL_SIGNING_CEREMONY.md)
for the complete runbook and
[`docs/certification/OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md`](certification/OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md)
for the step-by-step checklist (PR #70). Summary: generate the production
Issuer key offline (`scripts/generate_production_issuer_identity.py`),
commit only the public `config/official-issuer.json`/
`config/official-trust-store.json`, configure the `mcc-production-signing`
GitHub Environment and its `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` secret,
then dispatch `MCC Official Certification & Release` from `main` with
`dry_run: true` first, then `dry_run: false` to publish the immutable
GitHub Release once every ecosystem is confirmed eligible.

## 18. Known limitations

- **No official certificate has been issued.** Every artifact in this PR's
  CI is signed by the disclosed CI candidate issuer, not a real production
  Issuer — see the banner at the top of this document.
- **Only `generic-http` has been executed end-to-end in the environment
  this PR was authored in** (it has zero optional framework dependencies).
  LangGraph/CrewAI/AutoGen/VoltAgent correctly fail closed with
  `EcosystemDependencyUnavailableError` here because their real packages
  are not installed in this shared development environment — their real
  end-to-end runs happen in their own isolated CI jobs
  (`certification-langgraph`/`-crewai`/`-autogen`/`-voltagent`), exactly
  mirroring PR #48's own `interop-langgraph`/`-autogen`/`-crewai`/
  `-voltagent` isolation (these frameworks pin mutually incompatible
  dependencies and can never share one Python process).
- No production Issuer key exists anywhere yet; the protected signing
  ceremony workflow is implemented but has never been run for real.
- `mcc_certify` (including `ecosystems.py`/`aggregate.py`) remains excluded
  from the curated `mcc-core` PyPI wheel, exactly like `mcc_conformance`/
  `mcc_evidence` — unchanged packaging decision from PR #67/#68.
- The five targets' `conformance_entry_point`s import
  `tests.interoperability.*` directly (the only place the five real
  adapters exist) — a deliberate, disclosed layering choice explained in
  `src/mcc_certify/ecosystems.py`'s module docstring; this does not affect
  the curated wheel (which never ships `mcc_certify`).
- No cloud KMS/HSM/Vault-backed `SigningKeyProvider` exists yet (unchanged
  from PR #68) — the real signing ceremony still requires an operator to
  hold the PEM file locally for the duration of one workflow run.

## 19. PR #70 — MCC Official Certification Release

Implemented: production Issuer activation tooling, the centralized
official-eligibility gate, the immutable release-packaging module, the
protected signing-ceremony-and-release workflow, and full operator
documentation (`docs/certification/`). **Not yet performed:** the actual
protected ceremony against a real production Issuer key — see
`docs/certification/OFFICIAL_SIGNING_CEREMONY.md` §15 "Exact milestone
completion criteria" for what remains before any ecosystem is genuinely
OFFICIALLY CERTIFIED AND RELEASED.

---

## Certification report matrix

| target_id | Ecosystem | Ecosystem ver. | Adapter | Adapter ver. | Capability profile | Applicable reqs | PASS | NOT_APPLICABLE | Certificate status | Verification | Published | Reproduce with |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `generic-http` | Generic HTTP | `httpx` 0.28.1 (this env) | `tests.interoperability.adapters.generic_http` | 1.0.0 | `generic-http-reference-ecosystem-profile-v1` | 11 | 9 | 2 | CANDIDATE (CI issuer) | VALID (offline, trusted) | Not yet (candidate only) | `mcc certify generic-http ...` |
| `langgraph` | LangGraph | not installed in this doc-generation environment | `tests.interoperability.adapters.langgraph_adapter` | 1.0.0 | `langgraph-reference-ecosystem-profile-v1` | pending real run (`certification-langgraph` CI job) | — | — | SIGNING_REQUIRED | pending | Not yet | `mcc certify langgraph ...` (isolated env with `langgraph==1.2.9`) |
| `crewai` | CrewAI | not installed in this doc-generation environment | `tests.interoperability.adapters.crewai_adapter` | 1.0.0 | `crewai-reference-ecosystem-profile-v1` | pending real run (`certification-crewai` CI job) | — | — | SIGNING_REQUIRED | pending | Not yet | `mcc certify crewai ...` (isolated env with `crewai==1.15.5`) |
| `autogen` | AutoGen | not installed in this doc-generation environment | `tests.interoperability.adapters.autogen_adapter` | 1.0.0 | `autogen-reference-ecosystem-profile-v1` | pending real run (`certification-autogen` CI job) | — | — | SIGNING_REQUIRED | pending | Not yet | `mcc certify autogen ...` (isolated env with `autogen-agentchat==0.7.5`) |
| `voltagent` | VoltAgent | not installed in this doc-generation environment | `tests.interoperability.adapters.voltagent_adapter` | 1.0.0 | `voltagent-reference-ecosystem-profile-v1` | pending real run (`certification-voltagent` CI job) | — | — | SIGNING_REQUIRED | pending | Not yet | `mcc certify voltagent ...` (isolated env, Node 22 + `npm ci`) |

`generic-http`'s row reflects an actual local run in this environment
(11 requirements: 7 governance scenarios + capability-profile + provenance,
all PASS, plus ESCALATE/CONSTRAIN correctly NOT_APPLICABLE). The other
four rows are marked pending because their real framework packages are not
installed in the environment this PR was authored in; their dedicated,
isolated `certification-<ecosystem>` CI jobs (this PR) install the real
dependency and produce the actual candidate certification each time CI
runs — see that job's uploaded `certification-candidate-<ecosystem>`
artifact for concrete, current numbers.
