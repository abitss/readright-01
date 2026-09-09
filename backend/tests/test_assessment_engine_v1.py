from readright.assessment.adaptive_policy import DecisionKind, select_next_adaptive_task
from readright.assessment.evidence_quality import EvidenceQuality, rate_evidence
from readright.assessment.frontier import SamplingState, summarize_skill
from readright.assessment.models import AssessmentMode, ResponseInput
from readright.assessment.planner import select_first_task
from readright.assessment.models import StartAssessmentRequest
from readright.assessment.stopping import StopOutcome, evaluate_stop


def event(task_id, skill_id, correct, quality="HIGH", assistance="none", seconds=15):
    return {
        "task_id": task_id,
        "skill_id": skill_id,
        "correct": correct,
        "assistance": assistance,
        "quality": quality,
        "estimated_seconds": seconds,
    }


def test_independent_teacher_confirmed_response_is_high_quality():
    response = ResponseInput(
        task_id="en-blend-001",
        response_raw="map",
        correct=True,
        assistance="none",
        teacher_confirmed=True,
    )
    assert rate_evidence(response) == EvidenceQuality.high


def test_modelled_response_is_not_mastery_quality():
    response = ResponseInput(
        task_id="en-blend-001",
        response_raw="map",
        correct=True,
        assistance="model",
        teacher_confirmed=True,
    )
    assert rate_evidence(response) == EvidenceQuality.low


def test_baseline_starts_with_broad_oral_language_anchor():
    request = StartAssessmentRequest(
        learner_id="L1",
        language="en",
        mode=AssessmentMode.baseline,
    )
    assert select_first_task(request).id == "en-oral-comp-001"


def test_focused_probe_requires_explicit_scientific_target():
    request = StartAssessmentRequest(
        learner_id="L1",
        language="en",
        mode=AssessmentMode.focused_probe,
    )
    try:
        select_first_task(request)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_single_failure_triggers_equivalent_form_not_conclusion():
    evidence = [event("en-blend-001", "EN-PHON-BLEND-CVC", False)]
    decision = select_next_adaptive_task(
        mode=AssessmentMode.baseline,
        language="en",
        current_skill_id="EN-PHON-BLEND-CVC",
        evidence=evidence,
    )
    assert decision.task is not None
    assert decision.task.skill_id == "EN-PHON-BLEND-CVC"
    assert decision.kind == DecisionKind.equivalent_form


def test_mixed_independent_results_are_conflicting_not_averaged():
    evidence = [
        event("en-blend-001", "EN-PHON-BLEND-CVC", True),
        event("en-blend-002", "EN-PHON-BLEND-CVC", False),
    ]
    summary = summarize_skill(evidence, "EN-PHON-BLEND-CVC")
    assert summary.state == SamplingState.conflicting
    decision = select_next_adaptive_task(
        mode=AssessmentMode.baseline,
        language="en",
        current_skill_id="EN-PHON-BLEND-CVC",
        evidence=evidence,
    )
    assert decision.kind == DecisionKind.contradiction_probe
    assert decision.task is not None


def test_replicated_negative_blending_localizes_with_phoneme_probe():
    evidence = [
        event("en-blend-001", "EN-PHON-BLEND-CVC", False),
        event("en-blend-002", "EN-PHON-BLEND-CVC", False),
    ]
    decision = select_next_adaptive_task(
        mode=AssessmentMode.baseline,
        language="en",
        current_skill_id="EN-PHON-BLEND-CVC",
        evidence=evidence,
    )
    assert decision.kind == DecisionKind.prerequisite_probe
    assert decision.task is not None
    assert decision.task.skill_id in {"EN-PHON-ISOLATE", "EN-PHON-SEG"}


def test_two_independent_correct_items_are_only_replicated_positive_sampling():
    evidence = [
        event("en-gpc-001", "EN-GPC", True),
        event("en-gpc-002", "EN-GPC", True),
    ]
    summary = summarize_skill(evidence, "EN-GPC")
    assert summary.state == SamplingState.replicated_positive
    # This is deliberately a sampling state, not a mastery label.
    assert "master" not in summary.state.value.lower()


def test_unusable_evidence_never_becomes_collected_evidence():
    evidence = [event("x", "EN-GPC", False, quality="UNUSABLE")]
    assert evaluate_stop(
        mode=AssessmentMode.baseline,
        evidence=evidence,
        has_next_task=False,
    ) == StopOutcome.unusable_context


def test_mode_specific_task_cap_stops_assessment():
    evidence = [event(f"p{i}", "EN-GPC", True) for i in range(6)]
    assert evaluate_stop(
        mode=AssessmentMode.progress_probe,
        evidence=evidence,
        has_next_task=True,
    ) == StopOutcome.session_limit_reached
