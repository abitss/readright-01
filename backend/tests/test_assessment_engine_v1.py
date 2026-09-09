from readright.assessment.evidence_quality import EvidenceQuality, rate_evidence
from readright.assessment.models import ResponseInput
from readright.assessment.selector import select_next_task
from readright.assessment.stopping import StopOutcome, evaluate_stop


def test_independent_teacher_confirmed_response_is_high_quality():
    response = ResponseInput(
        task_id="en-blend-map-001",
        response_raw="map",
        correct=True,
        assistance="none",
        teacher_confirmed=True,
    )
    assert rate_evidence(response) == EvidenceQuality.high


def test_modelled_response_is_not_mastery_quality():
    response = ResponseInput(
        task_id="en-blend-map-001",
        response_raw="map",
        correct=True,
        assistance="model",
        teacher_confirmed=True,
    )
    assert rate_evidence(response) == EvidenceQuality.low


def test_single_failure_does_not_stop_assessment():
    evidence = [
        {
            "task_id": "en-blend-map-001",
            "skill_id": "EN-PHON-BLEND-CVC",
            "correct": False,
            "assistance": "none",
            "quality": "HIGH",
        }
    ]
    next_task, _ = select_next_task(
        language="en",
        current_skill_id="EN-PHON-BLEND-CVC",
        evidence=evidence,
    )
    assert next_task is not None
    assert next_task.id == "en-blend-sat-002"


def test_two_failures_without_safe_prerequisite_bank_branch_abstain():
    evidence = [
        {
            "task_id": "en-blend-map-001",
            "skill_id": "EN-PHON-BLEND-CVC",
            "correct": False,
            "assistance": "none",
            "quality": "HIGH",
        },
        {
            "task_id": "en-blend-sat-002",
            "skill_id": "EN-PHON-BLEND-CVC",
            "correct": False,
            "assistance": "none",
            "quality": "HIGH",
        },
    ]
    next_task, _ = select_next_task(
        language="en",
        current_skill_id="EN-PHON-BLEND-CVC",
        evidence=evidence,
    )
    assert next_task is None
    assert evaluate_stop(evidence=evidence, has_next_task=False) == StopOutcome.evidence_collected


def test_unusable_evidence_never_becomes_collected_evidence():
    evidence = [
        {
            "task_id": "x",
            "skill_id": "EN-GPC",
            "correct": False,
            "assistance": "none",
            "quality": "UNUSABLE",
        }
    ]
    assert evaluate_stop(evidence=evidence, has_next_task=False) == StopOutcome.unusable_context
