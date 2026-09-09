from __future__ import annotations

from readright.assessment.models import AssessmentMode, AssessmentTask, StartAssessmentRequest
from readright.assessment.skill_graph import get_skill
from readright.assessment.task_bank import get_task, tasks_for_skill


FIRST_TASK_BY_LANGUAGE = {
    # Baseline starts broad before descending into narrower reading processes.
    "en": "en-oral-comp-001",
    # Hindi remains a seed bank until its own language-specific bank is reviewed.
    "hi": "hi-akshara-k-001",
}


def _first_task_for_skill(skill_id: str, language: str) -> AssessmentTask | None:
    candidates = sorted(
        tasks_for_skill(skill_id, language),
        key=lambda task: (task.difficulty, task.id),
    )
    return candidates[0] if candidates else None


def select_first_task(request: StartAssessmentRequest) -> AssessmentTask:
    if request.mode in {AssessmentMode.focused_probe, AssessmentMode.progress_probe}:
        if not request.target_skill_id:
            raise ValueError("Focused and progress probes require target_skill_id")
        skill = get_skill(request.target_skill_id)
        if not skill or skill.language != request.language:
            raise ValueError("target_skill_id is not valid for the selected language")
        task = _first_task_for_skill(request.target_skill_id, request.language)
        if task is None:
            raise ValueError("No pilot task is available for target_skill_id")
        return task

    task = get_task(FIRST_TASK_BY_LANGUAGE[request.language])
    if task is None:
        raise RuntimeError("Configured assessment anchor is missing from the task bank")
    return task


def planner_reason(mode: AssessmentMode, target_skill_id: str | None = None) -> str:
    if mode == AssessmentMode.baseline:
        return "Start with a broad pilot anchor, then adapt toward the learner's unresolved skill frontier."
    if mode == AssessmentMode.focused_probe:
        return f"Collect focused evidence for explicit target {target_skill_id}; free-text concern is context only."
    return f"Collect a short parallel-form progress signal for explicit target {target_skill_id}."
