from __future__ import annotations

from collections import defaultdict

from readright.intelligence.intervention_models import (
    VerificationDecision,
    VerificationEvidence,
    VerificationOutcome,
    VerificationStage,
)

USABLE_QUALITIES = {"HIGH", "MODERATE"}


def evaluate_verification_stage(stage: VerificationStage, events: list[VerificationEvidence]) -> VerificationDecision:
    stage_events = [event for event in events if event.stage == stage]
    usable = [event for event in stage_events if event.quality in USABLE_QUALITIES]
    independent = [event for event in usable if event.independent]
    positives = [event for event in independent if event.correct is True]
    negatives = [event for event in independent if event.correct is False]

    if stage == VerificationStage.RETENTION and not stage_events:
        return VerificationDecision(
            stage=stage,
            outcome=VerificationOutcome.NOT_DUE,
            rationale=["Retention requires a later-session observation; absence of later evidence is not failure."],
        )

    if not stage_events:
        return VerificationDecision(
            stage=stage,
            outcome=VerificationOutcome.MORE_EVIDENCE_REQUIRED,
            rationale=["No verification evidence has been collected for this stage."],
        )

    if not usable or not independent:
        return VerificationDecision(
            stage=stage,
            outcome=VerificationOutcome.UNUSABLE,
            usable_events=len(usable),
            independent_events=len(independent),
            rationale=["No independent usable verification evidence is available."],
        )

    if positives and negatives:
        outcome = VerificationOutcome.CONFLICTING
        rationale = ["Independent usable verification evidence contains both success and failure." ]
    elif len(positives) >= 2:
        outcome = VerificationOutcome.PASS
        rationale = ["At least two independent usable positive observations support this verification stage."]
    elif len(negatives) >= 2:
        outcome = VerificationOutcome.FAIL
        rationale = ["At least two independent usable negative observations indicate this verification stage was not demonstrated."]
    else:
        outcome = VerificationOutcome.MORE_EVIDENCE_REQUIRED
        rationale = ["One independent observation is not enough to resolve this verification stage."]

    return VerificationDecision(
        stage=stage,
        outcome=outcome,
        usable_events=len(usable),
        independent_events=len(independent),
        positive_events=len(positives),
        negative_events=len(negatives),
        rationale=rationale,
    )


def evaluate_verification(events: list[VerificationEvidence]) -> list[VerificationDecision]:
    return [
        evaluate_verification_stage(stage, events)
        for stage in (
            VerificationStage.ACQUISITION,
            VerificationStage.INDEPENDENCE,
            VerificationStage.TRANSFER,
            VerificationStage.RETENTION,
        )
    ]
