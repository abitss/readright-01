from __future__ import annotations

from dataclasses import dataclass

from readright.assessment.models import AssessmentTask, TaskPrompt


@dataclass(frozen=True)
class TaskMeta:
    family: str
    equivalent_form_group: str
    prerequisites: tuple[str, ...]
    pilot_only: bool = True
    calibration_status: str = "UNVALIDATED_PILOT"


TASKS: dict[str, AssessmentTask] = {
    "en-gpc-m-001": AssessmentTask(
        id="en-gpc-m-001",
        language="en",
        skill_id="EN-GPC",
        type="letter_sound",
        prompt=TaskPrompt(
            learner_text="What sound does this letter make?",
            spoken_prompt=None,
            teacher_text="Show the learner the letter m without giving a sound cue.",
        ),
        capture="voice",
        difficulty=0.15,
        estimated_seconds=12,
        evidence_targets=["grapheme_phoneme_mapping"],
    ),
    "en-gpc-s-002": AssessmentTask(
        id="en-gpc-s-002",
        language="en",
        skill_id="EN-GPC",
        type="letter_sound",
        prompt=TaskPrompt(
            learner_text="What sound does this letter make?",
            spoken_prompt=None,
            teacher_text="Show the learner the letter s without giving a sound cue.",
        ),
        capture="voice",
        difficulty=0.15,
        estimated_seconds=12,
        evidence_targets=["grapheme_phoneme_mapping"],
    ),
    "en-blend-map-001": AssessmentTask(
        id="en-blend-map-001",
        language="en",
        skill_id="EN-PHON-BLEND-CVC",
        type="listen_and_respond",
        prompt=TaskPrompt(
            learner_text="What word do these sounds make?",
            spoken_prompt="/m/ /a/ /p/",
            teacher_text="Say each phoneme cleanly with a neutral pace and no extra cue.",
        ),
        capture="voice",
        difficulty=0.30,
        estimated_seconds=20,
        evidence_targets=["phoneme_blending"],
    ),
    "en-blend-sat-002": AssessmentTask(
        id="en-blend-sat-002",
        language="en",
        skill_id="EN-PHON-BLEND-CVC",
        type="listen_and_respond",
        prompt=TaskPrompt(
            learner_text="What word do these sounds make?",
            spoken_prompt="/s/ /a/ /t/",
            teacher_text="Say each phoneme cleanly with a neutral pace and no extra cue.",
        ),
        capture="voice",
        difficulty=0.30,
        estimated_seconds=20,
        evidence_targets=["phoneme_blending"],
    ),
    "en-seg-map-001": AssessmentTask(
        id="en-seg-map-001",
        language="en",
        skill_id="EN-PHON-SEG",
        type="listen_and_respond",
        prompt=TaskPrompt(
            learner_text="Tell me every sound you hear in the word.",
            spoken_prompt="map",
            teacher_text="Say the whole word once. Do not segment it for the learner.",
        ),
        capture="voice",
        difficulty=0.30,
        estimated_seconds=20,
        evidence_targets=["phoneme_segmentation"],
    ),
    "en-nonword-mip-001": AssessmentTask(
        id="en-nonword-mip-001",
        language="en",
        skill_id="EN-DECODE-NONWORD",
        type="word_decode",
        prompt=TaskPrompt(
            learner_text="Read this made-up word aloud.",
            spoken_prompt=None,
            teacher_text="Present the printed item mip. Do not pronounce it first.",
        ),
        capture="voice",
        difficulty=0.42,
        estimated_seconds=20,
        evidence_targets=["nonword_decoding"],
    ),
    "en-nonword-sop-002": AssessmentTask(
        id="en-nonword-sop-002",
        language="en",
        skill_id="EN-DECODE-NONWORD",
        type="word_decode",
        prompt=TaskPrompt(
            learner_text="Read this made-up word aloud.",
            spoken_prompt=None,
            teacher_text="Present the printed item sop. Do not pronounce it first.",
        ),
        capture="voice",
        difficulty=0.42,
        estimated_seconds=20,
        evidence_targets=["nonword_decoding"],
    ),
    "hi-akshara-k-001": AssessmentTask(
        id="hi-akshara-k-001",
        language="hi",
        skill_id="HI-AKSHARA-SOUND-BASIC",
        type="letter_sound",
        prompt=TaskPrompt(
            learner_text="इस अक्षर की ध्वनि बताओ।",
            spoken_prompt=None,
            teacher_text="Show क and record the response without coaching.",
        ),
        capture="voice",
        difficulty=0.20,
        estimated_seconds=15,
        evidence_targets=["akshara_sound_mapping"],
    ),
    "hi-akshara-m-002": AssessmentTask(
        id="hi-akshara-m-002",
        language="hi",
        skill_id="HI-AKSHARA-SOUND-BASIC",
        type="letter_sound",
        prompt=TaskPrompt(
            learner_text="इस अक्षर की ध्वनि बताओ।",
            spoken_prompt=None,
            teacher_text="Show म and record the response without coaching.",
        ),
        capture="voice",
        difficulty=0.20,
        estimated_seconds=15,
        evidence_targets=["akshara_sound_mapping"],
    ),
}


META: dict[str, TaskMeta] = {
    "en-gpc-m-001": TaskMeta("gpc_basic", "EN-GPC-EQ-A", ("EN-LETTER-RECOG",)),
    "en-gpc-s-002": TaskMeta("gpc_basic", "EN-GPC-EQ-A", ("EN-LETTER-RECOG",)),
    "en-blend-map-001": TaskMeta("blend_cvc", "EN-BLEND-EQ-A", ("EN-PHON-AWARE",)),
    "en-blend-sat-002": TaskMeta("blend_cvc", "EN-BLEND-EQ-A", ("EN-PHON-AWARE",)),
    "en-seg-map-001": TaskMeta("segment_cvc", "EN-SEG-EQ-A", ("EN-PHON-AWARE",)),
    "en-nonword-mip-001": TaskMeta("nonword_cvc", "EN-NONWORD-EQ-A", ("EN-GPC", "EN-PHON-BLEND-CVC")),
    "en-nonword-sop-002": TaskMeta("nonword_cvc", "EN-NONWORD-EQ-A", ("EN-GPC", "EN-PHON-BLEND-CVC")),
    "hi-akshara-k-001": TaskMeta("akshara_sound", "HI-AKSHARA-EQ-A", ("HI-AKSHARA-RECOG",)),
    "hi-akshara-m-002": TaskMeta("akshara_sound", "HI-AKSHARA-EQ-A", ("HI-AKSHARA-RECOG",)),
}


def tasks_for_skill(skill_id: str, language: str | None = None) -> list[AssessmentTask]:
    tasks = [task for task in TASKS.values() if task.skill_id == skill_id]
    if language:
        tasks = [task for task in tasks if task.language == language]
    return tasks


def get_task(task_id: str) -> AssessmentTask | None:
    return TASKS.get(task_id)
