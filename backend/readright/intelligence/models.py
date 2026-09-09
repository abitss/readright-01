from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class LearnerSkillState(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_DEMONSTRATED = "NOT_DEMONSTRATED"
    EMERGING = "EMERGING"
    FRAGILE = "FRAGILE"
    ACQUIRED = "ACQUIRED"
    INDEPENDENT = "INDEPENDENT"
    TRANSFERRED = "TRANSFERRED"
    RETAINED = "RETAINED"
    CONFLICTING = "CONFLICTING"


class EvidenceSupport(str, Enum):
    NONE = "NONE"
    LIMITED = "LIMITED"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    CONFLICTING = "CONFLICTING"


class HypothesisStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    WEAK = "WEAK"
    POSSIBLE = "POSSIBLE"
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"


class SkillStateRecord(BaseModel):
    skill_id: str
    state: LearnerSkillState
    evidence_support: EvidenceSupport
    usable_events: int = 0
    independent_events: int = 0
    positive_events: int = 0
    negative_events: int = 0
    rationale: list[str] = Field(default_factory=list)


class HypothesisRecord(BaseModel):
    hypothesis_id: str
    label: str
    status: HypothesisStatus
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    instruction_target: str | None = None


class BottleneckDecision(BaseModel):
    outcome: str
    primary_hypothesis: HypothesisRecord | None = None
    alternatives: list[HypothesisRecord] = Field(default_factory=list)
    next_evidence_needed: list[str] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)
    scientific_status: str = "UNVALIDATED_PILOT"
    engine_version: str = "learner-state-v1-pilot-2026-09"
