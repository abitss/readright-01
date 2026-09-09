from __future__ import annotations

from readright.persistence.models import LearnerEventRecord
from readright.teacher_decision.engine import build_teacher_decision
from readright.teacher_decision.grouping import build_30_minute_plan, build_instruction_groups
from readright.teacher_decision.models import TeacherDecisionOutcome


def ev(sequence_no: int, event_type: str, payload: dict, *, skill_id=None, hypothesis_id=None, intervention_id=None):
    return LearnerEventRecord(
        id=f"e-{sequence_no}",
        learner_id="learner",
        event_type=event_type,
        source_session_id=None,
        skill_id=skill_id,
        hypothesis_id=hypothesis_id,
        intervention_id=intervention_id,
        sequence_no=sequence_no,
        payload=payload,
        engine_version="test",
    )


def supported_blending_evidence(start: int = 1):
    return [
        ev(start, "ASSESSMENT_EVIDENCE", {"skill_id": "EN-GPC", "correct": True, "quality": "HIGH", "assistance": "none"}, skill_id="EN-GPC"),
        ev(start + 1, "ASSESSMENT_EVIDENCE", {"skill_id": "EN-GPC", "correct": True, "quality": "HIGH", "assistance": "none"}, skill_id="EN-GPC"),
        ev(start + 2, "ASSESSMENT_EVIDENCE", {"skill_id": "EN-PHON-BLEND-CVC", "correct": False, "quality": "HIGH", "assistance": "none"}, skill_id="EN-PHON-BLEND-CVC"),
        ev(start + 3, "ASSESSMENT_EVIDENCE", {"skill_id": "EN-PHON-BLEND-CVC", "correct": False, "quality": "HIGH", "assistance": "none"}, skill_id="EN-PHON-BLEND-CVC"),
    ]


def test_supported_barrier_becomes_why_do_verify_action():
    decision = build_teacher_decision("l1", "en", supported_blending_evidence())
    assert decision.outcome == TeacherDecisionOutcome.ACTION_READY
    assert "blending" in decision.why.headline.lower()
    assert decision.why.evidence_strength == "Strong"
    assert decision.do is not None
    assert decision.do.intervention_id == "INT-BLEND-EXPLICIT"
    assert decision.verify is not None
    assert decision.verify.status == "PLANNED_AFTER_INTERVENTION"


def test_plan_creation_alone_does_not_move_to_verify():
    events = supported_blending_evidence()
    events.append(
        ev(
            5,
            "INTERVENTION_PLAN_CREATED",
            {
                "acquisition_task_ids": ["a1", "a2"],
                "transfer_task_ids": ["t1", "t2"],
                "retention_task_ids": ["r1", "r2"],
            },
            skill_id="EN-PHON-BLEND-CVC",
            hypothesis_id="H-BLEND",
            intervention_id="INT-BLEND-EXPLICIT",
        )
    )
    decision = build_teacher_decision("l1", "en", events)
    assert decision.outcome == TeacherDecisionOutcome.ACTION_READY
    assert decision.verify.status == "PLANNED_AFTER_INTERVENTION"


def test_delivery_moves_teacher_to_independence_verification():
    events = supported_blending_evidence()
    events.extend([
        ev(5, "INTERVENTION_PLAN_CREATED", {
            "acquisition_task_ids": ["a1", "a2"],
            "transfer_task_ids": ["t1", "t2"],
            "retention_task_ids": ["r1", "r2"],
        }, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
        ev(6, "INTERVENTION_DELIVERED", {"fidelity": "ACCEPTABLE", "minutes_delivered": 8}, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
    ])
    decision = build_teacher_decision("l1", "en", events)
    assert decision.outcome == TeacherDecisionOutcome.VERIFY_DUE
    assert decision.verify.stage == "INDEPENDENCE"
    assert decision.verify.task_ids == ["a1", "a2"]


def test_independence_pass_moves_to_transfer():
    events = supported_blending_evidence()
    events.extend([
        ev(5, "INTERVENTION_PLAN_CREATED", {
            "acquisition_task_ids": ["a1", "a2"],
            "transfer_task_ids": ["t1", "t2"],
            "retention_task_ids": ["r1", "r2"],
        }, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
        ev(6, "INTERVENTION_DELIVERED", {"fidelity": "ACCEPTABLE", "minutes_delivered": 8}, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
        ev(7, "VERIFICATION_EVIDENCE", {"stage": "INDEPENDENCE", "correct": True, "independent": True, "quality": "HIGH"}, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
    ])
    decision = build_teacher_decision("l1", "en", events)
    assert decision.outcome == TeacherDecisionOutcome.VERIFY_DUE
    assert decision.verify.stage == "TRANSFER"
    assert decision.verify.task_ids == ["t1", "t2"]


def test_transfer_pass_waits_for_later_retention_instead_of_consuming_class_time():
    events = supported_blending_evidence()
    events.extend([
        ev(5, "INTERVENTION_PLAN_CREATED", {
            "acquisition_task_ids": ["a1", "a2"],
            "transfer_task_ids": ["t1", "t2"],
            "retention_task_ids": ["r1", "r2"],
        }, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
        ev(6, "INTERVENTION_DELIVERED", {"fidelity": "ACCEPTABLE", "minutes_delivered": 8}, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
        ev(7, "VERIFICATION_EVIDENCE", {"stage": "INDEPENDENCE", "correct": True, "independent": True, "quality": "HIGH"}, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
        ev(8, "VERIFICATION_EVIDENCE", {"stage": "TRANSFER", "correct": True, "independent": True, "quality": "HIGH"}, skill_id="EN-PHON-BLEND-CVC", hypothesis_id="H-BLEND", intervention_id="INT-BLEND-EXPLICIT"),
    ])
    decision = build_teacher_decision("l1", "en", events)
    assert decision.outcome == TeacherDecisionOutcome.NO_ACTION
    assert decision.verify.stage == "RETENTION"
    assert decision.verify.status == "DUE_LATER"


def test_same_intervention_groups_learners_together():
    d1 = build_teacher_decision("l1", "en", supported_blending_evidence())
    d2 = build_teacher_decision("l2", "en", supported_blending_evidence())
    groups = build_instruction_groups([d1, d2])
    teach = [g for g in groups if g.priority == 2]
    assert len(teach) == 1
    assert teach[0].learner_ids == ["l1", "l2"]
    assert teach[0].recommended_minutes == 8


def test_30_minute_plan_does_not_inflate_8_minute_intervention():
    d1 = build_teacher_decision("l1", "en", supported_blending_evidence())
    d2 = build_teacher_decision("l2", "en", supported_blending_evidence())
    plan = build_30_minute_plan([d1, d2], total_minutes=30)
    teaching = [r for r in plan.rotations if r.group_id is not None]
    assert len(teaching) == 1
    assert teaching[0].minutes == 8
    assert sum(rotation.minutes for rotation in plan.rotations) == 30
    assert any(rotation.title == "Independent practice and teacher observation" for rotation in plan.rotations)
