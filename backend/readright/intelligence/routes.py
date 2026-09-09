from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from readright.intelligence.intervention_models import (
    InterventionFidelity,
    VerificationEvidence,
)
from readright.intelligence.intervention_response import interpret_intervention_response
from readright.intelligence.intervention_selector import select_intervention_plan

router = APIRouter()


class InterventionPlanRequest(BaseModel):
    language: str = "en"
    evidence: list[dict] = Field(default_factory=list)


class InterventionResponseRequest(BaseModel):
    hypothesis_id: str
    fidelity: InterventionFidelity
    verification_events: list[VerificationEvidence] = Field(default_factory=list)


@router.post("/plan")
def create_intervention_plan(request: InterventionPlanRequest) -> dict:
    plan = select_intervention_plan(request.evidence, request.language)
    if plan is None:
        return {
            "plan": None,
            "outcome": "NO_SINGLE_ACTIONABLE_INTERVENTION",
            "scientific_status": "UNVALIDATED_PILOT",
            "message": "ReadRight does not prescribe an intervention when one instructional hypothesis is not sufficiently isolated.",
        }
    return {
        "plan": plan.model_dump(),
        "outcome": "INTERVENTION_PLAN_READY",
        "scientific_status": "UNVALIDATED_PILOT",
    }


@router.post("/verify")
def verify_intervention_response(request: InterventionResponseRequest) -> dict:
    decision = interpret_intervention_response(
        hypothesis_id=request.hypothesis_id,
        fidelity=request.fidelity,
        verification_events=request.verification_events,
    )
    return decision.model_dump()
