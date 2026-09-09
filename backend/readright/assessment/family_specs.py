from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskFamilySpec:
    id: str
    construct: str
    intended_evidence: tuple[str, ...]
    interpretation_limits: tuple[str, ...]
    required_context: tuple[str, ...] = ()


FAMILY_SPECS: dict[str, TaskFamilySpec] = {
    "oral_comprehension": TaskFamilySpec(
        "oral_comprehension",
        "Spoken-language comprehension",
        ("understanding spoken vocabulary/syntax", "literal/inferential oral comprehension"),
        ("Does not establish reading ability by itself.", "Poor performance may reflect language exposure or task misunderstanding."),
        ("language of instruction/exposure confirmed",),
    ),
    "phoneme_isolation": TaskFamilySpec(
        "phoneme_isolation",
        "Awareness of individual speech sounds",
        ("access to initial/final phonemes",),
        ("Does not diagnose dyslexia.", "Do not interpret without usable hearing/language context."),
    ),
    "phoneme_blending": TaskFamilySpec(
        "phoneme_blending",
        "Ability to combine orally presented phonemes",
        ("oral phoneme blending",),
        ("A single failure is insufficient.", "Failure does not prove a reading disorder."),
    ),
    "phoneme_segmentation": TaskFamilySpec(
        "phoneme_segmentation",
        "Ability to segment a spoken word into phonemes",
        ("phoneme segmentation",),
        ("A single failure is insufficient.", "Do not infer print-code weakness from this oral task alone."),
    ),
    "phoneme_manipulation": TaskFamilySpec(
        "phoneme_manipulation",
        "Higher-load phonemic manipulation",
        ("deletion/substitution of phonemes",),
        ("Conditional probe only.", "Working-memory demands can contribute to failure."),
        ("basic phoneme isolation/segmentation sampled first",),
    ),
    "letter_recognition": TaskFamilySpec(
        "letter_recognition",
        "Letter-name knowledge",
        ("recognition of printed letter forms",),
        ("Letter naming is not the same as grapheme-phoneme mapping.",),
    ),
    "grapheme_phoneme_mapping": TaskFamilySpec(
        "grapheme_phoneme_mapping",
        "Knowledge of common letter-sound correspondences",
        ("print-to-sound mapping",),
        ("Exact mappings are language/orthography dependent.", "One symbol error does not establish a barrier."),
        ("letter recognition sampled",),
    ),
    "phonological_memory": TaskFamilySpec(
        "phonological_memory",
        "Temporary retention/reproduction of unfamiliar phonological sequences",
        ("nonword repetition accuracy", "sequence retention"),
        ("Speech production, hearing, accent, and unfamiliarity can influence performance.", "Not a standalone diagnostic marker."),
    ),
    "rapid_naming": TaskFamilySpec(
        "rapid_naming",
        "Speed and accuracy of retrieving well-known verbal labels",
        ("rapid naming rate", "rapid naming errors/hesitations"),
        ("Invalid if the learner does not know the items untimed.", "Not a standalone diagnostic marker."),
        ("untimed item knowledge established",),
    ),
    "real_word_decoding": TaskFamilySpec(
        "real_word_decoding",
        "Reading printed real words",
        ("word-reading accuracy", "latency", "self-correction"),
        ("Real words may be recognized from memory, so this cannot isolate productive decoding alone.",),
    ),
    "nonword_decoding": TaskFamilySpec(
        "nonword_decoding",
        "Productive decoding of unfamiliar, pronounceable letter strings",
        ("application of print-sound knowledge to unfamiliar forms",),
        ("Nonword performance does not diagnose dyslexia.", "Items require linguistic review for phonotactic appropriateness."),
        ("grapheme-phoneme mapping and oral blending considered",),
    ),
    "word_automaticity": TaskFamilySpec(
        "word_automaticity",
        "Accuracy and rate for familiar printed words",
        ("word-reading rate", "word-reading accuracy"),
        ("Rate must not be interpreted without accuracy.", "Timed performance can be affected by unfamiliarity or test context."),
    ),
    "oral_reading_fluency": TaskFamilySpec(
        "oral_reading_fluency",
        "Connected-text oral reading accuracy and rate",
        ("words read", "errors", "self-corrections", "rate"),
        ("Fluency is not synonymous with comprehension.", "Passage difficulty must be calibrated before normative interpretation."),
        ("word-level reading sampled",),
    ),
    "reading_comprehension_literal": TaskFamilySpec(
        "reading_comprehension_literal",
        "Understanding explicitly stated information in text",
        ("literal reading comprehension",),
        ("Poor performance may reflect decoding or oral-language limitations.",),
        ("oral language and decoding evidence available",),
    ),
    "reading_comprehension_inferential": TaskFamilySpec(
        "reading_comprehension_inferential",
        "Integrating text information to make a simple inference",
        ("inferential reading comprehension",),
        ("Poor performance may reflect vocabulary/oral-language limits as well as reading processes.",),
        ("oral language and decoding evidence available",),
    ),
    "spelling_word": TaskFamilySpec(
        "spelling_word",
        "Encoding spoken real words into print",
        ("phoneme segmentation", "sound-symbol encoding", "orthographic knowledge"),
        ("Handwriting/motor output can contaminate written-response evidence.",),
    ),
    "spelling_nonword": TaskFamilySpec(
        "spelling_nonword",
        "Productive encoding of unfamiliar spoken forms",
        ("phoneme-to-grapheme encoding without memorized word spelling",),
        ("Nonword spelling is not a standalone diagnostic marker.", "Speech perception and phonotactic familiarity can affect responses."),
    ),
}


def get_family_spec(family_id: str) -> TaskFamilySpec | None:
    return FAMILY_SPECS.get(family_id)
