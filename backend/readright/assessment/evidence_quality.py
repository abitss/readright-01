from __future__ import annotations

from enum import Enum

from readright.assessment.models import ResponseInput


class EvidenceQuality(str, Enum):
    high = "HIGH"
    moderate = "MODERATE"
    low = "LOW"
    unusable = "UNUSABLE"


UNUSABLE_FLAGS = {
    "LANGUAGE_MISMATCH",
    "TASK_INTERRUPTED",
    "CAPTURE_FAILED",
    "UNUSABLE_AUDIO",
}

MODERATE_FLAGS = {
    "LOW_AUDIO_QUALITY",
    "DISTRACTED",
    "ASR_LOW_CONFIDENCE",
    "AMBIGUOUS_RESPONSE",
}


def rate_evidence(response: ResponseInput) -> EvidenceQuality:
    flags = set(response.quality_flags)

    if flags & UNUSABLE_FLAGS:
        return EvidenceQuality.unusable

    if response.assistance == "model":
        return EvidenceQuality.low

    if response.assistance == "hint":
        return EvidenceQuality.low

    if response.assistance == "repeat" or flags & MODERATE_FLAGS:
        return EvidenceQuality.moderate

    if response.teacher_confirmed and response.assistance == "none":
        return EvidenceQuality.high

    return EvidenceQuality.moderate
