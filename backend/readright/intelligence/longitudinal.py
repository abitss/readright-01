from __future__ import annotations

from dataclasses import dataclass

from readright.intelligence.bottleneck import decide_bottleneck
from readright.intelligence.hypotheses import evaluate_english_hypotheses
from readright.intelligence.learner_state import derive_learner_state
from readright.intelligence.models import LearnerSkillState, SkillStateRecord
from readright.persistence.models import LearnerEventRecord
from readright.persistence.store import assessment_evidence_from_events, verification_events_from_events

LONGITUDINAL_ENGINE_VERSION = "longitudinal-state-v1-pilot-2026-09"
USABLE_VERIFICATION_QUALITIES = {"HIGH", "MODERATE"}


@dataclass(frozen=True)
class VerificationStageSummary:
    stage: str
    usable: int
    positive: int
    negative: int
    conflicting: bool


def _verification_by_skill(events: list[LearnerEventRecord]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for event in verification_events_from_events(events):
        if not event.skill_id:
            continue
        grouped.setdefault(event.skill_id, []).append(dict(event.payload))
    return grouped


def _stage_summary(events: list[dict], stage: str) -> VerificationStageSummary:
    stage_events = [e for e in events if e.get("stage") == stage and e.get("quality") in USABLE_VERIFICATION_QUALITIES]
    positives = [e for e in stage_events if e.get("correct") is True and e.get("independent", True)]
    negatives = [e for e in stage_events if e.get("correct") is False]
    return VerificationStageSummary(
        stage=stage,
        usable=len(stage_events),
        positive=len(positives),
        negative=len(negatives),
        conflicting=bool(positives and negatives),
    )


def _apply_longitudinal_verification(base: SkillStateRecord, verification_events: list[dict]) -> SkillStateRecord:
    if not verification_events:
        return base

    independence = _stage_summary(verification_events, "INDEPENDENCE")
    transfer = _stage_summary(verification_events, "TRANSFER")
    retention = _stage_summary(verification_events, "RETENTION")

    rationale = list(base.rationale)
    state = base.state

    if independence.conflicting or transfer.conflicting or retention.conflicting:
        rationale.append("Longitudinal verification contains conflicting usable evidence.")
        return base.model_copy(update={
            "state": LearnerSkillState.CONFLICTING,
            "rationale": rationale,
        })

    # Later negative evidence can reopen a state. Historical success remains in the ledger.
    if retention.negative > 0:
        rationale.append("A later retention check was not demonstrated; the current state is reopened as FRAGILE.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    if transfer.negative > 0 and transfer.positive == 0:
        rationale.append("Independent performance did not transfer to unseen material; current state remains FRAGILE.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    if independence.negative > 0 and independence.positive == 0:
        rationale.append("The learner did not yet demonstrate the skill independently during verification.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    # Advancement requires staged evidence, never a single leap to retention.
    if independence.positive > 0 and state in {
        LearnerSkillState.EMERGING,
        LearnerSkillState.ACQUIRED,
        LearnerSkillState.INDEPENDENT,
        LearnerSkillState.TRANSFERRED,
        LearnerSkillState.RETAINED,
    }:
        state = LearnerSkillState.INDEPENDENT
        rationale.append("Independent verification was demonstrated on usable evidence.")

    if transfer.positive > 0 and independence.positive > 0 and state in {
        LearnerSkillState.INDEPENDENT,
        LearnerSkillState.TRANSFERRED,
        LearnerSkillState.RETAINED,
    }:
        state = LearnerSkillState.TRANSFERRED
        rationale.append("The learner transferred the skill to unseen material after independent verification.")

    if retention.positive > 0 and transfer.positive > 0 and independence.positive > 0 and state in {
        LearnerSkillState.TRANSFERRED,
        LearnerSkillState.RETAINED,
    }:
        state = LearnerSkillState.RETAINED
        rationale.append("Later usable retention evidence confirmed maintenance after transfer.")

    return base.model_copy(update={"state": state, "rationale": rationale})


def derive_longitudinal_state(events: list[LearnerEventRecord], language: str) -> dict[str, SkillStateRecord]:
    evidence = assessment_evidence_from_events(events)
    base = derive_learner_state(evidence)
    verification = _verification_by_skill(events)

    all_skill_ids = sorted(set(base) | set(verification))
    result: dict[str, SkillStateRecord] = {}
    for skill_id in all_skill_ids:
        base_record = base.get(skill_id)
        if base_record is None:
            base_record = SkillStateRecord(
                skill_id=skill_id,
                state=LearnerSkillState.UNKNOWN,
                evidence_support="NONE",
                rationale=["No assessment evidence is available for this skill yet."],
            )
        result[skill_id] = _apply_longitudinal_verification(base_record, verification.get(skill_id, []))
    return result


def replay_longitudinal(events: list[LearnerEventRecord], language: str) -> dict:
    evidence = assessment_evidence_from_events(events)
    learner_state = derive_longitudinal_state(events, language)
    hypotheses = evaluate_english_hypotheses(evidence) if language == "en" else []
    bottleneck = decide_bottleneck(evidence, language)

    verification_summary: dict[str, dict] = {}
    for skill_id, skill_events in _verification_by_skill(events).items():
        verification_summary[skill_id] = {
            stage: _stage_summary(skill_events, stage).__dict__
            for stage in ["ACQUISITION", "INDEPENDENCE", "TRANSFER", "RETENTION"]
        }

    return {
        "learner_state": {skill_id: record.model_dump(mode="json") for skill_id, record in learner_state.items()},
        "hypotheses": [record.model_dump(mode="json") for record in hypotheses],
        "bottleneck": bottleneck.model_dump(mode="json"),
        "verification": verification_summary,
        "engine_version": LONGITUDINAL_ENGINE_VERSION,
        "scientific_status": "UNVALIDATED_PILOT",
    }
