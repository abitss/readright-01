from fastapi import APIRouter, HTTPException

from readright.assessment.evidence_quality import rate_evidence
from readright.assessment.models import AssessmentSession, ResponseInput, StartAssessmentRequest
from readright.assessment.planner import planner_reason, select_first_task
from readright.assessment.selector import select_next_task
from readright.assessment.stopping import evaluate_stop

router = APIRouter()
_sessions: dict[str, AssessmentSession] = {}
_evidence: dict[str, list[dict]] = {}
_selection_log: dict[str, list[dict]] = {}


@router.post("/start")
def start_assessment(request: StartAssessmentRequest) -> dict:
    task = select_first_task(request)
    session = AssessmentSession(
        learner_id=request.learner_id,
        language=request.language,
        mode=request.mode,
        teacher_concern=request.teacher_concern,
        current_task=task,
    )
    _sessions[session.id] = session
    _evidence[session.id] = []
    _selection_log[session.id] = [
        {
            "task_id": task.id,
            "reason": planner_reason(request.mode),
            "policy_version": "assessment-v1-pilot-2026-09",
        }
    ]
    return {
        "session": session,
        "selection_reason": planner_reason(request.mode),
        "policy_version": "assessment-v1-pilot-2026-09",
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

    quality = rate_evidence(response)
    event = {
        "task_id": response.task_id,
        "skill_id": session.current_task.skill_id,
        "response_raw": response.response_raw,
        "correct": response.correct,
        "latency_ms": response.latency_ms,
        "assistance": response.assistance,
        "self_corrected": response.self_corrected,
        "teacher_confirmed": response.teacher_confirmed,
        "quality_flags": response.quality_flags,
        "quality": quality.value,
        "policy_version": "assessment-v1-pilot-2026-09",
    }
    _evidence[session_id].append(event)

    next_task, reason = select_next_task(
        language=session.language,
        current_skill_id=session.current_task.skill_id,
        evidence=_evidence[session_id],
    )

    stop_outcome = evaluate_stop(evidence=_evidence[session_id], has_next_task=next_task is not None)

    if stop_outcome is not None:
        session.current_task = None
        session.status = "complete"
        return {
            "assessment_complete": True,
            "outcome": stop_outcome.value,
            "evidence_count": len(_evidence[session_id]),
            "policy_version": "assessment-v1-pilot-2026-09",
            "message": "Assessment stopped under an auditable pilot stopping rule. This is not a clinical diagnosis.",
        }

    session.current_task = next_task
    _selection_log[session_id].append(
        {
            "task_id": next_task.id,
            "reason": reason,
            "policy_version": "assessment-v1-pilot-2026-09",
        }
    )
    return {
        "assessment_complete": False,
        "next_task": next_task,
        "selection_reason": reason,
        "evidence_count": len(_evidence[session_id]),
        "policy_version": "assessment-v1-pilot-2026-09",
    }


@router.get("/{session_id}")
def get_session(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found")
    return {
        "session": session,
        "evidence": _evidence.get(session_id, []),
        "selection_log": _selection_log.get(session_id, []),
    }
