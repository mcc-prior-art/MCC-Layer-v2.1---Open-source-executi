"""Negative Control for the attestation chain (PR-5).

Companion to ``assurance.sut.vulnerable_target``/``test_negative_control.py``
(PR #71), scoped specifically to the PR-1->4 attestation dimension those
predate and do not cover. Runs the EXACT SAME forged-attestation input
``test_attestation_chain.py::test_a1_forged_attestation_untrusted_key_blocked_no_actuation``
proves the REAL ``PreExecutionControl`` rejects through a DELIBERATELY
vulnerable stand-in instead (``assurance.sut.vulnerable_attestation_control.
VulnerableAttestationControl`` -- never wired into any real deployment) and
proves the SAME test methodology correctly reports it as exploitable there.

This never alters production behavior: the vulnerable stand-in is a
completely separate class, constructed and used ONLY inside this test
module's process, wired into a throwaway in-process GovernanceService
instance that exists only for the duration of one test.
"""

from __future__ import annotations

from assurance.sut.vulnerable_attestation_control import (
    VIOLATED_INVARIANTS,
    run_negative_control_scenario,
)


def test_nc_attestation_real_control_blocks_forged_attestation_no_actuation():
    """Restates the positive half of the comparison as its own assertion
    (not merely implied by the vulnerable half below): the REAL
    PreExecutionControl, presented with the identical forged attestation,
    blocks it and never actuates."""
    result = run_negative_control_scenario()
    assert result["real_status"] == "BLOCKED", result
    assert result["real_actuation_count"] == 0


def test_nc_attestation_vulnerable_control_wrongly_accepts_forged_attestation():
    """The control arm: the SAME forged attestation, presented to a
    DELIBERATELY vulnerable stand-in wired into the same kind of real
    GovernanceService stack, is wrongly accepted and genuinely actuates --
    proving the test methodology (construct an untrusted-key attestation;
    present it; observe BOTH the reported outcome and an independent
    actuation counter) has real discriminating power. A suite that always
    reports the attestation chain as secure, without ever being shown to
    detect an insecure one, would not be evidence of anything."""
    result = run_negative_control_scenario()
    assert result["vulnerable_status"] == "EXECUTED", (
        "the negative control was expected to be exploitable via a forged, "
        "untrusted-key attestation (no signature/trust/replay checking), "
        f"but it was not -- see assurance/sut/vulnerable_attestation_control.py: {result}"
    )
    assert result["vulnerable_actuation_count"] == 1


def test_nc_violated_invariants_are_named():
    """The negative control documents, in one place, exactly which real
    invariants it deliberately violates -- mirrors
    assurance.sut.vulnerable_target.VIOLATED_INVARIANTS's convention."""
    assert len(VIOLATED_INVARIANTS) >= 3
    for invariant in VIOLATED_INVARIANTS:
        assert isinstance(invariant, str) and invariant
