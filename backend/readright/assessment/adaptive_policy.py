from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from readright.assessment.frontier import (
    SamplingState,
    blocked_by_negative_prerequisite,
    summarize_skill,
    unresolved_prerequisites,
)
from readright.assessment.models import AssessmentMode, AssessmentTask
from readright.assessment.skill_graph import prerequisites_for
from readright.assessment.task_bank import META, TASKS, tasks_for_skill

POLICY_VERSION = "assessment-v1-adaptive-pilot-2026-09"


class DecisionKind(str, Enum):
    equivalent_form = "EQUIVALENT_FORM"
    contradiction_probe = "CONTRADICTION_PROBE"
    prerequisite_probe = "PREREQUISITE_PROBE"
    baseline_anchor = "BASELINE_ANCHOR"
    baseline_advance = "BASELINE_ADVANCE"
    focused_probe = "FOCUSED_PROBE"
    progress_probe = "PROGRESS_PROBE"
    abstain = "ABSTAIN"


@dataclass(frozen=True)
class TaskDecision:
    task: AssessmentTask | None
    reason: str
    kind: DecisionKind
    policy_version: str = POLICY_VERSION
    utility: float | None = None


# Deliberately transparent broad anchors. These are sequencing choices, not norms.
ENGLISH_BASELINE_SEQUENCE = [
    "EN-ORAL-COMP",
    "EN-GPC",
    "EN-DECODE-CVC",
    "EN-DECODE-NONWORD",
    "EN-WORD-AUTO",
    "EN-ORF",
    "EN-READ-COMP",
    "EN-SPELL",
]

HINDI_BASELINE_SEQUENCE = [
    "HI-ORAL-COMP",
    "HI-AKSHARA-SOUND-BASIC",
    "HI-MATRA-INTEGRATION",
    "HI-WORD-DECODE",
    "HI-ORF",
    "HI-READ-COMP",
    "HI-SPELL",
]


MODE_TIME_BUDGET_SECONDS = {
    AssessmentMode.baseline: 12 * 60,
    AssessmentMode.focused_probe: 5 * 60,
    AssessmentMode.progress_probe: 3 * 60,
}


def _used_task_ids(evidence: list[dict]) -> set[str]:
    return {event.get("task_id") for event in evidence if event.get("task_id")}


def _candidate_tasks(skill_id: str, language: str, evidence: list[dict]) -> list[AssessmentTask]:
    used = _used_task_ids(evidence)
    candidates = [task for task in tasks_for_skill(skill_id, language) if task.id not in used]
    return sorted(candidates, key=lambda task: (task.difficulty, task.id))


def _parallel_to_last(skill_id: str, language: str, evidence: list[dict]) -> AssessmentTask | None:
    events = [event for event in evidence if event.get("skill_id") == skill_id]
    if not events:
        candidates = _candidate_tasks(skill_id, language, evidence)
        return candidates[0] if candidates else None

    last_task_id = events[-1].get("task_id")
    last_meta = META.get(last_task_id)
    candidates = _candidate_tasks(skill_id, language, evidence)
    if not last_meta:
        return candidates[0] if candidates else None

    same_group = [
        task for task in candidates
        if META.get(task.id) and META[task.id].equivalent_form_group == last_meta.equivalent_form_group
    ]
    return same_group[0] if same_group else (candidates[0] if candidates else None)


def _task_utility(task: AssessmentTask, target_skill: str, evidence: list[dict]) -> float:
    """Pilot heuristic, never treated as psychometric information gain.

    This prioritizes unresolved target evidence, parallel-form value, reasonable burden,
    and prerequisite localization. It is intentionally interpretable and replaceable
    after calibration data exist.
    """

    target = summarize_skill(evidence, target_skill)
    evidence_need = {
        SamplingState.unseen: 1.0,
        SamplingState.unusable_only: 1.0,
        SamplingState.assisted_only: 0.95,
        SamplingState.negative_sample: 0.95,
        SamplingState.conflicting: 1.0,
        SamplingState.positive_sample: 0.55,
        SamplingState.replicated_positive: 0.10,
        SamplingState.replicated_negative: 0.35,
    }[target.state]

    burden = max(task.estimated_seconds, 1) / 30.0
    difficulty_penalty = abs(task.difficulty - 0.40) * 0.25
    return round((evidence_need * 1.5) - (0.15 * burden) - difficulty_penalty, 4)


def _best_task_for_skill(skill_id: str, language: str, evidence: list[dict]) -> tuple[AssessmentTask | None, float | None]:
    candidates = _candidate_tasks(skill_id, language, evidence)
    if not candidates:
        return None, None
    ranked = sorted(
        ((task, _task_utility(task, skill_id, evidence)) for task in candidates),
        key=lambda pair: (-pair[1], pair[0].difficulty, pair[0].id),
    )
    return ranked[0]


