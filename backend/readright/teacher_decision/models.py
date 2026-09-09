from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class TeacherDecisionOutcome(str, Enum):
    ACTION_READY = "ACTION_READY"
    VERIFY_DUE = "VERIFY_DUE"
    MORE_EVIDENCE = "MORE_EVIDENCE"
    CONFLICTING = "CONFLICTING"
    NO_ACTION = "NO_ACTION"


class WhyView(BaseModel):
    headline: str
    evidence_strength: str
    supporting_points: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class DoView(BaseModel):
    title: str
    duration_minutes: int | None = None
    group_size: str | None = None
    steps: list[str] = Field(default_factory=list)
    intervention_id: str | None = None


class VerifyView(BaseModel):
    stage: str
    instruction: str
    task_ids: list[str] = Field(default_factory=list)
    status: str


class LearnerTeacherDecision(BaseModel):
    learner_id: str
    language: str
    outcome: TeacherDecisionOutcome
    why: WhyView
    do: DoView | None = None
    verify: VerifyView | None = None
    learner_state: dict = Field(default_factory=dict)
    scientific_status: str = "UNVALIDATED_PILOT"
    engine_version: str = "teacher-decision-v1-pilot-2026-09"


class InstructionGroup(BaseModel):
    group_id: str
    label: str
    learner_ids: list[str]
    hypothesis_id: str | None = None
    intervention_id: str | None = None
    verification_stage: str | None = None
    priority: int
    reason: str


class RotationBlock(BaseModel):
    order: int
    minutes: int
    group_id: str | None = None
    title: str
    action: str
    learner_ids: list[str] = Field(default_factory=list)


class ClassPlan(BaseModel):
    total_minutes: int
    groups: list[InstructionGroup]
    rotations: list[RotationBlock]
    deferred_learner_ids: list[str] = Field(default_factory=list)
    scientific_status: str = "UNVALIDATED_PILOT"
    engine_version: str = "teacher-class-plan-v1-pilot-2026-09"
