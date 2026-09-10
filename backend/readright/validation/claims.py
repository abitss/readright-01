from __future__ import annotations

from dataclasses import dataclass

from readright.validation.models import ClaimStatus, StudyPhase, ValidationReport


@dataclass(frozen=True)
class ClaimGateResult:
    allowed: bool
    status: ClaimStatus
    reasons: tuple[str, ...]


def evaluate_validation_claim(report: ValidationReport) -> ClaimGateResult:
    """Prevent research outputs from being promoted into stronger claims by accident."""
    reasons: list[str] = []

    if report.phase in {StudyPhase.PILOT, StudyPhase.CALIBRATION}:
        reasons.append("Pilot/calibration data are development evidence, not independent validation.")

    if report.phase in {StudyPhase.HOLDOUT_VALIDATION, StudyPhase.EXTERNAL_VALIDATION} and not report.approved_by:
        reasons.append("Independent validation claims require documented scientific review/approval.")

    if report.claim_status != ClaimStatus.SUPPORTED_FOR_DEFINED_USE:
        reasons.append("Report does not conclude SUPPORTED_FOR_DEFINED_USE.")

    if not report.limitations:
        reasons.append("Validation claims require explicit limitations.")

    allowed = not reasons
    return ClaimGateResult(allowed=allowed, status=report.claim_status, reasons=tuple(reasons))


def public_claim_label(report: ValidationReport) -> str:
    gate = evaluate_validation_claim(report)
    if gate.allowed:
        return "SUPPORTED_FOR_DEFINED_USE"
    if report.phase == StudyPhase.PILOT:
        return "UNVALIDATED_PILOT"
    if report.phase == StudyPhase.CALIBRATION:
        return "CALIBRATION_IN_PROGRESS"
    return "VALIDATION_EVIDENCE_INSUFFICIENT"
