from __future__ import annotations

from enum import Enum

from readright.assessment.frontier import SamplingState, summarize_skill
from readright.assessment.models import AssessmentMode


class StopOutcome(str, Enum):
    evidence_collected = "EVIDENCE_COLLECTED"
    more_evidence_required = "MORE_EVIDENCE_REQUIRED"
    conflicting_evidence = "CONFLICTING_EVIDENCE"
    unusable_context = "UNUSABLE_CONTEXT"
    session_limit_reached = "SESSION_LIMIT_REACHED"


MAX_TASKS_BY_MODE = {
    AssessmentMode.baseline: 24,
    AssessmentMode.focused_probe: 10,
    AssessmentMode.progress_probe: 6,
}

MAX_ESTIMATED_SECONDS_BY_MODE = {
    AssessmentMode.baseline: 12 * 60,
    AssessmentMode.focused_probe: 5 * 60,
    AssessmentMode.progress_probe: 3 * 60,
}


def _estimated_seconds(evidence: list[dict]) -> int:
    return sum(int(event.get("estimated_seconds") or 0) for event in evidence)


def _has_conflict(evidence: list[dict]) -> bool:
    skills = {event.get("skill_id") for event in evidence if event.get("skill_id")}
    return any(summarize_skill(evidence, skill_id).state == SamplingState.conflicting for skill_id in skills)


def evaluate_stop(
    *,
    mode: AssessmentMode,
    evidence: list[dict],
    has_next_task: bool,
) -> StopOutcome | None:
    if len(evidence) >= MAX_TASKS_BY_MODE[mode]:
        return StopOutcome.session_limit_reached

    if _estimated_seconds(evidence) >= MAX_ESTIMATED_SECONDS_BY_MODE[mode]:
        return StopOutcome.session_limit_reached

    if evidence and all(event.get("quality") == "UNUSABLE" for event in evidence):
        # One unusable event is not enough to terminate if a safe retry exists.
        if len(evidence) >= 2 or not has_next_task:
            return StopOutcome.unusable_context

    if has_next_task:
        return None

    usable = [event for event in evidence if event.get("quality") in {"HIGH", "MODERATE"}]
    if not usable:
        return StopOutcome.more_evidence_required

    if _has_conflict(evidence):
        return StopOutcome.conflicting_evidence

    return StopOutcome.evidence_collected
