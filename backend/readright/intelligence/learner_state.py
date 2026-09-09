from __future__ import annotations

from readright.intelligence.models import EvidenceSupport, LearnerSkillState, SkillStateRecord

USABLE = {"HIGH", "MODERATE"}


def derive_skill_state(skill_id: str, evidence: list[dict]) -> SkillStateRecord:
    events = [e for e in evidence if e.get("skill_id") == skill_id]
    usable = [e for e in events if e.get("quality") in USABLE]
    independent = [e for e in usable if e.get("assistance") == "none"]
    pos = [e for e in independent if e.get("correct") is True]
    neg = [e for e in independent if e.get("correct") is False]

    rationale: list[str] = []

    if not events:
        return SkillStateRecord(skill_id=skill_id, state=LearnerSkillState.UNKNOWN, evidence_support=EvidenceSupport.NONE)

    if not usable:
        rationale.append("Observed events were not usable for learner-state inference.")
        return SkillStateRecord(skill_id=skill_id, state=LearnerSkillState.UNKNOWN, evidence_support=EvidenceSupport.LIMITED, usable_events=0, rationale=rationale)

    if not independent:
        rationale.append("Only assisted usable evidence is available; independent performance remains unknown.")
        return SkillStateRecord(skill_id=skill_id, state=LearnerSkillState.EMERGING, evidence_support=EvidenceSupport.LIMITED, usable_events=len(usable), rationale=rationale)

    if pos and neg:
        rationale.append("Independent usable evidence contains both success and failure.")
        return SkillStateRecord(
            skill_id=skill_id,
            state=LearnerSkillState.CONFLICTING,
            evidence_support=EvidenceSupport.CONFLICTING,
            usable_events=len(usable), independent_events=len(independent),
            positive_events=len(pos), negative_events=len(neg), rationale=rationale,
        )

    if len(pos) >= 2:
        rationale.append("At least two independent usable positive observations are present.")
        return SkillStateRecord(
            skill_id=skill_id,
            state=LearnerSkillState.INDEPENDENT,
            evidence_support=EvidenceSupport.STRONG,
            usable_events=len(usable), independent_events=len(independent),
            positive_events=len(pos), negative_events=0, rationale=rationale,
        )

    if len(pos) == 1:
        rationale.append("One independent usable positive observation is present; replication is still needed.")
        return SkillStateRecord(
            skill_id=skill_id,
            state=LearnerSkillState.EMERGING,
            evidence_support=EvidenceSupport.LIMITED,
            usable_events=len(usable), independent_events=len(independent),
            positive_events=1, negative_events=0, rationale=rationale,
        )

    if len(neg) >= 2:
        rationale.append("At least two independent usable negative observations are present.")
        return SkillStateRecord(
            skill_id=skill_id,
            state=LearnerSkillState.NOT_DEMONSTRATED,
            evidence_support=EvidenceSupport.STRONG,
            usable_events=len(usable), independent_events=len(independent),
            positive_events=0, negative_events=len(neg), rationale=rationale,
        )

    rationale.append("One independent usable negative observation is present; replication is required before interpretation.")
    return SkillStateRecord(
        skill_id=skill_id,
        state=LearnerSkillState.FRAGILE,
        evidence_support=EvidenceSupport.LIMITED,
        usable_events=len(usable), independent_events=len(independent),
        positive_events=0, negative_events=len(neg), rationale=rationale,
    )


def derive_learner_state(evidence: list[dict]) -> dict[str, SkillStateRecord]:
    skill_ids = sorted({e.get("skill_id") for e in evidence if e.get("skill_id")})
    return {skill_id: derive_skill_state(skill_id, evidence) for skill_id in skill_ids}
