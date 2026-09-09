from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from readright.intelligence.hypotheses import ENGLISH_HYPOTHESES
from readright.intelligence.intervention_models import (
    InterventionFidelity,
    VerificationEvidence,
)
from readright.intelligence.intervention_response import interpret_intervention_response
from readright.intelligence.intervention_selector import select_intervention_plan
from readright.intelligence.longitudinal import LONGITUDINAL_ENGINE_VERSION, replay_longitudinal
from readright.persistence.database import get_db
from readright.persistence.store import append_event, list_events, save_snapshot

router = APIRouter()


class InterventionPlanRequest(BaseModel):
    language: str = "en"
    evidence: list[dict] = Field(default_factory=list)
    learner_id: str | None = None


class InterventionResponseRequest(BaseModel):
    hypothesis_id: str
    fidelity: InterventionFidelity
    verification_events: list[VerificationEvidence] = Field(default_factory=list)
    learner_id: str | None = None
    language: str = "en"
    intervention_id: str | None = None


def _snapshot_after_persist(db: Session, learner_id: str, language: str, note: str) -> dict:
    events = list_events(db, learner_id)
    replay = replay_longitudinal(events, language)
    last = events[-1] if events else None
    snapshot = save_snapshot(
        db,
        learner_id=learner_id,
        through_event_id=last.id if last else None,
        through_sequence_no=last.sequence_no if last else 0,
        learner_state=replay["learner_state"],
        hypotheses=replay["hypotheses"],
        bottleneck=replay["bottleneck"],
        verification=replay["verification"],
        engine_version=LONGITUDINAL_ENGINE_VERSION,
        note=note,
    )
    return {**replay, "snapshot_id": snapshot.id, "through_sequence_no": snapshot.through_sequence_no}


@router.post("/plan")
def create_intervention_plan(request: InterventionPlanRequest, db: Session = Depends(get_db)) -> dict:
    plan = select_intervention_plan(request.evidence, request.language)
    if plan is None:
        return {
            "plan": None,
            "outcome": "NO_SINGLE_ACTIONABLE_INTERVENTION",
            "scientific_status": "UNVALIDATED_PILOT",
            "message": "ReadRight does not prescribe an intervention when one instructional hypothesis is not sufficiently isolated.",
        }

    persisted_event_id = None
    if request.learner_id:
        try:
            event = append_event(
                db,
                learner_id=request.learner_id,
                language=request.language,
                event_type="INTERVENTION_PLAN_CREATED",
                payload=plan.model_dump(mode="json"),
                engine_version=plan.engine_version,
                skill_id=plan.verification_skill_id,
                hypothesis_id=plan.hypothesis_id,
                intervention_id=plan.intervention.intervention_id,
            )
            persisted_event_id = event.id
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "plan": plan.model_dump(),
        "outcome": "INTERVENTION_PLAN_READY",
        "persistent_event_id": persisted_event_id,
        "scientific_status": "UNVALIDATED_PILOT",
    }


@router.post("/verify")
def verify_intervention_response(request: InterventionResponseRequest, db: Session = Depends(get_db)) -> dict:
    decision = interpret_intervention_response(
        hypothesis_id=request.hypothesis_id,
        fidelity=request.fidelity,
        verification_events=request.verification_events,
    )

    persisted_event_ids: list[str] = []
    current = None
    if request.learner_id:
        spec = ENGLISH_HYPOTHESES.get(request.hypothesis_id) if request.language == "en" else None
        target_skill_id = spec.target_skill if spec else None
        if target_skill_id is None:
            raise HTTPException(
                status_code=422,
                detail="Cannot persist verification without a language-specific hypothesis-to-skill mapping.",
            )

        try:
            for verification in request.verification_events:
                event = append_event(
                    db,
                    learner_id=request.learner_id,
                    language=request.language,
                    event_type="VERIFICATION_EVIDENCE",
                    payload={
                        "stage": verification.stage.value,
                        "correct": verification.correct,
                        "independent": verification.independent,
                        "quality": verification.quality,
                        "task_id": verification.task_id,
                        "notes": verification.notes,
                        "fidelity": request.fidelity.value,
                    },
                    engine_version=decision.engine_version,
                    skill_id=target_skill_id,
                    hypothesis_id=request.hypothesis_id,
                    intervention_id=request.intervention_id,
                )
                persisted_event_ids.append(event.id)

            revision_event = append_event(
                db,
                learner_id=request.learner_id,
                language=request.language,
                event_type="HYPOTHESIS_REVISION",
                payload=decision.model_dump(mode="json"),
                engine_version=decision.engine_version,
                skill_id=target_skill_id,
                hypothesis_id=request.hypothesis_id,
                intervention_id=request.intervention_id,
            )
            persisted_event_ids.append(revision_event.id)
            current = _snapshot_after_persist(
                db,
                request.learner_id,
                request.language,
                note="Intervention verification and hypothesis revision appended.",
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        **decision.model_dump(),
        "persistent_event_ids": persisted_event_ids,
        "current": current,
    }
