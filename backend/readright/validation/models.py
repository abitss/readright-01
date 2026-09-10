from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class StudyPhase(str, Enum):
    PILOT = "PILOT"
    CALIBRATION = "CALIBRATION"
    HOLDOUT_VALIDATION = "HOLDOUT_VALIDATION"
    EXTERNAL_VALIDATION = "EXTERNAL_VALIDATION"


class ClaimStatus(str, Enum):
    NOT_EVALUATED = "NOT_EVALUATED"
    EXPLORATORY_ONLY = "EXPLORATORY_ONLY"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    SUPPORTED_FOR_DEFINED_USE = "SUPPORTED_FOR_DEFINED_USE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ValidationMetric(BaseModel):
    metric: str
    value: float | None = None
    lower_ci: float | None = None
    upper_ci: float | None = None
    n: int | None = None
    subgroup: str | None = None
    notes: list[str] = Field(default_factory=list)


class SampleDescription(BaseModel):
    n_total: int
    grades: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    schools: int | None = None
    states_or_regions: list[str] = Field(default_factory=list)
    sampling_method: str
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    subgroup_fields: list[str] = Field(default_factory=list)


class StudyProtocol(BaseModel):
    study_id: str
    title: str
    phase: StudyPhase
    instrument_version: str
    engine_version: str
    intended_use: str
    primary_questions: list[str]
    sample: SampleDescription
    preregistered: bool = False
    locked_before_analysis: bool = False
    external_criterion: str | None = None
    planned_metrics: list[str]
    minimum_reporting: list[str]
    notes: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    study_id: str
    instrument_version: str
    phase: StudyPhase
    claim_status: ClaimStatus
    metrics: list[ValidationMetric]
    limitations: list[str]
    decision: str
    approved_by: list[str] = Field(default_factory=list)
    scientific_status: str = "RESEARCH_ONLY"
