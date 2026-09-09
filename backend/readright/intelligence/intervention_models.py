from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class InterventionFidelity(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    ACCEPTABLE = "ACCEPTABLE"
    HIGH = "HIGH"


class VerificationStage(str, Enum):
    ACQUISITION = "ACQUISITION"
    INDEPENDENCE = "INDEPENDENCE"
    TRANSFER = "TRANSFER"
    RETENTION = "RETENTION"


class VerificationOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONFLICTING = "CONFLICTING"
    UNUSABLE = "UNUSABLE"
    NOT_DUE = "NOT_DUE"
    MORE_EVIDENCE_REQUIRED = "MORE_EVIDENCE_REQUIRED"


class HypothesisRevisionDirection(str, Enum):
    STRENGTHEN = "STRENGTHEN"
    WEAKEN = "WEAKEN"
    REOPEN_ALTERNATIVES = "REOPEN_ALTERNATIVES"
    NO_CHANGE = "NO_CHANGE"
    CANNOT_INTERPRET = "CANNOT_INTERPRET"


class InterventionSpec(BaseModel):
    intervention_id: str
    hypothesis_id: str
    target_skill_id: str
    title: str
    purpose: str
    group_size: str
    duration_minutes: int = Field(gt=0)
    sessions_per_week: int = Field(gt=0)
    delivery_principles: list[str]
    steps: list[str]
    practice_constraints: list[str]
    do_not_do: list[str]
    expected_immediate_signal: str
    expected_transfer_signal: str
    falsification_signal: str
    evidence_basis: list[str]
    validation_status: str = "UNVALIDATED_PILOT"


class InterventionPlan(BaseModel):
    plan_id: str
    intervention: InterventionSpec
    hypothesis_id: str
    rationale: list[str]
    verification_skill_id: str
    acquisition_task_ids: list[str] = Field(default_factory=list)
    transfer_task_ids: list[str] = Field(default_factory=list)
    retention_task_ids: list[str] = Field(default_factory=list)
    scientific_status: str = "UNVALIDATED_PILOT"
    engine_version: str = "intervention-intelligence-v1-pilot-2026-09"


class VerificationEvidence(BaseModel):
    stage: VerificationStage
    correct: bool | None = None
    independent: bool = True
    quality: str = "HIGH"
    task_id: str | None = None
    notes: str | None = None


class VerificationDecision(BaseModel):
    stage: VerificationStage
    outcome: VerificationOutcome
    usable_events: int = 0
    independent_events: int = 0
    positive_events: int = 0
    negative_events: int = 0
    rationale: list[str] = Field(default_factory=list)


class InterventionResponseDecision(BaseModel):
    hypothesis_id: str
    revision: HypothesisRevisionDirection
    verification: list[VerificationDecision]
    next_action: str
    rationale: list[str]
    scientific_status: str = "UNVALIDATED_PILOT"
    engine_version: str = "intervention-response-v1-pilot-2026-09"
