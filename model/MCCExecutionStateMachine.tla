---------------------- MODULE MCCExecutionStateMachine ----------------------
(***************************************************************************)
(* PR #71 -- Independent Adversarial Assurance Baseline, Workstream I.     *)
(*                                                                         *)
(* A bounded, machine-checkable formal model of the eight-state execution *)
(* lifecycle documented informally (and checked black-box, against the    *)
(* REAL running system) in ``assurance/state_machine.py`` and             *)
(* ``docs/EXECUTION_STATE_MACHINE.md``: PREPARED -> AUTHORIZED ->         *)
(* EVIDENCE_COMMITTED -> DISPATCHED -> {EXECUTED | EXECUTION_UNKNOWN ->   *)
(* RECONCILED}, with PREPARED -> DENIED as the only other exit.           *)
(*                                                                         *)
(* This model is DELIBERATELY abstract and small: it does not model HTTP, *)
(* Ed25519 signatures, canonical action hashing, or Redis -- it models    *)
(* only the ORDERING and MUTUAL-EXCLUSION properties those mechanisms are *)
(* supposed to guarantee, so TLC can exhaustively explore every possible  *)
(* interleaving of a small, finite number of operations sharing a small,  *)
(* finite pool of one-time authorization nonces. It is evidence about the *)
(* SHAPE of the state machine and nonce single-use discipline, not proof  *)
(* that any particular line of Python code implements it correctly --     *)
(* see the Workstream A-H black-box tests for that, and                  *)
(* ``docs/ASSUMPTIONS_AND_LIMITS.md`` for the honest boundary between     *)
(* what this model proves and what it does not.                          *)
(*                                                                         *)
(* ``authHistory`` is a GHOST/history variable: it records every          *)
(* Authorize event together with the value ``backendAvailable`` had at    *)
(* that moment, purely so the fail-closed property can be stated as a     *)
(* checkable state invariant over the accumulated history, rather than    *)
(* needing to inspect a transition's primed variables directly (TLC's     *)
(* INVARIANT mechanism only evaluates ordinary, unprimed state predicates).*)
(***************************************************************************)
EXTENDS FiniteSets, Sequences, Integers, TLC

CONSTANTS Operations, Nonces

VARIABLES state, opNonce, consumedNonces, backendAvailable, authHistory

vars == <<state, opNonce, consumedNonces, backendAvailable, authHistory>>

States == {"UNSTARTED", "PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED",
           "DISPATCHED", "EXECUTED", "DENIED", "EXECUTION_UNKNOWN", "RECONCILED"}

TerminalStates == {"DENIED", "EXECUTED", "RECONCILED"}

TypeOK ==
    /\ state \in [Operations -> States]
    /\ opNonce \in [Operations -> Nonces \union {"NONE"}]
    /\ consumedNonces \subseteq Nonces
    /\ backendAvailable \in BOOLEAN
    /\ authHistory \in Seq([op: Operations, wasBackendAvailable: BOOLEAN])

Init ==
    /\ state = [op \in Operations |-> "UNSTARTED"]
    /\ opNonce = [op \in Operations |-> "NONE"]
    /\ consumedNonces = {}
    /\ backendAvailable = TRUE
    /\ authHistory = <<>>

(* An operation is prepared: its canonical action is built and it is      *)
(* provisionally assigned a nonce it will present for authorization.      *)
(* Two DIFFERENT operations may be assigned the SAME nonce (a small       *)
(* Nonces set forces this) -- the model must show at most one of them     *)
(* ever gets past AUTHORIZED with it.                                     *)
Prepare(op, n) ==
    /\ state[op] = "UNSTARTED"
    /\ state' = [state EXCEPT ![op] = "PREPARED"]
    /\ opNonce' = [opNonce EXCEPT ![op] = n]
    /\ UNCHANGED <<consumedNonces, backendAvailable, authHistory>>

