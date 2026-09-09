from __future__ import annotations

from readright.intelligence.hypotheses import evaluate_english_hypotheses
from readright.intelligence.models import BottleneckDecision, HypothesisRecord, HypothesisStatus


def decide_bottleneck_from_hypotheses(hypotheses: list[HypothesisRecord], language: str) -> BottleneckDecision:
    if language != "en":
        return BottleneckDecision(
            outcome="MORE_EVIDENCE_REQUIRED",
            next_evidence_needed=["Hindi bottleneck rules are not yet scientifically specified."],
            rationale=["The Hindi learner-state layer must be designed independently from English."],
        )

    supported = [h for h in hypotheses if h.status == HypothesisStatus.SUPPORTED]
    possible = [h for h in hypotheses if h.status == HypothesisStatus.POSSIBLE]

    if len(supported) == 1:
        return BottleneckDecision(
            outcome="ACTIONABLE_BARRIER_IDENTIFIED",
            primary_hypothesis=supported[0],
            alternatives=[h for h in possible if h.hypothesis_id != supported[0].hypothesis_id][:3],
            rationale=["One hypothesis is supported without unresolved contradictory context in the current pilot rules."],
        )

    if len(supported) > 1:
        return BottleneckDecision(
            outcome="MULTIPLE_PLAUSIBLE_BARRIERS",
            alternatives=supported + possible[:2],
            next_evidence_needed=sorted({m for h in supported for m in h.missing_evidence}),
            rationale=["More than one actionable explanation remains supported; ReadRight abstains from choosing a single cause."],
        )

    if possible:
        missing = sorted({m for h in possible for m in h.missing_evidence})
        return BottleneckDecision(
            outcome="MORE_EVIDENCE_REQUIRED",
            alternatives=possible[:4],
            next_evidence_needed=missing,
            rationale=["Evidence currently supports candidate explanations but does not justify a single high-confidence instructional barrier."],
        )

    conflicted = [h for h in hypotheses if h.status == HypothesisStatus.WEAK and h.missing_evidence]
    if conflicted:
        return BottleneckDecision(
            outcome="CONFLICTING_OR_INSUFFICIENT_EVIDENCE",
            alternatives=conflicted[:4],
            next_evidence_needed=sorted({m for h in conflicted for m in h.missing_evidence}),
            rationale=["Current evidence is insufficient or internally conflicting."],
        )

    return BottleneckDecision(
        outcome="NO_ACTIONABLE_BARRIER_IDENTIFIED",
        rationale=["Current assessment and intervention-response evidence does not support an actionable barrier under the pilot rules."],
    )


def decide_bottleneck(evidence: list[dict], language: str) -> BottleneckDecision:
    if language != "en":
        return decide_bottleneck_from_hypotheses([], language)
    return decide_bottleneck_from_hypotheses(evaluate_english_hypotheses(evidence), language)
