from __future__ import annotations

from enum import Enum

from readright.assessment.evidence_quality import EvidenceQuality


class StopOutcome(str, Enum):
    evidence_collected = "EVIDENCE_COLLECTED"
    more_evidence_required = "MORE_EVIDENCE_REQUIRED"
    conflicting_evidence = "CONFLICTING_EVIDENCE"
    unusable_context = "UNUSABLE_CONTEXT"
    session_limit_reached = "SESSION_LIMIT_REACHED"


PILOT_MAX_TASKS = 12


def evaluate_stop(*, evidence: list[dict], has_next_task: bool) -> StopOutcome | None:
    if len(evidence) >= PILOT_MAX_TASKS:
        return StopOutcome.session_limit_reached

    if evidence and all(event.get("quality") == EvidenceQuality.unusable.value for event in evidence):
        return StopOutcome.unusable_context

    if not has_next_task:
        usable = [
            event for event in evidence
            if event.get("quality") in {EvidenceQuality.high.value, EvidenceQuality.moderate.value}
        ]
        if not usable:
            return StopOutcome.more_evidence_required

        correct = sum(event.get("correct") is True for event in usable)
        incorrect = sum(event.get("correct") is False for event in usable)
        if correct and incorrect:
            return StopOutcome.conflicting_evidence
        return StopOutcome.evidence_collected

    return None
