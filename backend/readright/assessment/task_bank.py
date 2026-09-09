from __future__ import annotations

from dataclasses import dataclass

from readright.assessment.models import AssessmentTask, TaskPrompt


@dataclass(frozen=True)
class TaskMeta:
    family: str
    equivalent_form_group: str
    prerequisites: tuple[str, ...]
    pilot_only: bool = True
    calibration_status: str = "UNVALIDATED_PILOT"


# Keep Hindi as a deliberately tiny seed bank until its language-specific content
# receives independent linguistic design and review.
TASKS: dict[str, AssessmentTask] = {
    "hi-akshara-k-001": AssessmentTask(
        id="hi-akshara-k-001",
        language="hi",
        skill_id="HI-AKSHARA-SOUND-BASIC",
        type="letter_sound",
        prompt=TaskPrompt(
            learner_text="इस अक्षर की ध्वनि बताओ।",
            spoken_prompt=None,
            teacher_text="Show क and record the response without coaching.",
        ),
        capture="voice",
        difficulty=0.20,
        estimated_seconds=15,
        evidence_targets=["akshara_sound_mapping"],
    ),
    "hi-akshara-m-002": AssessmentTask(
        id="hi-akshara-m-002",
        language="hi",
        skill_id="HI-AKSHARA-SOUND-BASIC",
        type="letter_sound",
        prompt=TaskPrompt(
            learner_text="इस अक्षर की ध्वनि बताओ।",
            spoken_prompt=None,
            teacher_text="Show म and record the response without coaching.",
        ),
        capture="voice",
        difficulty=0.20,
        estimated_seconds=15,
        evidence_targets=["akshara_sound_mapping"],
    ),
}

META: dict[str, TaskMeta] = {
    "hi-akshara-k-001": TaskMeta("akshara_sound", "HI-AKSHARA-EQ-A", ("HI-AKSHARA-RECOG",)),
    "hi-akshara-m-002": TaskMeta("akshara_sound", "HI-AKSHARA-EQ-A", ("HI-AKSHARA-RECOG",)),
}

# Rich metadata not exposed in the public AssessmentTask contract yet.
STIMULI: dict[str, dict] = {
    "hi-akshara-k-001": {"display": "क", "expected": [], "validation_status": "UNVALIDATED_PILOT"},
    "hi-akshara-m-002": {"display": "म", "expected": [], "validation_status": "UNVALIDATED_PILOT"},
}

# Import after TaskMeta is defined to avoid coupling the English bank generator
# to API/runtime concerns.
from readright.assessment.english_v1 import build_english_v1  # noqa: E402

_EN_TASKS, _EN_META, _EN_STIMULI = build_english_v1()
TASKS.update(_EN_TASKS)
META.update(_EN_META)
STIMULI.update(_EN_STIMULI)


def tasks_for_skill(skill_id: str, language: str | None = None) -> list[AssessmentTask]:
    tasks = [task for task in TASKS.values() if task.skill_id == skill_id]
    if language:
        tasks = [task for task in tasks if task.language == language]
    return tasks


def get_task(task_id: str) -> AssessmentTask | None:
    return TASKS.get(task_id)


def get_task_stimulus(task_id: str) -> dict | None:
    return STIMULI.get(task_id)


def bank_summary() -> dict:
    english = [task for task in TASKS.values() if task.language == "en"]
    hindi = [task for task in TASKS.values() if task.language == "hi"]
    return {
        "english_items": len(english),
        "hindi_seed_items": len(hindi),
        "english_status": "UNVALIDATED_PILOT",
        "hindi_status": "UNVALIDATED_PILOT",
        "english_skills": sorted({task.skill_id for task in english}),
    }