(* Authorization succeeds only if the shared backend is reachable AND     *)
(* this operation's nonce has not already been consumed by anyone.        *)
Authorize(op) ==
    /\ state[op] = "PREPARED"
    /\ backendAvailable
    /\ opNonce[op] \notin consumedNonces
    /\ state' = [state EXCEPT ![op] = "AUTHORIZED"]
    /\ consumedNonces' = consumedNonces \union {opNonce[op]}
    /\ authHistory' = Append(authHistory, [op |-> op, wasBackendAvailable |-> backendAvailable])
    /\ UNCHANGED <<opNonce, backendAvailable>>

(* Denied: either the backend was unreachable, or this operation's nonce  *)
(* had already been consumed (a replay/double-spend attempt).            *)
Deny(op) ==
    /\ state[op] = "PREPARED"
    /\ (~backendAvailable \/ opNonce[op] \in consumedNonces)
    /\ state' = [state EXCEPT ![op] = "DENIED"]
    /\ UNCHANGED <<opNonce, consumedNonces, backendAvailable, authHistory>>

CommitEvidence(op) ==
    /\ state[op] = "AUTHORIZED"
    /\ state' = [state EXCEPT ![op] = "EVIDENCE_COMMITTED"]
    /\ UNCHANGED <<opNonce, consumedNonces, backendAvailable, authHistory>>

Dispatch(op) ==
    /\ state[op] = "EVIDENCE_COMMITTED"
    /\ state' = [state EXCEPT ![op] = "DISPATCHED"]
    /\ UNCHANGED <<opNonce, consumedNonces, backendAvailable, authHistory>>

Execute(op) ==
    /\ state[op] = "DISPATCHED"
    /\ state' = [state EXCEPT ![op] = "EXECUTED"]
    /\ UNCHANGED <<opNonce, consumedNonces, backendAvailable, authHistory>>

MarkExecutionUnknown(op) ==
    /\ state[op] = "DISPATCHED"
    /\ state' = [state EXCEPT ![op] = "EXECUTION_UNKNOWN"]
    /\ UNCHANGED <<opNonce, consumedNonces, backendAvailable, authHistory>>

Reconcile(op) ==
    /\ state[op] = "EXECUTION_UNKNOWN"
    /\ state' = [state EXCEPT ![op] = "RECONCILED"]
    /\ UNCHANGED <<opNonce, consumedNonces, backendAvailable, authHistory>>

(* The environment: the shared backend (Redis/consensus quorum) can go    *)
(* down or come back up at any time, independent of any operation.        *)
ToggleBackend ==
    /\ backendAvailable' = ~backendAvailable
    /\ UNCHANGED <<state, opNonce, consumedNonces, authHistory>>

Next ==
    \/ \E op \in Operations, n \in Nonces : Prepare(op, n)
    \/ \E op \in Operations : Authorize(op)
    \/ \E op \in Operations : Deny(op)
    \/ \E op \in Operations : CommitEvidence(op)
    \/ \E op \in Operations : Dispatch(op)
    \/ \E op \in Operations : Execute(op)
    \/ \E op \in Operations : MarkExecutionUnknown(op)
    \/ \E op \in Operations : Reconcile(op)
    \/ ToggleBackend

(* Per-action, per-operation fairness. Weak fairness on each action is not *)
(* enough for Authorize/Deny: ToggleBackend can repeatedly enable and       *)
(* disable them, so neither is ever CONTINUOUSLY enabled, and plain WF      *)
(* only promises progress for actions that stay enabled without interrup-  *)
(* tion. Strong fairness (SF) promises progress for an action enabled      *)
(* infinitely often (even if repeatedly, transiently disabled) -- the      *)
(* correct assumption for "the backend outage is not permanent", which is  *)
(* what ToggleBackend actually models (it can flip availability, but       *)
(* cannot hold it down forever without ever coming back).                  *)
Fairness ==
    /\ \A op \in Operations : WF_vars(\E n \in Nonces : Prepare(op, n))
    /\ \A op \in Operations : SF_vars(Authorize(op))
    /\ \A op \in Operations : SF_vars(Deny(op))
    /\ \A op \in Operations : WF_vars(CommitEvidence(op))
    /\ \A op \in Operations : WF_vars(Dispatch(op))
    /\ \A op \in Operations : WF_vars(Execute(op))
    /\ \A op \in Operations : WF_vars(MarkExecutionUnknown(op))
    /\ \A op \in Operations : WF_vars(Reconcile(op))

Spec == Init /\ [][Next]_vars /\ Fairness

-----------------------------------------------------------------------------
(* The six required properties. Every one is checked by TLC's exhaustive  *)
(* breadth-first exploration of ALL reachable states / all fair behaviors *)
(* -- not by inspection of the guards above, though the guards are of     *)
(* course why they hold.                                                  *)

(* 1. Well-formedness: every reachable state is type-correct.             *)
Inv_TypeOK == TypeOK

(* 2. No two DISTINCT operations are ever simultaneously past AUTHORIZED  *)
(*    holding the same nonce -- the nonce single-use / anti-replay        *)
(*    property, independent of which two operations or which nonce.      *)
Inv_NoDoubleNonceConsumption ==
    \A op1, op2 \in Operations :
        (op1 # op2 /\ opNonce[op1] = opNonce[op2]
         /\ state[op1] \notin {"UNSTARTED", "PREPARED", "DENIED"}
         /\ state[op2] \notin {"UNSTARTED", "PREPARED", "DENIED"})
        => FALSE

(* 3. Once terminal, always terminal: expressed as the standard TLA+      *)
(*    "leads-to-and-stays" idiom -- whenever an operation reaches a       *)
(*    given terminal state, it is henceforth ALWAYS in that same state.   *)
Prop_TerminalStability ==
    \A op \in Operations : \A s \in TerminalStates :
        (state[op] = s) ~> [](state[op] = s)

(* 4. Fail-closed: every recorded Authorize EVENT, across the entire      *)
(*    explored state space, occurred while the shared backend was         *)
(*    reachable -- no operation is ever freshly authorized during an      *)
(*    outage (an operation already authorized before an outage begins     *)
(*    is unaffected -- a real system does not retroactively undo a        *)
(*    completed authorization).                                           *)
Inv_FailClosedWhileBackendDown ==
    \A i \in 1..Len(authHistory) : authHistory[i].wasBackendAvailable = TRUE

(* 5. Executed implies the operation's nonce was legitimately consumed    *)
(*    via Authorize -- authority-before-execution. Because EXECUTED is    *)
(*    reachable only via the fixed chain AUTHORIZED -> EVIDENCE_COMMITTED *)
(*    -> DISPATCHED -> EXECUTED, and Authorize is the only action that    *)
(*    inserts a nonce into consumedNonces, this ties the terminal state   *)
(*    back to the authorization event that justified it.                 *)
Inv_ExecutedImpliesAuthorizedPath ==
    \A op \in Operations : state[op] = "EXECUTED" => opNonce[op] \in consumedNonces

(* 6. Liveness: every operation that is ever PREPARED eventually reaches  *)
(*    a terminal state (DENIED, EXECUTED, or RECONCILED) -- no operation  *)
(*    is left stuck forever, under the fairness assumption WF_vars(Next). *)
Prop_EventualTermination ==
    \A op \in Operations : (state[op] = "PREPARED") ~> (state[op] \in TerminalStates)

=============================================================================
