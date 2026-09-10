from readright.validation.claims import evaluate_validation_claim, public_claim_label
from readright.validation.models import ClaimStatus, StudyPhase, ValidationReport
from readright.validation.registry import CALIBRATION_PROTOCOL, HOLDOUT_PROTOCOL, PILOT_PROTOCOL
from readright.validation.statistics import (
    binary_classification_metrics,
    cohens_kappa,
    cronbach_alpha,
    item_difficulty,
    percent_agreement,
    wilson_interval,
)


def test_protocols_separate_development_from_independent_validation():
    assert PILOT_PROTOCOL.phase == StudyPhase.PILOT
    assert CALIBRATION_PROTOCOL.phase == StudyPhase.CALIBRATION
    assert HOLDOUT_PROTOCOL.phase == StudyPhase.HOLDOUT_VALIDATION
    assert HOLDOUT_PROTOCOL.external_criterion is not None


def test_classification_metrics_are_explicit():
    result = binary_classification_metrics(
        [True, True, False, False],
        [True, False, True, False],
    )
    assert result.tp == 1
    assert result.tn == 1
    assert result.fp == 1
    assert result.fn == 1
    assert result.sensitivity == 0.5
    assert result.specificity == 0.5


def test_inter_rater_metrics():
    a = [1, 1, 0, 0]
    b = [1, 0, 0, 0]
    assert percent_agreement(a, b) == 0.75
    assert cohens_kappa(a, b) is not None


def test_alpha_is_not_forced_when_data_are_invalid():
    assert cronbach_alpha([]) is None
    assert cronbach_alpha([[1]]) is None


def test_item_difficulty_and_interval():
    assert item_difficulty([1, 1, 0, 1]) == 0.75
    interval = wilson_interval(75, 100)
    assert interval is not None
    assert interval[0] < 0.75 < interval[1]


def test_pilot_can_never_publish_validated_claim():
    report = ValidationReport(
        study_id="pilot",
        instrument_version="v1",
        phase=StudyPhase.PILOT,
        claim_status=ClaimStatus.SUPPORTED_FOR_DEFINED_USE,
        metrics=[],
        limitations=["small pilot"],
        decision="exploratory",
        approved_by=["reviewer"],
    )
    gate = evaluate_validation_claim(report)
    assert gate.allowed is False
    assert public_claim_label(report) == "UNVALIDATED_PILOT"


def test_independent_validation_still_requires_review_and_limitations():
    report = ValidationReport(
        study_id="holdout",
        instrument_version="v2",
        phase=StudyPhase.HOLDOUT_VALIDATION,
        claim_status=ClaimStatus.SUPPORTED_FOR_DEFINED_USE,
        metrics=[],
        limitations=[],
        decision="supported",
        approved_by=[],
    )
    assert evaluate_validation_claim(report).allowed is False


def test_defined_use_claim_can_only_pass_after_independent_review():
    report = ValidationReport(
        study_id="holdout",
        instrument_version="v2",
        phase=StudyPhase.HOLDOUT_VALIDATION,
        claim_status=ClaimStatus.SUPPORTED_FOR_DEFINED_USE,
        metrics=[],
        limitations=["Applies only to the studied Grades 1-3 teacher-assisted context."],
        decision="supported for defined use",
        approved_by=["independent-scientific-review"],
    )
    assert evaluate_validation_claim(report).allowed is True
