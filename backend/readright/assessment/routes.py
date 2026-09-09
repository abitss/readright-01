from fastapi import APIRouter, HTTPException

from readright.assessment.models import AssessmentSession, ResponseInput, StartAssessmentRequest
from readright.assessment.planner import planner_reason, select_first_task

router = APIRouter()
_sessions: dict[str, AssessmentSession] = {}
_evidence: dict[str, list[dict]] = {}


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
    return {
        "session": session,
        "selection_reason": planner_reason(request.mode),
    }


@router.post("/{session_id}/respond")
def record_response(session_id: str, response: ResponseInput) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found")
    if session.status != "active":
        raise HTTPException(status_code=409, detail="Assessment session is not active")

    event = {
        "task_id": response.task_id,
        "response_raw": response.response_raw,
        "correct": response.correct,
        "latency_ms": response.latency_ms,
        "assistance": response.assistance,
        "self_corrected": response.self_corrected,
        "teacher_confirmed": response.teacher_confirmed,
        "quality_flags": response.quality_flags,
    }
    _evidence[session_id].append(event)

    # The next-task algorithm is intentionally not faked yet.
    # Until the calibrated selector exists, the engine returns a safe abstention.
    session.current_task = None
    session.status = "complete"
    return {
        "assessment_complete": True,
        "outcome": "MORE_EVIDENCE_REQUIRED",
        "message": "Evidence was stored. Adaptive inference is not enabled in this foundation build.",
        "evidence_count": len(_evidence[session_id]),
    }


@router.get("/{session_id}")
def get_session(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Assessment session not found")
    return {"session": session, "evidence": _evidence.get(session_id, [])}
