from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from readright.intelligence.longitudinal import derive_longitudinal_state, replay_longitudinal
from readright.intelligence.models import HypothesisStatus, LearnerSkillState
from readright.persistence.database import Base
from readright.persistence.store import append_event, list_events, save_snapshot


def _db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


def _assessment(db, learner, skill, task, correct):
    return append_event(
        db,
        learner_id=learner,
        language="en",
        event_type="ASSESSMENT_EVIDENCE",
        payload={
            "task_id": task,
            "skill_id": skill,
            "correct": correct,
            "assistance": "none",
            "quality": "HIGH",
            "teacher_confirmed": True,
        },
        engine_version="test-assessment",
        skill_id=skill,
    )


def _verification(db, learner, skill, stage, correct):
    return append_event(
        db,
        learner_id=learner,
        language="en",
        event_type="VERIFICATION_EVIDENCE",
        payload={
            "stage": stage,
            "correct": correct,
            "independent": True,
            "quality": "HIGH",
        },
        engine_version="test-verification",
        skill_id=skill,
    )


def test_event_store_is_append_only_and_monotonic():
    db = _db()
    first = _assessment(db, "L1", "EN-GPC", "t1", True)
    second = _assessment(db, "L1", "EN-GPC", "t2", True)
    events = list_events(db, "L1")
    assert first.sequence_no == 1
    assert second.sequence_no == 2
    assert [e.id for e in events] == [first.id, second.id]


def test_retention_requires_independence_and_transfer_not_one_retention_event():
    db = _db()
    _assessment(db, "L2", "EN-GPC", "t1", True)
    _assessment(db, "L2", "EN-GPC", "t2", True)
    _verification(db, "L2", "EN-GPC", "RETENTION", True)

    state = derive_longitudinal_state(list_events(db, "L2"), "en")["EN-GPC"]
    assert state.state == LearnerSkillState.INDEPENDENT


def test_staged_verification_can_reach_retained():
    db = _db()
    _assessment(db, "L3", "EN-GPC", "t1", True)
    _assessment(db, "L3", "EN-GPC", "t2", True)
    _verification(db, "L3", "EN-GPC", "ACQUISITION", True)
    _verification(db, "L3", "EN-GPC", "INDEPENDENCE", True)
    _verification(db, "L3", "EN-GPC", "TRANSFER", True)
    _verification(db, "L3", "EN-GPC", "RETENTION", True)

    state = derive_longitudinal_state(list_events(db, "L3"), "en")["EN-GPC"]
    assert state.state == LearnerSkillState.RETAINED


def test_later_retention_failure_reopens_current_state_but_history_remains():
    db = _db()
    _assessment(db, "L4", "EN-GPC", "t1", True)
    _assessment(db, "L4", "EN-GPC", "t2", True)
    _verification(db, "L4", "EN-GPC", "INDEPENDENCE", True)
    _verification(db, "L4", "EN-GPC", "TRANSFER", True)
    _verification(db, "L4", "EN-GPC", "RETENTION", True)
    _verification(db, "L4", "EN-GPC", "RETENTION", False)

    events = list_events(db, "L4")
    state = derive_longitudinal_state(events, "en")["EN-GPC"]
    assert state.state == LearnerSkillState.FRAGILE
    retention_events = [e for e in events if e.event_type == "VERIFICATION_EVIDENCE" and e.payload.get("stage") == "RETENTION"]
    assert [e.payload["correct"] for e in retention_events] == [True, False]


def test_hypothesis_revision_survives_deterministic_replay():
    db = _db()
    # Secure GPC reduces an alternative explanation.
    _assessment(db, "L5", "EN-GPC", "g1", True)
    _assessment(db, "L5", "EN-GPC", "g2", True)
    # Repeated blending difficulty supports H-BLEND under v1 rules.
    _assessment(db, "L5", "EN-PHON-BLEND-CVC", "b1", False)
    _assessment(db, "L5", "EN-PHON-BLEND-CVC", "b2", False)

    before = replay_longitudinal(list_events(db, "L5"), "en")
    before_h = next(h for h in before["hypotheses"] if h["hypothesis_id"] == "H-BLEND")
    assert before_h["status"] == HypothesisStatus.SUPPORTED.value

    append_event(
        db,
        learner_id="L5",
        language="en",
        event_type="HYPOTHESIS_REVISION",
        payload={"revision": "WEAKEN", "rationale": ["Predicted response did not occur."]},
        engine_version="intervention-response-test",
        skill_id="EN-PHON-BLEND-CVC",
        hypothesis_id="H-BLEND",
        intervention_id="INT-BLEND",
    )

    after = replay_longitudinal(list_events(db, "L5"), "en")
    after_h = next(h for h in after["hypotheses"] if h["hypothesis_id"] == "H-BLEND")
    assert after_h["status"] == HypothesisStatus.WEAK.value
    assert after["hypothesis_revisions"][-1]["revision"] == "WEAKEN"


def test_snapshot_is_a_versioned_cache_not_source_of_truth():
    db = _db()
    _assessment(db, "L6", "EN-GPC", "t1", True)
    _assessment(db, "L6", "EN-GPC", "t2", True)
    events = list_events(db, "L6")
    replay = replay_longitudinal(events, "en")
    snapshot = save_snapshot(
        db,
        learner_id="L6",
        through_event_id=events[-1].id,
        through_sequence_no=events[-1].sequence_no,
        learner_state=replay["learner_state"],
        hypotheses=replay["hypotheses"],
        bottleneck=replay["bottleneck"],
        verification=replay["verification"],
        engine_version=replay["engine_version"],
        note="test",
    )
    rebuilt = replay_longitudinal(list_events(db, "L6"), "en")
    assert snapshot.learner_state == rebuilt["learner_state"]
    assert snapshot.through_sequence_no == 2
