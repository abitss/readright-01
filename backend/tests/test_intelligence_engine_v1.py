from readright.intelligence.bottleneck import decide_bottleneck
from readright.intelligence.hypotheses import evaluate_english_hypotheses
from readright.intelligence.learner_state import derive_skill_state
from readright.intelligence.models import HypothesisStatus, LearnerSkillState


def ev(task_id, skill_id, correct, quality="HIGH", assistance="none"):
    return {
        "task_id": task_id,
        "skill_id": skill_id,
        "correct": correct,
        "quality": quality,
        "assistance": assistance,
    }


def test_two_independent_positives_do_not_claim_retention():
    evidence = [ev("a", "EN-GPC", True), ev("b", "EN-GPC", True)]
    state = derive_skill_state("EN-GPC", evidence)
    assert state.state == LearnerSkillState.INDEPENDENT
    assert state.state not in {LearnerSkillState.TRANSFERRED, LearnerSkillState.RETAINED}


def test_one_negative_is_fragile_not_confirmed_barrier():
    state = derive_skill_state("EN-PHON-BLEND-CVC", [ev("a", "EN-PHON-BLEND-CVC", False)])
    assert state.state == LearnerSkillState.FRAGILE


def test_mixed_independent_evidence_becomes_conflicting():
    state = derive_skill_state("EN-GPC", [ev("a", "EN-GPC", True), ev("b", "EN-GPC", False)])
    assert state.state == LearnerSkillState.CONFLICTING


def test_blending_hypothesis_requires_context_before_supported():
    evidence = [
        ev("b1", "EN-PHON-BLEND-CVC", False),
        ev("b2", "EN-PHON-BLEND-CVC", False),
    ]
    hypotheses = {h.hypothesis_id: h for h in evaluate_english_hypotheses(evidence)}
    assert hypotheses["H-BLEND"].status == HypothesisStatus.POSSIBLE
    assert hypotheses["H-BLEND"].missing_evidence


def test_blending_can_be_supported_when_gpc_is_independent():
    evidence = [
        ev("g1", "EN-GPC", True), ev("g2", "EN-GPC", True),
        ev("b1", "EN-PHON-BLEND-CVC", False), ev("b2", "EN-PHON-BLEND-CVC", False),
    ]
    hypotheses = {h.hypothesis_id: h for h in evaluate_english_hypotheses(evidence)}
    assert hypotheses["H-BLEND"].status == HypothesisStatus.SUPPORTED


def test_bottleneck_engine_abstains_when_multiple_hypotheses_possible():
    evidence = [
        ev("b1", "EN-PHON-BLEND-CVC", False), ev("b2", "EN-PHON-BLEND-CVC", False),
        ev("d1", "EN-DECODE-NONWORD", False), ev("d2", "EN-DECODE-NONWORD", False),
    ]
    decision = decide_bottleneck(evidence, "en")
    assert decision.outcome in {"MORE_EVIDENCE_REQUIRED", "MULTIPLE_PLAUSIBLE_BARRIERS"}


def test_hindi_does_not_reuse_english_bottleneck_rules():
    decision = decide_bottleneck([], "hi")
    assert decision.outcome == "MORE_EVIDENCE_REQUIRED"
