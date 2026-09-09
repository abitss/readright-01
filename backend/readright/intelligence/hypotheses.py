from __future__ import annotations

from dataclasses import dataclass

from readright.intelligence.learner_state import derive_skill_state
from readright.intelligence.models import HypothesisRecord, HypothesisStatus, LearnerSkillState


@dataclass(frozen=True)
class HypothesisSpec:
    id: str
    label: str
    target_skill: str
    supporting_states: tuple[LearnerSkillState, ...]
    contradicting_states: tuple[LearnerSkillState, ...]
    required_context_skills: tuple[str, ...] = ()


ENGLISH_HYPOTHESES: dict[str, HypothesisSpec] = {
    "H-GPC": HypothesisSpec(
        "H-GPC", "Print-to-sound mapping is the current actionable barrier", "EN-GPC",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-LETTER-RECOG",),
    ),
    "H-BLEND": HypothesisSpec(
        "H-BLEND", "Phoneme blending is the current actionable barrier", "EN-PHON-BLEND-CVC",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-GPC",),
    ),
    "H-SEG": HypothesisSpec(
        "H-SEG", "Phoneme segmentation is the current actionable barrier", "EN-PHON-SEG",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
    ),
    "H-PHON-MEM": HypothesisSpec(
        "H-PHON-MEM", "Phonological sequence retention may be contributing to difficulty", "EN-PHON-MEM",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
    ),
    "H-DECODE": HypothesisSpec(
        "H-DECODE", "Productive decoding is the current actionable barrier", "EN-DECODE-NONWORD",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-GPC", "EN-PHON-BLEND-CVC"),
    ),
    "H-AUTO": HypothesisSpec(
        "H-AUTO", "Word-reading automaticity is the current actionable barrier", "EN-WORD-AUTO",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-DECODE-CVC",),
    ),
    "H-ORF": HypothesisSpec(
        "H-ORF", "Connected-text fluency is the current actionable barrier", "EN-ORF",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-WORD-AUTO",),
    ),
    "H-ORAL-LANG": HypothesisSpec(
        "H-ORAL-LANG", "Oral-language comprehension may be limiting reading comprehension", "EN-ORAL-COMP",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
    ),
    "H-COMP": HypothesisSpec(
        "H-COMP", "Reading comprehension is the current actionable barrier", "EN-READ-COMP",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-ORAL-COMP", "EN-DECODE-CVC"),
    ),
    "H-SPELL": HypothesisSpec(
        "H-SPELL", "Spelling/encoding is the current actionable barrier", "EN-SPELL",
        (LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.FRAGILE),
        (LearnerSkillState.INDEPENDENT,),
        ("EN-PHON-SEG", "EN-GPC"),
    ),
}


def evaluate_hypothesis(spec: HypothesisSpec, evidence: list[dict]) -> HypothesisRecord:
    target = derive_skill_state(spec.target_skill, evidence)
    support: list[str] = []
    contradiction: list[str] = []
    missing: list[str] = []

    if target.state in spec.supporting_states:
        support.append(f"{spec.target_skill} is currently {target.state.value}.")
    elif target.state in spec.contradicting_states:
        contradiction.append(f"{spec.target_skill} is currently {target.state.value}.")
    elif target.state == LearnerSkillState.CONFLICTING:
        missing.append(f"Resolve conflicting evidence for {spec.target_skill}.")
    elif target.state == LearnerSkillState.UNKNOWN:
        missing.append(f"Collect evidence for {spec.target_skill}.")

    for skill_id in spec.required_context_skills:
        state = derive_skill_state(skill_id, evidence)
        if state.state == LearnerSkillState.UNKNOWN:
            missing.append(f"Collect prerequisite/context evidence for {skill_id}.")
        elif state.state in {LearnerSkillState.NOT_DEMONSTRATED, LearnerSkillState.CONFLICTING}:
            contradiction.append(f"{skill_id} is {state.state.value}, so it may better explain the observed difficulty.")
        elif state.state == LearnerSkillState.INDEPENDENT:
            support.append(f"{skill_id} is independently demonstrated, reducing one alternative explanation.")

    if contradiction and not support:
        status = HypothesisStatus.CONTRADICTED
    elif len(support) >= 2 and not contradiction and not missing:
        status = HypothesisStatus.SUPPORTED
    elif support and not contradiction:
        status = HypothesisStatus.POSSIBLE
    elif target.state == LearnerSkillState.UNKNOWN:
        status = HypothesisStatus.UNKNOWN
    else:
        status = HypothesisStatus.WEAK

    return HypothesisRecord(
        hypothesis_id=spec.id,
        label=spec.label,
        status=status,
        supporting_evidence=support,
        contradicting_evidence=contradiction,
        missing_evidence=missing,
        instruction_target=spec.target_skill,
    )


def evaluate_english_hypotheses(evidence: list[dict]) -> list[HypothesisRecord]:
    return [evaluate_hypothesis(spec, evidence) for spec in ENGLISH_HYPOTHESES.values()]
