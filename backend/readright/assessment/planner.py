from readright.assessment.models import AssessmentMode, AssessmentTask, StartAssessmentRequest
from readright.assessment.task_bank import get_task


FIRST_TASK_BY_LANGUAGE = {
    "en": "en-blend-map-001",
    "hi": "hi-akshara-k-001",
}


def select_first_task(request: StartAssessmentRequest) -> AssessmentTask:
    # V1 uses a transparent anchor policy. The anchor is deliberately simple
    # and every subsequent branch is auditable. Psychometric selection can
    # replace this after calibration data exist.
    task = get_task(FIRST_TASK_BY_LANGUAGE[request.language])
    if task is None:  # defensive; bank configuration error, not learner error
        raise RuntimeError("Configured assessment anchor is missing from the task bank")
    return task


def planner_reason(mode: AssessmentMode) -> str:
    return {
        AssessmentMode.baseline: "Establish an initial skill frontier with a transparent pilot anchor.",
        AssessmentMode.focused_probe: "Collect evidence around the current concern or uncertainty.",
        AssessmentMode.progress_probe: "Collect a short comparable progress signal without changing scientific thresholds.",
    }[mode]
