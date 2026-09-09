from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable

from readright.assessment.skill_graph import SKILLS, prerequisites_for

USABLE_QUALITIES = {"HIGH", "MODERATE"}


class SamplingState(str, Enum):
    """Assessment sampling state, deliberately NOT a mastery state."""

    unseen = "UNSEEN"
    unusable_only = "UNUSABLE_ONLY"
    assisted_only = "ASSISTED_ONLY"
    positive_sample = "POSITIVE_SAMPLE"
    negative_sample = "NEGATIVE_SAMPLE"
    replicated_positive = "REPLICATED_POSITIVE"
    replicated_negative = "REPLICATED_NEGATIVE"
    conflicting = "CONFLICTING"


@dataclass(frozen=True)
class SkillEvidenceSummary:
    skill_id: str
    state: SamplingState
    observed: int
    usable: int
    independent_usable: int
    independent_correct: int
    independent_incorrect: int
    task_ids: tuple[str, ...]

    @property
    def sampled_for_baseline(self) -> bool:
        return self.state in {
            SamplingState.positive_sample,
            SamplingState.replicated_positive,
            SamplingState.replicated_negative,
        }

    @property
    def requires_more_evidence(self) -> bool:
        return self.state in {
            SamplingState.unseen,
            SamplingState.unusable_only,
            SamplingState.assisted_only,
            SamplingState.negative_sample,
            SamplingState.conflicting,
        }


def _skill_events(evidence: Iterable[dict], skill_id: str) -> list[dict]:
    return [event for event in evidence if event.get("skill_id") == skill_id]


def summarize_skill(evidence: list[dict], skill_id: str) -> SkillEvidenceSummary:
    events = _skill_events(evidence, skill_id)
    if not events:
        return SkillEvidenceSummary(skill_id, SamplingState.unseen, 0, 0, 0, 0, 0, ())

    usable = [event for event in events if event.get("quality") in USABLE_QUALITIES]
    independent = [event for event in usable if event.get("assistance") == "none"]
    correct = [event for event in independent if event.get("correct") is True]
    incorrect = [event for event in independent if event.get("correct") is False]

    if not usable:
        state = SamplingState.unusable_only
    elif not independent:
        state = SamplingState.assisted_only
    elif correct and incorrect:
        state = SamplingState.conflicting
    elif len(correct) >= 2:
        state = SamplingState.replicated_positive
    elif len(incorrect) >= 2:
        state = SamplingState.replicated_negative
    elif len(correct) == 1:
        state = SamplingState.positive_sample
    elif len(incorrect) == 1:
        state = SamplingState.negative_sample
    else:
        state = SamplingState.assisted_only

    return SkillEvidenceSummary(
        skill_id=skill_id,
        state=state,
        observed=len(events),
        usable=len(usable),
        independent_usable=len(independent),
        independent_correct=len(correct),
        independent_incorrect=len(incorrect),
        task_ids=tuple(event.get("task_id", "") for event in events),
    )


def unresolved_prerequisites(skill_id: str, evidence: list[dict]) -> list[str]:
    unresolved: list[str] = []
    for prerequisite in prerequisites_for(skill_id):
        state = summarize_skill(evidence, prerequisite).state
        if state not in {SamplingState.positive_sample, SamplingState.replicated_positive}:
            unresolved.append(prerequisite)
    return unresolved


def blocked_by_negative_prerequisite(skill_id: str, evidence: list[dict]) -> list[str]:
    blocked: list[str] = []
    for prerequisite in prerequisites_for(skill_id):
        state = summarize_skill(evidence, prerequisite).state
        if state in {SamplingState.replicated_negative, SamplingState.conflicting}:
            blocked.append(prerequisite)
    return blocked


def frontier_snapshot(evidence: list[dict], language: str | None = None) -> dict[str, dict]:
    snapshot: dict[str, dict] = {}
    for skill_id, skill in SKILLS.items():
        if language and skill.language != language:
            continue
        summary = summarize_skill(evidence, skill_id)
        payload = asdict(summary)
        payload["state"] = summary.state.value
        payload["prerequisites"] = list(skill.prerequisites)
        payload["unresolved_prerequisites"] = unresolved_prerequisites(skill_id, evidence)
        snapshot[skill_id] = payload
    return snapshot


def replicated_negative_skills(evidence: list[dict], language: str | None = None) -> list[str]:
    results: list[str] = []
    for skill_id, skill in SKILLS.items():
        if language and skill.language != language:
            continue
        if summarize_skill(evidence, skill_id).state == SamplingState.replicated_negative:
            results.append(skill_id)
    return results
