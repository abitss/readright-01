from __future__ import annotations

from readright.intelligence.intervention_library import interventions_for_hypothesis
from readright.intelligence.longitudinal import replay_longitudinal
from readright.persistence.models import LearnerEventRecord
from readright.persistence.store import assessment_evidence_from_events
from readright.teacher_decision.models import (
    DoView,
    LearnerTeacherDecision,
    TeacherDecisionOutcome,
    VerifyView,
    WhyView,
)

ENGINE_VERSION = "teacher-decision-v1-pilot-2026-09"


def _latest_event(events: list[LearnerEventRecord], event_type: str, hypothesis_id: str | None = None):
    candidates = [e for e in events if e.event_type == event_type]
    if hypothesis_id:
        candidates = [e for e in candidates if e.hypothesis_id == hypothesis_id]
    return candidates[-1] if candidates else None


def _verification_stage(events: list[LearnerEventRecord], hypothesis_id: str, intervention_id: str | None) -> tuple[str, str]:
    relevant = [
        e for e in events
        if e.event_type == "VERIFICATION_EVIDENCE"
        and e.hypothesis_id == hypothesis_id
        and (intervention_id is None or e.intervention_id == intervention_id)
    ]
    passed = {
        str(e.payload.get("stage"))
        for e in relevant
        if e.payload.get("correct") is True
        and e.payload.get("independent", True)
        and e.payload.get("quality") in {"HIGH", "MODERATE"}
    }
    if "INDEPENDENCE" not in passed:
        return "INDEPENDENCE", "DUE"
    if "TRANSFER" not in passed:
        return "TRANSFER", "DUE"
    if "RETENTION" not in passed:
        return "RETENTION", "DUE_LATER"
    return "RETENTION", "COMPLETE"


def _evidence_strength(hypothesis: dict) -> str:
    status = hypothesis.get("status")
    if status == "SUPPORTED":
        return "Strong"
    if status == "POSSIBLE":
        return "Some"
    if status in {"WEAK", "CONTRADICTED"}:
        return "Limited"
    return "Not enough"


def _why_from_bottleneck(bottleneck: dict) -> WhyView:
    primary = bottleneck.get("primary_hypothesis")
    alternatives = bottleneck.get("alternatives") or []
    if primary:
        return WhyView(
            headline=primary.get("label", "Current actionable learning barrier"),
            evidence_strength=_evidence_strength(primary),
            supporting_points=primary.get("supporting_evidence") or [],
            alternatives=[a.get("label", "") for a in alternatives[:3] if a.get("label")],
        )
    next_needed = bottleneck.get("next_evidence_needed") or []
    headline = {
        "MORE_EVIDENCE_REQUIRED": "More evidence is needed before choosing one learning barrier",
        "MULTIPLE_PLAUSIBLE_BARRIERS": "More than one learning barrier remains plausible",
        "CONFLICTING_OR_INSUFFICIENT_EVIDENCE": "Current evidence is conflicting or insufficient",
        "NO_ACTIONABLE_BARRIER_IDENTIFIED": "No actionable learning barrier is currently supported",
    }.get(bottleneck.get("outcome"), "Current learning picture is still forming")
    return WhyView(
        headline=headline,
        evidence_strength="Not enough" if next_needed else "Limited",
        supporting_points=bottleneck.get("rationale") or [],
        alternatives=[a.get("label", "") for a in alternatives[:3] if a.get("label")],
    )


def build_teacher_decision(learner_id: str, language: str, events: list[LearnerEventRecord]) -> LearnerTeacherDecision:
    replay = replay_longitudinal(events, language)
    bottleneck = replay["bottleneck"]
    why = _why_from_bottleneck(bottleneck)
    learner_state = replay["learner_state"]

    primary = bottleneck.get("primary_hypothesis")
    if not primary:
        outcome = {
            "MORE_EVIDENCE_REQUIRED": TeacherDecisionOutcome.MORE_EVIDENCE,
            "MULTIPLE_PLAUSIBLE_BARRIERS": TeacherDecisionOutcome.MORE_EVIDENCE,
            "CONFLICTING_OR_INSUFFICIENT_EVIDENCE": TeacherDecisionOutcome.CONFLICTING,
        }.get(bottleneck.get("outcome"), TeacherDecisionOutcome.NO_ACTION)
        return LearnerTeacherDecision(
            learner_id=learner_id,
            language=language,
            outcome=outcome,
            why=why,
            learner_state=learner_state,
        )

    hypothesis_id = primary["hypothesis_id"]
    intervention_candidates = interventions_for_hypothesis(hypothesis_id)
    intervention = intervention_candidates[0] if intervention_candidates else None

    latest_plan = _latest_event(events, "INTERVENTION_PLAN_CREATED", hypothesis_id)
    intervention_id = latest_plan.intervention_id if latest_plan else (intervention.intervention_id if intervention else None)
    verification_stage, verification_status = _verification_stage(events, hypothesis_id, intervention_id)

    if latest_plan and verification_status != "COMPLETE":
        reserved = latest_plan.payload
        task_key = {
            "INDEPENDENCE": "acquisition_task_ids",
            "TRANSFER": "transfer_task_ids",
            "RETENTION": "retention_task_ids",
        }[verification_stage]
        verify = VerifyView(
            stage=verification_stage,
            instruction={
                "INDEPENDENCE": "Check whether the learner can perform the target independently without the teaching scaffold.",
                "TRANSFER": "Use unseen equivalent material to check whether learning generalizes.",
                "RETENTION": "Run a later check to confirm the learning is maintained over time.",
            }[verification_stage],
            task_ids=reserved.get(task_key, []),
            status=verification_status,
        )
        return LearnerTeacherDecision(
            learner_id=learner_id,
            language=language,
            outcome=TeacherDecisionOutcome.VERIFY_DUE,
            why=why,
            do=None,
            verify=verify,
            learner_state=learner_state,
        )

    if intervention is None:
        return LearnerTeacherDecision(
            learner_id=learner_id,
            language=language,
            outcome=TeacherDecisionOutcome.NO_ACTION,
            why=why,
            learner_state=learner_state,
        )

    do = DoView(
        title=intervention.title,
        duration_minutes=intervention.duration_minutes,
        group_size=intervention.group_size,
        steps=intervention.steps,
        intervention_id=intervention.intervention_id,
    )
    verify = VerifyView(
        stage="INDEPENDENCE",
        instruction="After teaching, verify independent performance with reserved unseen items before claiming learning.",
        task_ids=[],
        status="PLANNED_AFTER_INTERVENTION",
    )
    return LearnerTeacherDecision(
        learner_id=learner_id,
        language=language,
        outcome=TeacherDecisionOutcome.ACTION_READY,
        why=why,
        do=do,
        verify=verify,
        learner_state=learner_state,
    )
