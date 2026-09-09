from __future__ import annotations

from collections import defaultdict

from readright.assessment.evidence_quality import EvidenceQuality
from readright.assessment.skill_graph import prerequisites_for
from readright.assessment.task_bank import TASKS, META, tasks_for_skill


MIN_USABLE_OBSERVATIONS = 2


def _usable(event: dict) -> bool:
    return event.get("quality") in {EvidenceQuality.high.value, EvidenceQuality.moderate.value}


def _independent(event: dict) -> bool:
    return event.get("assistance") == "none" and _usable(event)


def summarize_by_skill(evidence: list[dict]) -> dict[str, dict]:
    summary: dict[str, dict] = defaultdict(lambda: {
        "usable": 0,
        "independent": 0,
        "correct": 0,
        "incorrect": 0,
        "task_ids": set(),
    })

    for event in evidence:
        skill_id = event.get("skill_id")
        if not skill_id:
            continue
        bucket = summary[skill_id]
        bucket["task_ids"].add(event.get("task_id"))
        if _usable(event):
            bucket["usable"] += 1
            if _independent(event):
                bucket["independent"] += 1
            if event.get("correct") is True:
                bucket["correct"] += 1
            elif event.get("correct") is False:
                bucket["incorrect"] += 1

    return dict(summary)


def conflicting(summary: dict) -> bool:
    return summary.get("correct", 0) > 0 and summary.get("incorrect", 0) > 0


def next_equivalent_task(skill_id: str, used_task_ids: set[str], language: str):
    candidates = tasks_for_skill(skill_id, language)
    for task in candidates:
        if task.id not in used_task_ids:
            return task
    return None


def select_next_task(*, language: str, current_skill_id: str, evidence: list[dict]):
    summary = summarize_by_skill(evidence)
    current = summary.get(current_skill_id, {})
    used = {event.get("task_id") for event in evidence}

    # 1. First resolve conflicting evidence with an equivalent-form task.
    if conflicting(current):
        candidate = next_equivalent_task(current_skill_id, used, language)
        if candidate:
            return candidate, "Resolve conflicting evidence with an equivalent-form probe."

    # 2. Do not treat one observation as sufficient sampling.
    if current.get("usable", 0) < MIN_USABLE_OBSERVATIONS:
        candidate = next_equivalent_task(current_skill_id, used, language)
        if candidate:
            return candidate, "Collect a second usable observation before interpreting this target."

    # 3. Repeated failure on a higher-level skill should trigger prerequisite probing.
    if current.get("incorrect", 0) >= MIN_USABLE_OBSERVATIONS:
        for prerequisite in prerequisites_for(current_skill_id):
            prereq_summary = summary.get(prerequisite, {})
            if prereq_summary.get("usable", 0) < MIN_USABLE_OBSERVATIONS:
                candidate = next_equivalent_task(prerequisite, used, language)
                if candidate:
                    return candidate, f"Probe prerequisite {prerequisite} to localize the breakdown."

    # 4. If current target is sufficiently sampled and no safe branch exists, stop.
    return None, "No additional validated pilot branch is available for this uncertainty."
