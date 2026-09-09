from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from readright.persistence.models import LearnerEventRecord, LearnerRecord, LearnerStateSnapshotRecord

PERSISTENCE_VERSION = "longitudinal-store-v1-pilot-2026-09"


def ensure_learner(db: Session, learner_id: str, language: str) -> LearnerRecord:
    learner = db.get(LearnerRecord, learner_id)
    if learner is None:
        learner = LearnerRecord(id=learner_id, language=language)
        db.add(learner)
        db.flush()
    elif learner.language != language:
        raise ValueError("Learner language does not match the existing longitudinal record.")
    return learner


def _next_sequence(db: Session, learner_id: str) -> int:
    current = db.scalar(
        select(func.max(LearnerEventRecord.sequence_no)).where(LearnerEventRecord.learner_id == learner_id)
    )
    return int(current or 0) + 1


def append_event(
    db: Session,
    *,
    learner_id: str,
    language: str,
    event_type: str,
    payload: dict,
    engine_version: str,
    source_session_id: str | None = None,
    skill_id: str | None = None,
    hypothesis_id: str | None = None,
    intervention_id: str | None = None,
    occurred_at: datetime | None = None,
) -> LearnerEventRecord:
    ensure_learner(db, learner_id, language)
    event = LearnerEventRecord(
        learner_id=learner_id,
        event_type=event_type,
        source_session_id=source_session_id,
        skill_id=skill_id,
        hypothesis_id=hypothesis_id,
        intervention_id=intervention_id,
        occurred_at=occurred_at or datetime.now(timezone.utc),
        sequence_no=_next_sequence(db, learner_id),
        payload=payload,
        engine_version=engine_version,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, learner_id: str) -> list[LearnerEventRecord]:
    return list(
        db.scalars(
            select(LearnerEventRecord)
            .where(LearnerEventRecord.learner_id == learner_id)
            .order_by(LearnerEventRecord.sequence_no.asc(), LearnerEventRecord.occurred_at.asc())
        )
    )


def assessment_evidence_from_events(events: list[LearnerEventRecord]) -> list[dict]:
    return [dict(event.payload) for event in events if event.event_type == "ASSESSMENT_EVIDENCE"]


def verification_events_from_events(events: list[LearnerEventRecord]) -> list[LearnerEventRecord]:
    return [event for event in events if event.event_type == "VERIFICATION_EVIDENCE"]


def hypothesis_revision_events(events: list[LearnerEventRecord]) -> list[LearnerEventRecord]:
    return [event for event in events if event.event_type == "HYPOTHESIS_REVISION"]


def save_snapshot(
    db: Session,
    *,
    learner_id: str,
    through_event_id: str | None,
    through_sequence_no: int,
    learner_state: dict,
    hypotheses: list,
    bottleneck: dict,
    verification: dict,
    engine_version: str,
    note: str | None = None,
) -> LearnerStateSnapshotRecord:
    snapshot = LearnerStateSnapshotRecord(
        learner_id=learner_id,
        through_event_id=through_event_id,
        through_sequence_no=through_sequence_no,
        learner_state=learner_state,
        hypotheses=hypotheses,
        bottleneck=bottleneck,
        verification=verification,
        engine_version=engine_version,
        note=note,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def latest_snapshot(db: Session, learner_id: str) -> LearnerStateSnapshotRecord | None:
    return db.scalar(
        select(LearnerStateSnapshotRecord)
        .where(LearnerStateSnapshotRecord.learner_id == learner_id)
        .order_by(LearnerStateSnapshotRecord.through_sequence_no.desc(), LearnerStateSnapshotRecord.created_at.desc())
        .limit(1)
    )
