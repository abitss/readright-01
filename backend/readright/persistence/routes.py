from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from readright.intelligence.intervention_models import VerificationStage
from readright.intelligence.longitudinal import LONGITUDINAL_ENGINE_VERSION, replay_longitudinal
from readright.persistence.database import get_db
from readright.persistence.models import LearnerRecord
from readright.persistence.store import append_event, latest_snapshot, list_events, save_snapshot

router = APIRouter()


class VerificationEventRequest(BaseModel):
    language: str = "en"
    skill_id: str
    stage: VerificationStage
    correct: bool | None = None
    independent: bool = True
    quality: str = "HIGH"
    task_id: str | None = None
    hypothesis_id: str | None = None
    intervention_id: str | None = None
    notes: str | None = None
    occurred_at: datetime | None = None


class TeacherObservationRequest(BaseModel):
    language: str = "en"
    skill_id: str | None = None
    observation_type: str
    note: str
    structured_tags: list[str] = Field(default_factory=list)
    occurred_at: datetime | None = None


def _rebuild_and_snapshot(db: Session, learner_id: str, language: str, note: str | None = None) -> dict:
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


@router.post("/{learner_id}/verification")
def append_verification(learner_id: str, request: VerificationEventRequest, db: Session = Depends(get_db)) -> dict:
    payload = {
        "stage": request.stage.value,
        "correct": request.correct,
        "independent": request.independent,
        "quality": request.quality,
        "task_id": request.task_id,
        "notes": request.notes,
    }
    try:
        event = append_event(
            db,
            learner_id=learner_id,
            language=request.language,
            event_type="VERIFICATION_EVIDENCE",
            payload=payload,
            engine_version=LONGITUDINAL_ENGINE_VERSION,
            skill_id=request.skill_id,
            hypothesis_id=request.hypothesis_id,
            intervention_id=request.intervention_id,
            occurred_at=request.occurred_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    state = _rebuild_and_snapshot(db, learner_id, request.language, note="Verification evidence appended.")
    return {"event_id": event.id, "sequence_no": event.sequence_no, "current": state}


@router.post("/{learner_id}/observations")
def append_teacher_observation(learner_id: str, request: TeacherObservationRequest, db: Session = Depends(get_db)) -> dict:
    try:
        event = append_event(
            db,
            learner_id=learner_id,
            language=request.language,
            event_type="TEACHER_OBSERVATION",
            payload={
                "observation_type": request.observation_type,
                "note": request.note,
                "structured_tags": request.structured_tags,
            },
            engine_version=LONGITUDINAL_ENGINE_VERSION,
            skill_id=request.skill_id,
            occurred_at=request.occurred_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"event_id": event.id, "sequence_no": event.sequence_no, "status": "APPENDED"}


@router.get("/{learner_id}/timeline")
def get_timeline(learner_id: str, db: Session = Depends(get_db)) -> dict:
    learner = db.get(LearnerRecord, learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    events = list_events(db, learner_id)
    return {
        "learner_id": learner_id,
        "language": learner.language,
        "events": [
            {
                "id": e.id,
                "sequence_no": e.sequence_no,
                "event_type": e.event_type,
                "skill_id": e.skill_id,
                "hypothesis_id": e.hypothesis_id,
                "intervention_id": e.intervention_id,
                "source_session_id": e.source_session_id,
                "occurred_at": e.occurred_at.isoformat(),
                "payload": e.payload,
                "engine_version": e.engine_version,
            }
            for e in events
        ],
    }


@router.get("/{learner_id}/state")
def get_current_state(learner_id: str, db: Session = Depends(get_db)) -> dict:
    learner = db.get(LearnerRecord, learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    events = list_events(db, learner_id)
    return replay_longitudinal(events, learner.language)


@router.post("/{learner_id}/rebuild")
def rebuild_state(learner_id: str, db: Session = Depends(get_db)) -> dict:
    learner = db.get(LearnerRecord, learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    return _rebuild_and_snapshot(db, learner_id, learner.language, note="Manual deterministic replay.")


@router.get("/{learner_id}/snapshots/latest")
def get_latest_snapshot(learner_id: str, db: Session = Depends(get_db)) -> dict:
    learner = db.get(LearnerRecord, learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    snapshot = latest_snapshot(db, learner_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No learner-state snapshot exists yet")
    return {
        "id": snapshot.id,
        "through_sequence_no": snapshot.through_sequence_no,
        "created_at": snapshot.created_at.isoformat(),
        "learner_state": snapshot.learner_state,
        "hypotheses": snapshot.hypotheses,
        "bottleneck": snapshot.bottleneck,
        "verification": snapshot.verification,
        "engine_version": snapshot.engine_version,
        "scientific_status": snapshot.scientific_status,
    }
