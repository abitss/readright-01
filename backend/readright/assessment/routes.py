from fastapi import APIRouter, HTTPException

from readright.assessment.adaptive_policy import POLICY_VERSION, select_next_adaptive_task
from readright.assessment.evidence_quality import rate_evidence
from readright.assessment.frontier import frontier_snapshot
from readright.assessment.models import AssessmentSession, ResponseInput, StartAssessmentRequest
from readright.assessment.planner import planner_reason, select_first_task
from readright.assessment.stopping import evaluate_stop
from readright.assessment.task_bank import META, bank_summary, get_task_stimulus

router = APIRouter()
_sessions: dict[str, AssessmentSession] = {}
_evidence: dict[str, list[dict]] = {}
_selection_log: dict[str, list[dict]] = {}


@router.get("/bank/summary")
def get_bank_summary() -> dict:
    return {**bank_summary(), "policy_version": POLICY_VERSION}


@router.post("/start")
def start_assessment(request: StartAssessmentRequest) -> dict:
    try:
        task = select_first_task(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    session = AssessmentSession(
        learner_id=request.learner_id,
        language=request.language,
        mode=request.mode,
        teacher_concern=request.teacher_concern,
        target_skill_id=request.target_skill_id,
        current_task=task,
    )
    _sessions[session.id] = session
    _evidence[session.id] = []
    reason = planner_reason(request.mode, request.target_skill_id)
    _selection_log[session.id] = [
        {
            "task_id": task.id,
            "skill_id": task.skill_id,
            "reason": reason,
            "decision_kind": "INITIAL_ANCHOR",
            "policy_version": POLICY_VERSION,
        }
    ]
    return {
        "session": session,
        "task_stimulus": get_task_stimulus(task.id),
        "selection_reason": reason,
        "policy_version": POLICY_VERSION,
        "scientific_status": "UNVALIDATED_PILOT",
    }


@router.post("/{session_id}/respond")
def record_response(session_id: str, response: ResponseInput) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found")
    if session.status != "active":
        raise HTTPException(status_code=409, detail="Assessment session is not active")
    if not session.current_task or response.task_id != session.current_task.id:
        raise HTTPException(status_code=409, detail="Response does not match the current assessment task")

    completed_task = session.current_task
    quality = rate_evidence(response)
    task_meta = META.get(completed_task.id)

    event = {
        "task_id": response.task_id,
        "skill_id": completed_task.skill_id,
        "task_family": task_meta.family if task_meta else None,
        "response_raw": response.response_raw,
        "correct": response.correct,
        "latency_ms": response.latency_ms,
        "assistance": response.assistance,
        "self_corrected": response.self_corrected,
        "teacher_confirmed": response.teacher_confirmed,
        "quality_flags": response.quality_flags,
        "quality": quality.value,
        "estimated_seconds": completed_task.estimated_seconds,
        "policy_version": POLICY_VERSION,
        "bank_validation_status": task_meta.calibration_status if task_meta else "UNVALIDATED_PILOT",
    }
    _evidence[session_id].append(event)

    decision = select_next_adaptive_task(
        mode=session.mode,
        language=session.language,
        current_skill_id=completed_task.skill_id,
        evidence=_evidence[session_id],
        teacher_concern_skill_id=session.target_skill_id,
    )

    stop_outcome = evaluate_stop(
        mode=session.mode,
        evidence=_evidence[session_id],
        has_next_task=decision.task is not None,
    )

    snapshot = frontier_snapshot(_evidence[session_id], language=session.language)

    if stop_outcome is not None:
        session.current_task = None
        session.status = "complete"
        return {
            "assessment_complete": True,
            "outcome": stop_outcome.value,
            "evidence_count": len(_evidence[session_id]),
            "frontier": snapshot,
            "policy_version": POLICY_VERSION,
            "scientific_status": "UNVALIDATED_PILOT",
            "message": "Assessment stopped under an auditable pilot rule. Sampling states are not diagnoses or mastery claims.",
        }

    next_task = decision.task
    session.current_task = next_task
    _selection_log[session_id].append(
        {
            "task_id": next_task.id,
            "skill_id": next_task.skill_id,
            "reason": decision.reason,
            "decision_kind": decision.kind.value,
            "utility": decision.utility,
            "policy_version": decision.policy_version,
        }
    )
    return {
        "assessment_complete": False,
        "next_task": next_task,
        "task_stimulus": get_task_stimulus(next_task.id),
        "selection_reason": decision.reason,
        "decision_kind": decision.kind.value,
        "utility": decision.utility,
        "evidence_count": len(_evidence[session_id]),
        "frontier": snapshot,
        "policy_version": POLICY_VERSION,
        "scientific_status": "UNVALIDATED_PILOT",
    }


@router.get("/{session_id}")
def get_session(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found")
    evidence = _evidence.get(session_id, [])
    return {
        "session": session,
        "evidence": evidence,
        "frontier": frontier_snapshot(evidence, language=session.language),
        "selection_log": _selection_log.get(session_id, []),
        "policy_version": POLICY_VERSION,
        "scientific_status": "UNVALIDATED_PILOT",
    }