def _first_unresolved_prerequisite(skill_id: str, language: str, evidence: list[dict]) -> TaskDecision | None:
    for prerequisite in prerequisites_for(skill_id):
        summary = summarize_skill(evidence, prerequisite)
        if summary.state in {
            SamplingState.unseen,
            SamplingState.unusable_only,
            SamplingState.assisted_only,
            SamplingState.negative_sample,
            SamplingState.conflicting,
        }:
            task, utility = _best_task_for_skill(prerequisite, language, evidence)
            if task:
                return TaskDecision(
                    task=task,
                    reason=f"Probe prerequisite {prerequisite} before interpreting {skill_id}.",
                    kind=DecisionKind.prerequisite_probe,
                    utility=utility,
                )
    return None


def _resolve_current_skill(current_skill_id: str, language: str, evidence: list[dict]) -> TaskDecision | None:
    summary = summarize_skill(evidence, current_skill_id)

    if summary.state == SamplingState.conflicting:
        task = _parallel_to_last(current_skill_id, language, evidence)
        if task:
            return TaskDecision(
                task=task,
                reason="Current evidence conflicts; collect an equivalent-form observation before moving on.",
                kind=DecisionKind.contradiction_probe,
                utility=_task_utility(task, current_skill_id, evidence),
            )

    if summary.state in {
        SamplingState.unusable_only,
        SamplingState.assisted_only,
        SamplingState.negative_sample,
    }:
        task = _parallel_to_last(current_skill_id, language, evidence)
        if task:
            return TaskDecision(
                task=task,
                reason="Collect a second independent usable observation before interpreting this skill.",
                kind=DecisionKind.equivalent_form,
                utility=_task_utility(task, current_skill_id, evidence),
            )

    if summary.state == SamplingState.replicated_negative:
        prerequisite_decision = _first_unresolved_prerequisite(current_skill_id, language, evidence)
        if prerequisite_decision:
            return prerequisite_decision

    return None


def _baseline_sequence(language: str) -> list[str]:
    return ENGLISH_BASELINE_SEQUENCE if language == "en" else HINDI_BASELINE_SEQUENCE


def _baseline_next(language: str, evidence: list[dict]) -> TaskDecision:
    sequence = _baseline_sequence(language)

    # If a lower-level repeated negative is unresolved, localize it before climbing.
    for skill_id in sequence:
        summary = summarize_skill(evidence, skill_id)
        if summary.state == SamplingState.replicated_negative:
            prereq = _first_unresolved_prerequisite(skill_id, language, evidence)
            if prereq:
                return prereq

    for skill_id in sequence:
        summary = summarize_skill(evidence, skill_id)
        if summary.state in {SamplingState.unseen, SamplingState.unusable_only, SamplingState.assisted_only}:
            blockers = blocked_by_negative_prerequisite(skill_id, evidence)
            if blockers:
                continue
            unresolved = unresolved_prerequisites(skill_id, evidence)
            if unresolved and skill_id not in {"EN-ORAL-COMP", "EN-GPC", "HI-ORAL-COMP", "HI-AKSHARA-SOUND-BASIC"}:
                prereq = _first_unresolved_prerequisite(skill_id, language, evidence)
                if prereq:
                    return prereq
            task, utility = _best_task_for_skill(skill_id, language, evidence)
            if task:
                return TaskDecision(
                    task=task,
                    reason=f"Advance baseline coverage to unresolved anchor skill {skill_id}.",
                    kind=DecisionKind.baseline_advance,
                    utility=utility,
                )

    return TaskDecision(
        task=None,
        reason="No additional safe baseline branch remains in the pilot bank.",
        kind=DecisionKind.abstain,
    )


def select_next_adaptive_task(
    *,
    mode: AssessmentMode,
    language: str,
    current_skill_id: str,
    evidence: list[dict],
    teacher_concern_skill_id: str | None = None,
) -> TaskDecision:
    current_resolution = _resolve_current_skill(current_skill_id, language, evidence)
    if current_resolution:
        return current_resolution

    if mode == AssessmentMode.focused_probe and teacher_concern_skill_id:
        prerequisite_decision = _first_unresolved_prerequisite(teacher_concern_skill_id, language, evidence)
        if prerequisite_decision:
            return prerequisite_decision
        task, utility = _best_task_for_skill(teacher_concern_skill_id, language, evidence)
        if task:
            return TaskDecision(
                task=task,
                reason=f"Continue focused evidence collection for {teacher_concern_skill_id}.",
                kind=DecisionKind.focused_probe,
                utility=utility,
            )
        return TaskDecision(None, "Focused probe has no unused safe pilot item.", DecisionKind.abstain)

    if mode == AssessmentMode.progress_probe:
        # Progress probes require comparable tasks; they do not escalate to broad diagnosis.
        task = _parallel_to_last(current_skill_id, language, evidence)
        if task:
            return TaskDecision(
                task=task,
                reason="Use a parallel-form item for a short comparable progress signal.",
                kind=DecisionKind.progress_probe,
                utility=_task_utility(task, current_skill_id, evidence),
            )
        return TaskDecision(None, "No unused parallel-form progress item is available.", DecisionKind.abstain)

    return _baseline_next(language, evidence)
