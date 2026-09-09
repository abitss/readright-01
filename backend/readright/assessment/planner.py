from readright.assessment.models import AssessmentMode, AssessmentTask, StartAssessmentRequest, TaskPrompt


ENGLISH_BASELINE_ANCHOR = AssessmentTask(
    id="en-phon-blend-cvc-001",
    language="en",
    skill_id="EN-PHON-BLEND-CVC",
    type="listen_and_respond",
    prompt=TaskPrompt(
        learner_text="What word do these sounds make?",
        spoken_prompt="/m/ /a/ /p/",
        teacher_text="Present the sounds with a neutral pace and no additional cue.",
    ),
    capture="voice",
    difficulty=0.30,
    estimated_seconds=20,
    evidence_targets=["phoneme_blending"],
)


HINDI_BASELINE_ANCHOR = AssessmentTask(
    id="hi-akshara-sound-001",
    language="hi",
    skill_id="HI-AKSHARA-SOUND-BASIC",
    type="letter_sound",
    prompt=TaskPrompt(
        learner_text="इस अक्षर की ध्वनि बताओ।",
        teacher_text="Record the learner response without coaching.",
    ),
    capture="voice",
    difficulty=0.20,
    estimated_seconds=15,
    evidence_targets=["akshara_sound_mapping"],
)


def select_first_task(request: StartAssessmentRequest) -> AssessmentTask:
    # V0 planner deliberately uses transparent anchor rules.
    # Adaptive selection will replace this with information-gain logic after calibration.
    if request.language == "hi":
        return HINDI_BASELINE_ANCHOR
    return ENGLISH_BASELINE_ANCHOR


def planner_reason(mode: AssessmentMode) -> str:
    return {
        AssessmentMode.baseline: "Establish an initial skill frontier with a high-value anchor task.",
        AssessmentMode.focused_probe: "Collect evidence around the teacher concern or current uncertainty.",
        AssessmentMode.progress_probe: "Collect a short, comparable progress signal.",
    }[mode]
