from __future__ import annotations

from dataclasses import dataclass

from readright.intelligence.bottleneck import decide_bottleneck_from_hypotheses
from readright.intelligence.hypotheses import evaluate_english_hypotheses
from readright.intelligence.learner_state import derive_learner_state
from readright.intelligence.models import HypothesisRecord, HypothesisStatus, LearnerSkillState, SkillStateRecord
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
    latest_correct: bool | None
    conflicting: bool


def _verification_by_skill(events: list[LearnerEventRecord]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for event in verification_events_from_events(events):
        if not event.skill_id:
            continue
        payload = dict(event.payload)
        payload["_sequence_no"] = event.sequence_no
        grouped.setdefault(event.skill_id, []).append(payload)
    for values in grouped.values():
        values.sort(key=lambda item: item.get("_sequence_no", 0))
    return grouped


def _stage_summary(events: list[dict], stage: str) -> VerificationStageSummary:
    stage_events = [
        e for e in events
        if e.get("stage") == stage and e.get("quality") in USABLE_VERIFICATION_QUALITIES
    ]
    positives = [e for e in stage_events if e.get("correct") is True and e.get("independent", True)]
    negatives = [e for e in stage_events if e.get("correct") is False]
    latest = stage_events[-1] if stage_events else None
    latest_correct = latest.get("correct") if latest else None
    return VerificationStageSummary(
        stage=stage,
        usable=len(stage_events),
        positive=len(positives),
        negative=len(negatives),
        latest_correct=latest_correct,
        conflicting=bool(positives and negatives and len(stage_events) >= 2 and stage_events[-1].get("_sequence_no") == stage_events[-2].get("_sequence_no")),
    )


def _apply_longitudinal_verification(base: SkillStateRecord, verification_events: list[dict]) -> SkillStateRecord:
    if not verification_events:
        return base

    acquisition = _stage_summary(verification_events, "ACQUISITION")
    independence = _stage_summary(verification_events, "INDEPENDENCE")
    transfer = _stage_summary(verification_events, "TRANSFER")
    retention = _stage_summary(verification_events, "RETENTION")

    rationale = list(base.rationale)
    state = base.state

    # Current state follows the latest usable evidence at each verification level.
    # Older outcomes remain visible in the timeline and stage counts.
    if retention.latest_correct is False:
        rationale.append("The latest retention check was not demonstrated; the current state is reopened as FRAGILE.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    if transfer.latest_correct is False:
        rationale.append("The latest transfer check was not demonstrated on unseen material; current state is FRAGILE.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    if independence.latest_correct is False:
        rationale.append("The latest independence check was not demonstrated without support.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    if acquisition.latest_correct is False:
        rationale.append("The latest acquisition check was not demonstrated after instruction.")
        return base.model_copy(update={"state": LearnerSkillState.FRAGILE, "rationale": rationale})

    if acquisition.latest_correct is True and state in {
        LearnerSkillState.UNKNOWN,
        LearnerSkillState.NOT_DEMONSTRATED,
        LearnerSkillState.FRAGILE,
        LearnerSkillState.EMERGING,
        LearnerSkillState.ACQUIRED,
    }:
        state = LearnerSkillState.ACQUIRED
        rationale.append("Usable acquisition evidence shows the skill after instruction; independence is not yet assumed.")

    if independence.latest_correct is True and state in {
        LearnerSkillState.EMERGING,
        LearnerSkillState.ACQUIRED,
        LearnerSkillState.INDEPENDENT,
        LearnerSkillState.TRANSFERRED,
        LearnerSkillState.RETAINED,
    }:
        state = LearnerSkillState.INDEPENDENT
        rationale.append("Independent verification was demonstrated on usable evidence.")

    if transfer.latest_correct is True and independence.latest_correct is True and state in {
        LearnerSkillState.INDEPENDENT,
        LearnerSkillState.TRANSFERRED,
        LearnerSkillState.RETAINED,
    }:
        state = LearnerSkillState.TRANSFERRED
        rationale.append("The learner transferred the skill to unseen material after independent verification.")

    if retention.latest_correct is True and transfer.latest_correct is True and independence.latest_correct is True and state in {
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


def _apply_revision(record: HypothesisRecord, revision: str) -> HypothesisRecord:
    support = list(record.supporting_evidence)
    contradiction = list(record.contradicting_evidence)

    if revision == "STRENGTHEN" and record.status != HypothesisStatus.CONTRADICTED:
        support.append("A high-fidelity intervention produced the predicted verification response.")
        return record.model_copy(update={"status": HypothesisStatus.SUPPORTED, "supporting_evidence": support})

    if revision == "WEAKEN" and record.status != HypothesisStatus.CONTRADICTED:
        contradiction.append("A sufficiently faithful intervention did not produce the predicted acquisition/independence response.")
        return record.model_copy(update={"status": HypothesisStatus.WEAK, "contradicting_evidence": contradiction})

    if revision == "REOPEN_ALTERNATIVES" and record.status != HypothesisStatus.CONTRADICTED:
        contradiction.append("The taught response did not generalize, so competing explanations must be reconsidered.")
        return record.model_copy(update={"status": HypothesisStatus.POSSIBLE, "contradicting_evidence": contradiction})

    return record


def replay_hypotheses(events: list[LearnerEventRecord], language: str) -> list[HypothesisRecord]:
    if language != "en":
        return []

    evidence = assessment_evidence_from_events(events)
    records = {record.hypothesis_id: record for record in evaluate_english_hypotheses(evidence)}

    for event in sorted(events, key=lambda item: item.sequence_no):
        if event.event_type != "HYPOTHESIS_REVISION" or not event.hypothesis_id:
            continue
        record = records.get(event.hypothesis_id)
        if record is None:
            continue
        revision = str(event.payload.get("revision", "NO_CHANGE"))
        records[event.hypothesis_id] = _apply_revision(record, revision)

    return list(records.values())


def replay_longitudinal(events: list[LearnerEventRecord], language: str) -> dict:
    learner_state = derive_longitudinal_state(events, language)
    hypotheses = replay_hypotheses(events, language)
    bottleneck = decide_bottleneck_from_hypotheses(hypotheses, language)

    verification_summary: dict[str, dict] = {}
    for skill_id, skill_events in _verification_by_skill(events).items():
        verification_summary[skill_id] = {
            stage: _stage_summary(skill_events, stage).__dict__
            for stage in ["ACQUISITION", "INDEPENDENCE", "TRANSFER", "RETENTION"]
        }

    revisions = [
        {
            "sequence_no": event.sequence_no,
            "hypothesis_id": event.hypothesis_id,
            "intervention_id": event.intervention_id,
            "revision": event.payload.get("revision"),
            "payload": event.payload,
        }
        for event in events
        if event.event_type == "HYPOTHESIS_REVISION"
    ]

    return {
        "learner_state": {skill_id: record.model_dump(mode="json") for skill_id, record in learner_state.items()},
        "hypotheses": [record.model_dump(mode="json") for record in hypotheses],
        "bottleneck": bottleneck.model_dump(mode="json"),
        "verification": verification_summary,
        "hypothesis_revisions": revisions,
        "event_count": len(events),
        "engine_version": LONGITUDINAL_ENGINE_VERSION,
        "scientific_status": "UNVALIDATED_PILOT",
    }
