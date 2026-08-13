# Canonical Action Format — the normative HTTP action shape (`mcc-canonical-http-action/1`)

Part of the **MCC-Core Independent Adversarial Assurance Baseline** (PR #71,
Workstream D). This document is the normative specification for the flat,
deterministic dict that represents one outbound HTTP action — the exact
structure the decision token is signed over and the execution gate binds to
(`egress_proxy/canonical_action.py`, schema version implied by this doc).

It exists so a canonicalization can be re-implemented independently — and
was: `assurance/canonical_action.py` is a second, from-spec implementation,
used for the differential tests in
`assurance/tests/test_canonical_action_differential.py`
(`docs/INDEPENDENT_ASSURANCE.md` Workstream D). Two independent
implementations agreeing on the hash for a large input corpus is evidence
the format is unambiguous, not merely "whatever the code happens to do".

> The model proposes. MCC-Core decides. The gate enforces. The audit chain
> records. **This document fixes what "the action" means before any of
> that happens.**

## Why canonical form matters

The decision token's payload hash binds authorization to the *exact*
outbound action. Any difference between the action a Decision Token
authorizes and the action the executor actually performs — host, method,
path, query, a governed header, the body — must change the hash and be
rejected by the gate. Two representations of what a human would call "the
same request" (e.g. `Content-Type` vs `content-type`, or query params in a
different order) must therefore canonicalize to the *identical* dict, and
two materially different requests must canonicalize to *different* dicts.
This document is the rule for how that collapsing/distinguishing happens.

## Fields

| Field | Type | Rule |
|---|---|---|
| `action_type` | string | Always `"http.request"` |
| `method` | string | Uppercased; MUST be one of `GET POST PUT PATCH DELETE HEAD OPTIONS` |
| `scheme` | string | Lowercased; MUST be `http` or `https` |
| `host` | string | Lowercased hostname; MUST be non-empty; embedded userinfo (`user:pass@host`) is REJECTED |
| `port` | integer | Explicit port, or the scheme default (`80`/`443`) when omitted; MUST be in `(0, 65536)` |
| `path` | string | URL path; empty path normalizes to `/` |
| `query` | list of `[key, value]` pairs | Parsed with blank values kept, then **sorted** — order and duplicate keys in the input do not survive |
| `headers` | list of `[name, value]` pairs | Only **governed** headers survive (default: `content-type`, `accept`); names are lowercased; hop-by-hop headers (`Connection`, `Host`, `Content-Length`, …) are always dropped; the list is sorted |
| `destination_id` | string | `"{host}:{port}"` — a convenience field derived from the two above |
| `cred_ref` / `client_identity_ref` / `ca_bundle_ref` | string, optional | Governed credential **references** (identifiers only — never secret material); present only when supplied |
| `body_kind` | string | One of `empty`, `json`, `raw` — see below |

### Body encoding

* **Empty** (`None`, `{}`, or `""`) → `{"body_kind": "empty"}`, nothing else.
* **JSON object** → `{"body_kind": "json", "__body_keys__": [...sorted keys...], "body.<key>": <value>, ...}` for every key, sorted. Namespacing under `body.<key>` lets a policy constraint address a specific field (`max_body.amount`, `allowed_body.currency`) without reaching into a nested structure, and lets a CONSTRAIN clamp rewrite one field, producing a new, different hash.
* **Anything else** (string/bytes) → `{"body_kind": "raw", "__rawbody_b64__": <base64>, "__rawbody_sha256__": "sha256:<hex>"}`. Not clampable — a raw body is bound only by its hash.
* A body exceeding **1 MiB** (JSON-encoded or raw byte length) is REJECTED.

### Rejected inputs (canonicalization fails closed)

The following MUST be rejected before any authority/consensus decision is
made — a malformed action never reaches the gate:

* an unsupported `method` (anything outside the allowed set, including
  `TRACE`, `CONNECT`, or an empty string)
* an unsupported `scheme` (anything other than `http`/`https`, e.g. `ftp`)
* a URL with no host, an invalid port, or a port outside `(0, 65536)`
* a URL with embedded credentials (`http://user:pass@host/...`)
* a header whose name matches a **secret-bearing** header: `authorization`,
  `proxy-authorization`, `cookie`, `x-api-key`, `x-operator-key`, `api-key`
  (case-insensitive) — a caller proposes credential *references*, never raw
  secrets, in a header
* a body exceeding the 1 MiB cap

Two rejection layers exist in the real actuator: request-schema validation
(e.g. `method`/`url` with `min_length=1` — empty strings never reach
canonicalization at all) and canonicalization itself. Both are fail-closed;
which layer catches a given malformed input is an implementation detail, not
a normative guarantee — `assurance/tests/test_canonical_action_differential.py`
treats either as a pass for the malformed corpus.

## The hash

```
action_hash = sha256_hex(canonical_bytes(action))
```

reusing `mcc_core.signing`'s canonical JSON serialization (sorted keys,
compact separators, ASCII) and SHA-256 — the same low-level primitive every
signed or hashed structure in this repository uses. This document does not
introduce a second hashing scheme; only the higher-level question of *what
goes into the dict, and how it's normalized* is independently reimplemented
for differential testing.

## Non-goals

* This is not a general HTTP canonicalization standard — it governs exactly
  the fields MCC-Core binds authorization to, nothing more (e.g. it says
  nothing about header *values* it doesn't govern, or about response
  handling).
* Agreement between the reference implementation (`egress_proxy/canonical_action.py`)
  and the independent one (`assurance/canonical_action.py`) on the corpus in
  `assurance/tests/test_canonical_action_differential.py` is evidence, not
  proof, of correctness — a shared blind spot in both implementations (an
  input neither considered) would not be caught by this test.
