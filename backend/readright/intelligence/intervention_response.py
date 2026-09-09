from __future__ import annotations

from readright.intelligence.intervention_models import (
    HypothesisRevisionDirection,
    InterventionFidelity,
    InterventionResponseDecision,
    VerificationEvidence,
    VerificationOutcome,
)
from readright.intelligence.verification import evaluate_verification


def interpret_intervention_response(
    *,
    hypothesis_id: str,
    fidelity: InterventionFidelity,
    verification_events: list[VerificationEvidence],
) -> InterventionResponseDecision:
    verification = evaluate_verification(verification_events)
    by_stage = {item.stage.value: item for item in verification}

    if fidelity in {InterventionFidelity.UNKNOWN, InterventionFidelity.LOW}:
        return InterventionResponseDecision(
            hypothesis_id=hypothesis_id,
            revision=HypothesisRevisionDirection.CANNOT_INTERPRET,
            verification=verification,
            next_action="Improve intervention fidelity and repeat verification before revising the hypothesis.",
            rationale=["Low or unknown delivery fidelity makes non-response scientifically uninterpretable."],
        )

    acquisition = by_stage["ACQUISITION"].outcome
    independence = by_stage["INDEPENDENCE"].outcome
    transfer = by_stage["TRANSFER"].outcome
    retention = by_stage["RETENTION"].outcome

    if acquisition == VerificationOutcome.PASS and independence == VerificationOutcome.PASS:
        if transfer == VerificationOutcome.PASS:
            return InterventionResponseDecision(
                hypothesis_id=hypothesis_id,
                revision=HypothesisRevisionDirection.STRENGTHEN,
                verification=verification,
                next_action="Continue to retention verification in a later session; reduce support gradually.",
                rationale=["Improvement under acceptable fidelity transferred to unseen evidence, which is consistent with the targeted hypothesis."],
            )
        if transfer == VerificationOutcome.FAIL:
            return InterventionResponseDecision(
                hypothesis_id=hypothesis_id,
                revision=HypothesisRevisionDirection.REOPEN_ALTERNATIVES,
                verification=verification,
                next_action="Reopen competing explanations and examine why taught performance did not transfer.",
                rationale=["Acquisition occurred but transfer failed, so the current hypothesis may be incomplete."],
            )

    if acquisition == VerificationOutcome.FAIL and independence == VerificationOutcome.FAIL:
        return InterventionResponseDecision(
            hypothesis_id=hypothesis_id,
            revision=HypothesisRevisionDirection.WEAKEN,
            verification=verification,
            next_action="Weaken the current hypothesis and collect discriminating evidence for alternative explanations.",
            rationale=["The predicted response did not occur despite acceptable-fidelity targeted intervention."],
        )

    if any(item.outcome in {VerificationOutcome.CONFLICTING, VerificationOutcome.UNUSABLE} for item in verification):
        return InterventionResponseDecision(
            hypothesis_id=hypothesis_id,
            revision=HypothesisRevisionDirection.CANNOT_INTERPRET,
            verification=verification,
            next_action="Resolve conflicting or unusable verification evidence before changing the hypothesis.",
            rationale=["Verification quality is not sufficient for hypothesis revision."],
        )

    return InterventionResponseDecision(
        hypothesis_id=hypothesis_id,
        revision=HypothesisRevisionDirection.NO_CHANGE,
        verification=verification,
        next_action="Collect the minimum additional verification evidence needed to resolve the intervention response.",
        rationale=["Current verification evidence is not yet sufficient to strengthen or weaken the hypothesis."],
    )
