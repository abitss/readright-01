from readright.intelligence.intervention_models import (
    HypothesisRevisionDirection,
    InterventionFidelity,
    VerificationEvidence,
    VerificationStage,
)
from readright.intelligence.intervention_response import interpret_intervention_response
from readright.intelligence.intervention_selector import select_intervention_plan


def _event(skill_id: str, correct: bool):
    return {
        "task_id": f"t-{skill_id}-{correct}",
        "skill_id": skill_id,
        "correct": correct,
        "assistance": "none",
        "quality": "HIGH",
    }


def test_no_intervention_when_bottleneck_not_isolated():
    assert select_intervention_plan([], "en") is None


def test_supported_blending_hypothesis_can_select_plan():
    evidence = [
        _event("EN-GPC", True),
        _event("EN-GPC", True),
        _event("EN-PHON-BLEND-CVC", False),
        _event("EN-PHON-BLEND-CVC", False),
    ]
    plan = select_intervention_plan(evidence, "en")
    assert plan is not None
    assert plan.hypothesis_id == "H-BLEND"
    assert plan.intervention.target_skill_id == "EN-PHON-BLEND-CVC"
    assert plan.intervention.validation_status == "UNVALIDATED_PILOT"


def test_low_fidelity_failure_cannot_weaken_hypothesis():
    events = [
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=False, independent=True),
    ]
    decision = interpret_intervention_response(
        hypothesis_id="H-BLEND",
        fidelity=InterventionFidelity.LOW,
        verification_events=events,
    )
    assert decision.revision == HypothesisRevisionDirection.CANNOT_INTERPRET


def test_acceptable_fidelity_nonresponse_weakens_hypothesis():
    events = [
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=False, independent=True),
    ]
    decision = interpret_intervention_response(
        hypothesis_id="H-BLEND",
        fidelity=InterventionFidelity.ACCEPTABLE,
        verification_events=events,
    )
    assert decision.revision == HypothesisRevisionDirection.WEAKEN


def test_transfer_success_strengthens_hypothesis():
    events = [
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.TRANSFER, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.TRANSFER, correct=True, independent=True),
    ]
    decision = interpret_intervention_response(
        hypothesis_id="H-BLEND",
        fidelity=InterventionFidelity.HIGH,
        verification_events=events,
    )
    assert decision.revision == HypothesisRevisionDirection.STRENGTHEN


def test_acquisition_without_transfer_reopens_alternatives():
    events = [
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.ACQUISITION, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.INDEPENDENCE, correct=True, independent=True),
        VerificationEvidence(stage=VerificationStage.TRANSFER, correct=False, independent=True),
        VerificationEvidence(stage=VerificationStage.TRANSFER, correct=False, independent=True),
    ]
    decision = interpret_intervention_response(
        hypothesis_id="H-BLEND",
        fidelity=InterventionFidelity.ACCEPTABLE,
        verification_events=events,
    )
    assert decision.revision == HypothesisRevisionDirection.REOPEN_ALTERNATIVES
