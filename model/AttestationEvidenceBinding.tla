---------------------- MODULE AttestationEvidenceBinding ----------------------
(***************************************************************************)
(* PR-5 -- Independent Assurance, Workstream I (extension).                *)
(*                                                                         *)
(* MCCExecutionStateMachine.tla (the original PR #71 model, unmodified by  *)
(* this file) models the generic PREPARED -> AUTHORIZED -> ... lifecycle   *)
(* and its single decision-token nonce -- it PRE-DATES PR-1 through PR-4   *)
(* entirely and has no notion of an attestation, an evidence digest, or a  *)
(* binding between the two. Rather than overload that module's already-    *)
(* meaningful state names with an unrelated concern, this is a SEPARATE,   *)
(* deliberately small module for exactly the part of the PR-1->4 chain     *)
(* that module cannot express: the relationship between VERIFIED EVIDENCE  *)
(* (PR-2's PreExecutionControl) and the SIGNED, evidence-BOUND execution   *)
(* token that ExecutionGate checks (PR-3).                                 *)
(*                                                                         *)
(* Concrete runtime mapping (informative, not machine-checked):            *)
(*   VerifyEvidence(op,en,eid)  <-> gateway.pre_execution_control.         *)
(*                                  PreExecutionControl.evaluate() -- a    *)
(*                                  successful, required attestation       *)
(*                                  verification, consuming the            *)
(*                                  attestation's OWN nonce (domain-       *)
(*                                  separated -- see ATC-REPLAY-002) and    *)
(*                                  producing evidence_digest (MCC-AT-003  *)
(*                                  EBT-DIGEST-001/002/003).               *)
(*   DenyEvidence(op,en)        <-> PreExecutionControl.evaluate() failing *)
(*                                  ANY static check (signature/trust/     *)
(*                                  action/payload/scope/policy/validity)  *)
(*                                  OR a replayed attestation nonce.       *)
(*   IssueToken(op,tn)          <-> DecisionEngine.issue_token(...,        *)
(*                                  evidence_digest=...) -- the SAME       *)
(*                                  evidence_digest VerifyEvidence produced *)
(*                                  is signed into the token's claims       *)
(*                                  (never re-derived, never a second       *)
(*                                  verification pass; this model's         *)
(*                                  ``boundEvidence[op]`` does not change    *)
(*                                  after VerifyEvidence for exactly this    *)
(*                                  reason).                                *)
(*   PresentEvidence(op,eid)    <-> the exact raw evidence artifact         *)
(*                                  ``EnforcementCoordinator.enforce()``     *)
(*                                  passes to ``ExecutionGate.verify()``    *)
(*                                  (governance_service.py's ``_run``).      *)
(*   GateAccept(op)             <-> ExecutionGate._verify()'s evidence-     *)
(*                                  binding check (hash_document(evidence)  *)
(*                                  == token's evidence_digest claim)        *)
(*                                  followed by nonce consumption -- both    *)
(*                                  succeeding.                              *)
(*   (no explicit "reject" action: see Inv_ExecutedImpliesEvidenceMatch     *)
(*   below -- GateAccept is simply not ENABLED on a mismatch, exactly       *)
(*   mirroring gate.py returning GateResult(False, "EVIDENCE_DIGEST_       *)
(*   MISMATCH: ...") WITHOUT consuming the nonce -- so a later              *)
(*   PresentEvidence with the CORRECT artifact can still enable             *)
(*   GateAccept for the SAME token; this is the model-level expression      *)
(*   of PR-3's "retry with correct evidence succeeds" proof.)               *)
(*                                                                         *)
(* This model is DELIBERATELY abstract and small, exactly like its         *)
(* companion: it does not model HTTP, Ed25519 signatures, or Redis -- it   *)
(* models only the ORDERING and SINGLE-USE-NONCE properties those          *)
(* mechanisms are supposed to guarantee. See                               *)
(* ``docs/ATTESTATION_INDEPENDENT_ASSURANCE.md`` for the honest boundary    *)
(* between what this model proves and what the black-box tests             *)
(* (``assurance/tests/test_attestation_chain.py``,                         *)
(* ``tests/test_evidence_bound_execution_ticket.py``) prove instead.        *)
(***************************************************************************)
EXTENDS FiniteSets, TLC

CONSTANTS Operations, EvidenceIds, EvidenceNonces, TokenNonces, NoEvidence, NoNonce

VARIABLES state, boundEvidence, presentedEvidence, evidenceNonceUsed,
          consumedEvidenceNonces, tokenNonce, consumedTokenNonces

vars == <<state, boundEvidence, presentedEvidence, evidenceNonceUsed,
          consumedEvidenceNonces, tokenNonce, consumedTokenNonces>>

States == {"UNSTARTED", "ATTESTED", "AUTHORIZED", "EXECUTED", "DENIED"}
TerminalStates == {"EXECUTED", "DENIED"}

(* NoEvidence / NoNonce are sentinel model values (declared as CONSTANTS,   *)
(* distinct-by-construction from every element of EvidenceIds/             *)
(* EvidenceNonces/TokenNonces via the .cfg's model-value declarations --   *)
(* TLA+ cannot express "choose a value outside this finite set" as a       *)
(* bounded CHOOSE, so an explicit sentinel constant is the standard idiom) *)
(* representing "not yet set" for boundEvidence/presentedEvidence and      *)
(* "not yet issued" for evidenceNonceUsed/tokenNonce.                      *)
ASSUME NoEvidence \notin EvidenceIds
ASSUME NoNonce \notin EvidenceNonces \union TokenNonces

TypeOK ==
    /\ state \in [Operations -> States]
    /\ boundEvidence \in [Operations -> EvidenceIds \union {NoEvidence}]
    /\ presentedEvidence \in [Operations -> EvidenceIds \union {NoEvidence}]
    /\ evidenceNonceUsed \in [Operations -> EvidenceNonces \union {NoNonce}]
    /\ consumedEvidenceNonces \subseteq EvidenceNonces
    /\ tokenNonce \in [Operations -> TokenNonces \union {NoNonce}]
    /\ consumedTokenNonces \subseteq TokenNonces

Init ==
    /\ state = [op \in Operations |-> "UNSTARTED"]
    /\ boundEvidence = [op \in Operations |-> NoEvidence]
    /\ presentedEvidence = [op \in Operations |-> NoEvidence]
    /\ evidenceNonceUsed = [op \in Operations |-> NoNonce]
    /\ consumedEvidenceNonces = {}
    /\ tokenNonce = [op \in Operations |-> NoNonce]
    /\ consumedTokenNonces = {}

(* PreExecutionControl.evaluate() succeeds: the attestation's own nonce is *)
(* fresh, and it binds this operation to exactly evidence document `eid`  *)
(* -- the same artifact whose digest becomes the token's evidence_digest  *)
(* claim (MCC-AT-003 EBT-DIGEST-003: the digest, and therefore this       *)
(* binding, is derived from the exact verified snapshot -- PR-3's TOCTOU  *)
(* fix is why `boundEvidence` is set exactly once, here, and never        *)
(* re-derived from a possibly-since-mutated caller object).               *)
VerifyEvidence(op, en, eid) ==
    /\ state[op] = "UNSTARTED"
    /\ en \notin consumedEvidenceNonces
    /\ state' = [state EXCEPT ![op] = "ATTESTED"]
    /\ boundEvidence' = [boundEvidence EXCEPT ![op] = eid]
    /\ evidenceNonceUsed' = [evidenceNonceUsed EXCEPT ![op] = en]
    /\ consumedEvidenceNonces' = consumedEvidenceNonces \union {en}
    /\ UNCHANGED <<presentedEvidence, tokenNonce, consumedTokenNonces>>

(* PreExecutionControl.evaluate() fails closed: either a replayed         *)
(* attestation nonce, or (abstracted away here, since it is not this      *)
(* model's concern -- see the companion model / MCC-AT-001's own black-   *)
(* box tests) any other static check. Either way: no evidence_digest, no  *)
(* token, ever, for this operation.                                       *)
DenyEvidence(op, en) ==
    /\ state[op] = "UNSTARTED"
    /\ en \in consumedEvidenceNonces
    /\ state' = [state EXCEPT ![op] = "DENIED"]
    /\ UNCHANGED <<boundEvidence, presentedEvidence, evidenceNonceUsed,
                   consumedEvidenceNonces, tokenNonce, consumedTokenNonces>>

(* DecisionEngine.issue_token(..., evidence_digest=...): mints a token     *)
(* carrying `tn` as its OWN (separate, domain-separated -- see             *)
(* MCC-AT-002 ATC-REPLAY-002) nonce. The token is not yet ACCEPTED by the  *)
(* Gate -- its nonce is not yet consumed; boundEvidence[op] (already set   *)
(* by VerifyEvidence and never changed again) is what the token's signed   *)
(* evidence_digest claim now, immutably, refers to.                        *)
IssueToken(op, tn) ==
    /\ state[op] = "ATTESTED"
    /\ state' = [state EXCEPT ![op] = "AUTHORIZED"]
    /\ tokenNonce' = [tokenNonce EXCEPT ![op] = tn]
    /\ UNCHANGED <<boundEvidence, presentedEvidence, evidenceNonceUsed,
                   consumedEvidenceNonces, consumedTokenNonces>>

(* The exact raw evidence artifact EnforcementCoordinator hands to         *)
(* ExecutionGate.verify() for this token -- MAY be presented (or           *)
(* re-presented, after an earlier mismatch) with ANY EvidenceIds value,    *)
(* not necessarily boundEvidence[op]: this is exactly the untrusted,       *)
(* attacker- or caller-controlled input GateAccept's guard below must      *)
(* discriminate on its own.                                                *)
PresentEvidence(op, eid) ==
    /\ state[op] = "AUTHORIZED"
    /\ presentedEvidence' = [presentedEvidence EXCEPT ![op] = eid]
    /\ UNCHANGED <<state, boundEvidence, evidenceNonceUsed,
                   consumedEvidenceNonces, tokenNonce, consumedTokenNonces>>

(* ExecutionGate accepts ONLY when the presented artifact's digest         *)
(* matches the token's bound evidence_digest claim exactly (MCC-AT-003     *)
(* EBT-GATE-003) AND the token's own nonce has not already been consumed   *)
(* by some other operation racing for the same TokenNonces value (a small  *)
(* TokenNonces set forces this collision, exactly as the companion model's *)
(* Nonces set does for opNonce) -- nonce consumption happens HERE, LAST,   *)
(* never before the evidence check (EBT-ORDER-001).                        *)
GateAccept(op) ==
    /\ state[op] = "AUTHORIZED"
    /\ presentedEvidence[op] = boundEvidence[op]
    /\ tokenNonce[op] \notin consumedTokenNonces
    /\ state' = [state EXCEPT ![op] = "EXECUTED"]
    /\ consumedTokenNonces' = consumedTokenNonces \union {tokenNonce[op]}
    /\ UNCHANGED <<boundEvidence, presentedEvidence, evidenceNonceUsed,
                   consumedEvidenceNonces, tokenNonce>>

(* No explicit "gate reject" action: a mismatched/replayed-nonce           *)
(* GateAccept is simply not ENABLED, so the operation stays AUTHORIZED --  *)
(* modeling that a rejected attempt never advances state, never consumes   *)
(* the nonce, and a SUBSEQUENT PresentEvidence with the correct artifact   *)
(* can still enable GateAccept for the identical, still-unconsumed token.  *)

Next ==
    \/ \E op \in Operations, en \in EvidenceNonces, eid \in EvidenceIds : VerifyEvidence(op, en, eid)
    \/ \E op \in Operations, en \in EvidenceNonces : DenyEvidence(op, en)
    \/ \E op \in Operations, tn \in TokenNonces : IssueToken(op, tn)
    \/ \E op \in Operations, eid \in EvidenceIds : PresentEvidence(op, eid)
    \/ \E op \in Operations : GateAccept(op)

Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------
(* Five required properties (PR-5 task specification, Phase 5), checked   *)
(* by TLC's exhaustive exploration of every reachable state.              *)

(* 1. Well-formedness. *)
Inv_TypeOK == TypeOK

(* 2. Execution implies valid authority: EXECUTED is reachable only via   *)
(*    AUTHORIZED (a token was actually issued) -- by construction, since  *)
(*    GateAccept's precondition is state[op] = "AUTHORIZED" and no other  *)
(*    action sets state to "EXECUTED".                                    *)
Inv_ExecutedImpliesAuthorized ==
    \A op \in Operations : state[op] = "EXECUTED" => tokenNonce[op] # NoNonce

(* 3. Where attestation is required (every operation, in this model),     *)
(*    execution implies verified trusted evidence was bound BEFORE the    *)
(*    token existed -- boundEvidence[op] is set exactly once, by          *)
(*    VerifyEvidence, and never afterward.                                *)
Inv_ExecutedImpliesEvidenceVerified ==
    \A op \in Operations : state[op] = "EXECUTED" => boundEvidence[op] # NoEvidence

(* 4. The evidence bound to the token matches the evidence presented at   *)
(*    the Gate -- the central MCC-AT-003 claim, restated as a state       *)
(*    invariant: it is IMPOSSIBLE to be EXECUTED with mismatched          *)
(*    evidence, because GateAccept's guard would not have been enabled.   *)
Inv_ExecutedImpliesEvidenceMatch ==
    \A op \in Operations : state[op] = "EXECUTED" => presentedEvidence[op] = boundEvidence[op]

(* 5. Replay cannot produce a second execution, in EITHER nonce domain:   *)
(*    no two distinct operations are ever simultaneously past ATTESTED    *)
(*    holding the same evidence (attestation) nonce, and no two distinct  *)
(*    operations are ever simultaneously EXECUTED holding the same token  *)
(*    nonce. Domain separation (MCC-AT-002 ATC-REPLAY-002) means these    *)
(*    are two INDEPENDENT invariants over two independent nonce spaces,   *)
(*    exactly as modeled here with two disjoint constant sets.            *)
Inv_NoDoubleEvidenceNonceConsumption ==
    \A op1, op2 \in Operations :
        (op1 # op2 /\ evidenceNonceUsed[op1] # NoNonce /\ evidenceNonceUsed[op1] = evidenceNonceUsed[op2])
        => FALSE

Inv_NoDoubleTokenNonceConsumption ==
    \A op1, op2 \in Operations :
        (op1 # op2 /\ tokenNonce[op1] # NoNonce /\ tokenNonce[op1] = tokenNonce[op2]
         /\ state[op1] = "EXECUTED" /\ state[op2] = "EXECUTED")
        => FALSE

=============================================================================
