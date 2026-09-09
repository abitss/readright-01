from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from readright.persistence.database import get_db
from readright.persistence.models import LearnerRecord
from readright.persistence.store import list_events
from readright.teacher_decision.engine import build_teacher_decision
from readright.teacher_decision.grouping import build_30_minute_plan

router = APIRouter()


class ClassPlanRequest(BaseModel):
    learner_ids: list[str] = Field(min_length=1)
    total_minutes: int = Field(default=30, ge=15, le=90)


@router.get("/learners/{learner_id}")
def get_teacher_decision(learner_id: str, db: Session = Depends(get_db)) -> dict:
    learner = db.get(LearnerRecord, learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    events = list_events(db, learner_id)
    decision = build_teacher_decision(learner_id, learner.language, events)
    return decision.model_dump(mode="json")


@router.post("/class-plan")
def create_class_plan(request: ClassPlanRequest, db: Session = Depends(get_db)) -> dict:
    decisions = []
    missing: list[str] = []
    for learner_id in request.learner_ids:
        learner = db.get(LearnerRecord, learner_id)
        if learner is None:
            missing.append(learner_id)
            continue
        decisions.append(build_teacher_decision(learner_id, learner.language, list_events(db, learner_id)))

    if missing:
        raise HTTPException(status_code=404, detail={"message": "Some learners were not found", "learner_ids": missing})

    plan = build_30_minute_plan(decisions, total_minutes=request.total_minutes)
    return {
        "plan": plan.model_dump(mode="json"),
        "decisions": [decision.model_dump(mode="json") for decision in decisions],
        "warning": "Temporary instructional grouping only. Groups must change as evidence and verification change.",
    }
