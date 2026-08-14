# Third-Party Runbook — running the Independent Assurance Baseline yourself (PR #71)

> **For the current, single-command reproduction path** (`make
> verify-assurance`, with exact prerequisites, a pinned-commit checkout
> procedure, expected results, and the documented verified scope), see
> **[docs/REPRODUCING_ASSURANCE.md](REPRODUCING_ASSURANCE.md)**. This
> document remains useful for its "Mode 2" external-target instructions and
> its `MCC_ASSURANCE_*` environment-variable reference, which
> `REPRODUCING_ASSURANCE.md` does not duplicate — nothing here has been
> removed. Read the note below on this document's title before treating
> anything in it as third-party evidence, though: this repository has never
> been run by an unaffiliated third party, and nothing in either document
> claims otherwise.

This document is for someone who did **not** write this code and wants to
verify its claims independently — the necessary (but not sufficient, see
["What this is not"](#what-this-is-not) below) starting point for genuine
independent certification. **"Third-party" in the title names who this
runbook is written for (a reader who is not this project), not a claim
about who has produced any evidence using it.** No test result, evidence
bundle, or claim anywhere in this repository has been produced or operated
by an unaffiliated third party — every run to date, including any cited
elsewhere in this repository's docs or PR history, was performed by this
project itself. Calling that evidence "third-party" or "independent" would
be false; it is self-administered, and is described that way in
`docs/REPRODUCING_ASSURANCE.md`.

## Prerequisites

- Python 3.11+
- `redis-server` and `redis-cli` on `PATH` (for Workstream E)
- Java 11+ (Workstream I; `model/run_tlc.sh` downloads TLC's own jar —
  requires outbound network access on first run)
- Optionally: Node 22 + the frameworks in `tests/interoperability/
  requirements-{langgraph,autogen,crewai}.txt` if you want Workstream K's
  four framework-specific adapters to run locally instead of skipping

```bash
git clone <this repository>
cd mcc-layer
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Mode 1 — self-contained (the default; start here)

The suite provisions its own real, three-process deployment locally: a
real Gateway, a real `egress_proxy` actuator, a real mock external-effect
sink. No credentials to supply.

```bash
make independent-assurance
# or directly:
PYTHONPATH=src:.:sdk/python/src python -m assurance run --output artifacts/independent-assurance
```

This runs every workstream test module under `assurance/tests/`, prints a
summary, and writes a signed evidence bundle to the output directory. Exit
code is non-zero if any test failed.

Run the formal model and mutation testing separately (both are also
included by the CI workflow's mandatory job, but are slower and not part
of `assurance run` itself):

```bash
model/run_tlc.sh                                    # Workstream I
PYTHONPATH=. python -m mutation --output artifacts/mutation-report.json   # Workstream J
```

### Verifying the evidence bundle offline

```bash
PYTHONPATH=src:.:sdk/python/src python -m assurance verify --bundle artifacts/independent-assurance
```

Add `--trusted-public-key <base64>` if the run was signed with a key you
have the public half of (unsigned bundles verify as `INTACT`; signed but
untrusted-key bundles verify as `INTACT_UNTRUSTED_SIGNER`, not `INVALID` —
a tampered bundle is the only case that reports `INVALID`).

## Mode 2 — external target (pointing the suite at a deployment you provisioned)

Point the suite at a deployment YOU control and did not have this session
provision. This is the mechanism a genuinely independent reviewer would
need — but using this mode yourself does not, by itself, produce
third-party or independent evidence; it is still you (or this project)
running this project's own test suite. It becomes genuine third-party
verification only when the person running it is the unaffiliated reviewer
described in ["What this is not"](#what-this-is-not) below, on infrastructure
they control, publishing their own signed findings.

Set `MCC_ASSURANCE_EXTERNAL=1` plus:

| Variable | What it is |
|---|---|
| `MCC_ASSURANCE_GATEWAY_URL` | Your Gateway's base URL |
| `MCC_ASSURANCE_ACTUATOR_URL` | Your actuator's base URL |
| `MCC_ASSURANCE_NOTIFY_URL` | Your external-effect sink's base URL |
| `MCC_ASSURANCE_API_KEY` / `MCC_ASSURANCE_OPERATOR_KEY` | Your deployment's client credentials |
| `MCC_ASSURANCE_ACTUATOR_API_KEY` | Your actuator's client credential |
| `MCC_ASSURANCE_POLICY_HASH` | Your Gateway's policy hash (from its `/health`) |
| `MCC_ASSURANCE_EVALUATOR_KEYS_PATH` / `MCC_ASSURANCE_ACTUATOR_EVALUATOR_KEYS_PATH` | Paths to JSON files of `[{"kid": "...", "pem_path": "..."}]` — PEM file PATHS, never raw key material as an env value or CLI argument |

```bash
export MCC_ASSURANCE_EXTERNAL=1
export MCC_ASSURANCE_GATEWAY_URL=https://your-gateway.example
# ... the rest of the variables above ...
PYTHONPATH=src:.:sdk/python/src pytest assurance/tests/ -v
```

**This mode still requires YOU, the operator of the target deployment, to
generate evaluator keypairs, register the public halves in your OWN trust
config, and hand this suite the private key paths.** That is not a gap in
this suite — a black-box tester cannot prove "valid authorization works"
without being handed valid authorization by the system's own operator. It
is stated here so it is never mistaken for something this suite works
around. See `docs/ASSUMPTIONS_AND_LIMITS.md`.

## Interpreting a failure

- A failed test in `assurance/tests/` means a stated invariant did not
  hold against the target you pointed the suite at, at the commit you
  checked out. Read the failing test's own docstring — every test in this
  suite states, in its own words, which claim it is checking.
- `python -m mutation` reporting `SURVIVED` for a defect ID means the
  named detector test did not fail when that specific, documented code
  change was applied — see `mutation/defects.py` for exactly what changed
  and why it should have been caught.
- `model/run_tlc.sh` reporting a counterexample means the formal model
  itself found an internally inconsistent state — read the printed
  behavior trace; it names the exact sequence of actions that reached it.

## What this is not

Running this runbook yourself produces a **Certification Candidate
Evidence Bundle**. It is not, by itself, independent certification.
Genuine independent certification begins only when an **unaffiliated
third-party reviewer**:

1. did not write the code under test or this assurance suite;
2. controls execution themselves (chooses the environment, does not run a
   script the subject of the review handed them without reading it);
3. reviews the threat model (`docs/THREAT_MODEL.md`) and decides for
   themselves whether it matches their own risk model;
4. verifies the environment and source revision independently (this
   suite's evidence bundle records a best-effort `source_commit_sha`, but
   does not itself attest to build provenance beyond that);
5. signs their OWN findings with their OWN key — not this suite's;
6. publishes their own conclusions, including any limitations THEY find,
   which may differ from `docs/ASSUMPTIONS_AND_LIMITS.md`.

Nothing in this repository can perform steps 1–6 on its own behalf — by
definition, no system can independently certify itself. This runbook
exists to make step 2 straightforward for the reviewer who does.
