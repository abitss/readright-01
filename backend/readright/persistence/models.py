from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from readright.persistence.database import Base


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class LearnerRecord(Base):
    __tablename__ = "learners"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    events: Mapped[list["LearnerEventRecord"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    snapshots: Mapped[list["LearnerStateSnapshotRecord"]] = relationship(back_populates="learner", cascade="all, delete-orphan")


class LearnerEventRecord(Base):
    __tablename__ = "learner_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    skill_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    hypothesis_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    intervention_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True, nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    engine_version: Mapped[str] = mapped_column(String(128), nullable=False)

    learner: Mapped[LearnerRecord] = relationship(back_populates="events")


class LearnerStateSnapshotRecord(Base):
    __tablename__ = "learner_state_snapshots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    learner_id: Mapped[str] = mapped_column(ForeignKey("learners.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True, nullable=False)
    through_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    through_sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    learner_state: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    hypotheses: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    bottleneck: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    verification: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    engine_version: Mapped[str] = mapped_column(String(128), nullable=False)
    scientific_status: Mapped[str] = mapped_column(String(64), nullable=False, default="UNVALIDATED_PILOT")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    learner: Mapped[LearnerRecord] = relationship(back_populates="snapshots")
