# Exclusive Execution Path — Workstream A (PR #71)

The single claim under test: **the protected actuator (`egress_proxy`)
never reports `executed=true` without a verified, correctly bound N-of-M
evaluator consensus.** Every attack below is a distinct way to try to make
that claim false, tested strictly black-box, over the real actuator's
public HTTP API (`POST /v1/http/execute`), against a real, live,
three-process deployment — never a mock, never an in-process call.

Full implementation: `assurance/tests/test_exclusive_execution_path.py`.
Reference model, adversary classes: `docs/THREAT_MODEL.md`.

## Observation method

Every test compares two independent signals:

1. **The actuator's own claim** — its JSON response (`outcome`,
   `executed`).
2. **An independently observed external effect** — the real
   `pilot_notify` mock service's own `GET /receipts` count, polled before
   and after each attack.

An attack "succeeds" against the real actuator only if BOTH signals agree
that nothing executed (`executed=false` AND the receipt count did not
increase). Trusting only the actuator's self-report would not be a
genuine black-box proof; the receipt count is the ground truth an
external, disinterested observer could also check.

## The eight required attacks

### A1 — Direct actuator invocation without completing consensus

Propose an action and never submit the second round (challenge + votes).
**Expected:** `outcome != ALLOW`, `executed=false`, no receipt.

### A2 — Stolen endpoint / wrong client credential

The attacker knows the actuator's URL but not its `x-api-key`.
**Expected:** HTTP 401, no receipt.

### A3 — Reused credential (replay)

Complete one fully authorized flow (proves the positive path is real: the
receipt count DOES increment by exactly one), then replay the identical
`challenge_id` + votes verbatim.
**Expected:** the replay is rejected (single-use challenge consumption);
the receipt count does not increase a second time.

### A4 — Adapter-to-actuator bypass (wrong trust domain)

Votes signed by the GATEWAY's own evaluator pool — a real, valid
consensus, but in a DIFFERENT trust domain than the actuator trusts.
**Expected:** rejected; trust sets are not interchangeable across
components even when both are internally valid.

### A5 — Agent-to-actuator bypass (self-signed forged evaluator)

An agent mints its own Ed25519 key and signs its own "evaluator" votes — a
key never registered in the actuator's trust store. Even three identical
ballots from the same untrusted key do not count as three votes.
**Expected:** rejected.

### A6 — Alternate network route (disallowed destination)

The proposed destination is outside the actuator's allowed-host set.
**Expected:** rejected by SSRF/allowlist enforcement (HTTP 400,
`SSRF_DENIED`), independent of whether valid votes would otherwise exist.

> **Stated limitation (this attack only):** A6 proves the actuator's OWN
> application-level allowlist works. It does NOT prove that an attacker
> with raw network access to the notify sink (bypassing the actuator's
> process entirely) could not reach it directly — that is a
> network-segmentation property this single-host, single-network-namespace
> test cannot observe.
>
> **That stronger claim is now proven separately**, with a real,
> kernel-enforced network boundary: `assurance/sut/network_segmentation.py`
> builds a genuine three-network-namespace topology (host → actuator's own
> namespace → the upstream's own namespace, connected only by veth links;
> no Docker — this environment's Docker Hub pulls are policy-blocked) in
> which the upstream namespace has NO route back to the host at all.
> `assurance/tests/test_network_segmentation.py` (N1–N3) proves: the
> governed flow still works end-to-end ACROSS that real boundary (N1); a
> direct connection attempt from the host straight to the upstream, with
> zero actuator/governance involvement, fails as a genuine NETWORK-layer
> error (`ConnectError`/`ConnectTimeout`, not an HTTP-level DENY) (N2); and
> the actuator's own inbound API remains reachable the whole time, proving
> the topology is segmented by design, not simply broken (N3). See
> `docs/ASSUMPTIONS_AND_LIMITS.md` for this proof's own stated limits (a
> `CAP_NET_ADMIN` process on the same host could still join the upstream's
> namespace directly; this is not a claim about a real multi-host network).

### A7 — Forged gate identity (tampered signature)

An otherwise well-formed, correctly bound vote whose signature bytes have
been altered after signing.
**Expected:** rejected; signature verification is exercised on genuinely
tampered bytes, not merely absent-signature cases.

### A8 — Valid token, wrong binding

Fully valid, correctly signed votes for a DIFFERENT, genuinely-issued
operation, submitted against THIS operation's challenge.
**Expected:** rejected; a valid signature alone is insufficient — the vote
must bind to the exact action/payload/actor/resource/nonce being executed.

## What "exclusive" means here, precisely

"Exclusive" is a claim about THIS ACTUATOR PROCESS's decision logic, not
about the network topology surrounding it. Combined with Workstream C
(the same containment property, proven one layer up at the Gateway's own
`/consensus/*` API) and Workstream K (proven again across five different
proposal-origination frameworks), the claim generalizes to: *regardless of
which component in this system's call graph an attacker targets, or which
framework originated the proposal, unauthorized execution is rejected at
every point tested.* It remains, throughout, a claim about the tested
component boundary — not a claim about host or network security outside
that boundary.
