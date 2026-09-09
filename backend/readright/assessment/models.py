from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class AssessmentMode(str, Enum):
    baseline = "baseline"
    focused_probe = "focused_probe"
    progress_probe = "progress_probe"


class StartAssessmentRequest(BaseModel):
    learner_id: str
    language: Literal["en", "hi"]
    mode: AssessmentMode
    teacher_concern: str | None = None
    # Focused/progress assessment must use an explicit scientific target.
    # Free-text teacher concern is preserved as context but never parsed into a
    # scientific skill label by an LLM in Assessment Engine v1.
    target_skill_id: str | None = None


class TaskPrompt(BaseModel):
    learner_text: str | None = None
    spoken_prompt: str | None = None
    teacher_text: str | None = None


class AssessmentTask(BaseModel):
    id: str
    language: Literal["en", "hi"]
    skill_id: str
    type: str
    prompt: TaskPrompt
    capture: str
    difficulty: float = Field(ge=0, le=1)
    estimated_seconds: int = Field(gt=0)
    evidence_targets: list[str]


class AssessmentSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    learner_id: str
    language: Literal["en", "hi"]
    mode: AssessmentMode
    status: Literal["active", "paused", "complete"] = "active"
    teacher_concern: str | None = None
    target_skill_id: str | None = None
    current_task: AssessmentTask | None = None


class ResponseInput(BaseModel):
    task_id: str
    response_raw: str | None = None
    correct: bool | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    assistance: Literal["none", "repeat", "hint", "model"] = "none"
    self_corrected: bool = False
    teacher_confirmed: bool = False
    quality_flags: list[str] = Field(default_factory=list)
