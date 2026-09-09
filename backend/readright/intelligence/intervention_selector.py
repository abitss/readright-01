from __future__ import annotations

from uuid import uuid4

from readright.assessment.task_bank import tasks_for_skill
from readright.intelligence.bottleneck import decide_bottleneck
from readright.intelligence.intervention_library import interventions_for_hypothesis
from readright.intelligence.intervention_models import InterventionPlan


def _reserve_verification_tasks(skill_id: str, language: str = "en") -> tuple[list[str], list[str], list[str]]:
    tasks = sorted(tasks_for_skill(skill_id, language), key=lambda task: (task.difficulty, task.id))
    ids = [task.id for task in tasks]
    if not ids:
        return [], [], []

    acquisition = ids[-2:] if len(ids) >= 2 else ids[:]
    remaining = [task_id for task_id in ids if task_id not in acquisition]
    transfer = remaining[-2:] if len(remaining) >= 2 else remaining[:]
    remaining = [task_id for task_id in remaining if task_id not in transfer]
    retention = remaining[-2:] if len(remaining) >= 2 else remaining[:]
    return acquisition, transfer, retention


def select_intervention_plan(evidence: list[dict], language: str) -> InterventionPlan | None:
    bottleneck = decide_bottleneck(evidence, language)
    if bottleneck.outcome != "ACTIONABLE_BARRIER_IDENTIFIED" or not bottleneck.primary_hypothesis:
        return None

    hypothesis = bottleneck.primary_hypothesis
    candidates = interventions_for_hypothesis(hypothesis.hypothesis_id)
    if not candidates:
        return None

    intervention = candidates[0]
    acquisition, transfer, retention = _reserve_verification_tasks(intervention.target_skill_id, language)

    return InterventionPlan(
        plan_id=str(uuid4()),
        intervention=intervention,
        hypothesis_id=hypothesis.hypothesis_id,
        rationale=[
            "Selected only because exactly one instructional hypothesis is currently supported under the pilot bottleneck rules.",
            *bottleneck.rationale,
        ],
        verification_skill_id=intervention.target_skill_id,
        acquisition_task_ids=acquisition,
        transfer_task_ids=transfer,
        retention_task_ids=retention,
    )
