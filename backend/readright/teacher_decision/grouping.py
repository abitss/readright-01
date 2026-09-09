from __future__ import annotations

from collections import defaultdict
from uuid import uuid4

from readright.teacher_decision.models import (
    ClassPlan,
    InstructionGroup,
    LearnerTeacherDecision,
    RotationBlock,
    TeacherDecisionOutcome,
)


def build_instruction_groups(decisions: list[LearnerTeacherDecision]) -> list[InstructionGroup]:
    buckets: dict[tuple, list[LearnerTeacherDecision]] = defaultdict(list)

    for decision in decisions:
        if decision.outcome == TeacherDecisionOutcome.VERIFY_DUE and decision.verify:
            key = ("VERIFY", decision.verify.stage, decision.why.headline)
        elif decision.outcome == TeacherDecisionOutcome.ACTION_READY and decision.do:
            key = ("TEACH", decision.do.intervention_id, decision.why.headline)
        elif decision.outcome in {TeacherDecisionOutcome.MORE_EVIDENCE, TeacherDecisionOutcome.CONFLICTING}:
            key = ("EVIDENCE", decision.outcome.value, decision.why.headline)
        else:
            key = ("NO_ACTION", decision.outcome.value, decision.why.headline)
        buckets[key].append(decision)

    groups: list[InstructionGroup] = []
    for key, members in buckets.items():
        kind = key[0]
        if kind == "VERIFY":
            priority = 1
            label = f"Verify {key[1].title().lower()}"
            reason = "These learners are ready for the same verification stage."
            verification_stage = key[1]
            intervention_id = None
        elif kind == "TEACH":
            priority = 2
            label = members[0].do.title if members[0].do else "Teacher action"
            reason = "These learners share the same current actionable barrier and intervention routine."
            verification_stage = None
            intervention_id = members[0].do.intervention_id if members[0].do else None
        elif kind == "EVIDENCE":
            priority = 3
            label = "Focused evidence check"
            reason = "Do not group these learners for remediation yet; collect distinguishing evidence first."
            verification_stage = None
            intervention_id = None
        else:
            priority = 4
            label = "Independent / monitor"
            reason = "No immediate teacher-led action is supported by current evidence."
            verification_stage = None
            intervention_id = None

        groups.append(
            InstructionGroup(
                group_id=str(uuid4()),
                label=label,
                learner_ids=sorted(member.learner_id for member in members),
                intervention_id=intervention_id,
                verification_stage=verification_stage,
                priority=priority,
                reason=reason,
            )
        )

    return sorted(groups, key=lambda group: (group.priority, -len(group.learner_ids), group.label))


def build_30_minute_plan(decisions: list[LearnerTeacherDecision], total_minutes: int = 30) -> ClassPlan:
    groups = build_instruction_groups(decisions)
    active = [group for group in groups if group.priority <= 3]

    rotations: list[RotationBlock] = []
    order = 1
    remaining = total_minutes

    launch = min(3, remaining)
    if launch:
        rotations.append(
            RotationBlock(
                order=order,
                minutes=launch,
                title="Launch",
                action="Set expectations, materials, and independent work for learners not currently with the teacher.",
            )
        )
        order += 1
        remaining -= launch

    # Preserve a short closure. Up to three teacher-led rotations avoids an unusable plan.
    closure = 3 if remaining >= 6 else 0
    usable_for_groups = max(0, remaining - closure)
    selected = active[:3]

    if selected and usable_for_groups:
        base = usable_for_groups // len(selected)
        extra = usable_for_groups % len(selected)
        for index, group in enumerate(selected):
            minutes = base + (1 if index < extra else 0)
            action = {
                1: f"Run the due {group.verification_stage or 'verification'} check using unseen material. Record independence and evidence quality.",
                2: f"Teach the approved routine for {group.label}. Keep prompts and assistance observable.",
                3: "Run a short focused probe only. Do not begin remediation until the competing explanations are better separated.",
            }[group.priority]
            rotations.append(
                RotationBlock(
                    order=order,
                    minutes=minutes,
                    group_id=group.group_id,
                    title=group.label,
                    action=action,
                    learner_ids=group.learner_ids,
                )
            )
            order += 1

    if closure:
        rotations.append(
            RotationBlock(
                order=order,
                minutes=closure,
                title="Close and record",
                action="Record fidelity, prompts, notable observations, and any evidence that changes the next decision.",
            )
        )

    selected_ids = {learner_id for group in selected for learner_id in group.learner_ids}
    deferred = sorted(
        decision.learner_id
        for decision in decisions
        if decision.learner_id not in selected_ids
        and decision.outcome != TeacherDecisionOutcome.NO_ACTION
    )

    return ClassPlan(
        total_minutes=total_minutes,
        groups=groups,
        rotations=rotations,
        deferred_learner_ids=deferred,
    )
