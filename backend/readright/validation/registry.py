from __future__ import annotations

from readright.validation.models import SampleDescription, StudyPhase, StudyProtocol


VALIDATION_FRAMEWORK_VERSION = "validation-framework-v1-2026-09"


PILOT_PROTOCOL = StudyProtocol(
    study_id="RR-EN-PILOT-001",
    title="ReadRight English Pilot: Feasibility, administration quality, and item functioning",
    phase=StudyPhase.PILOT,
    instrument_version="EN-TASKBANK-V1-PILOT-2026-09",
    engine_version="assessment-v1-adaptive-pilot-2026-09",
    intended_use="Teacher-assisted foundational reading assessment research for Grades 1-3; not diagnosis.",
    primary_questions=[
        "Can teachers administer the task families consistently?",
        "Which items show ceiling, floor, ambiguity, or scoring problems?",
        "Which task families show sufficient response variation for calibration?",
        "Where do administration or language-context failures occur?",
    ],
    sample=SampleDescription(
        n_total=0,
        grades=["1", "2", "3"],
        languages=["en"],
        schools=None,
        states_or_regions=[],
        sampling_method="To be preregistered before field recruitment",
        inclusion_criteria=["Enrolled in target grades", "Parent/guardian consent and school approval as required"],
        exclusion_criteria=[],
        subgroup_fields=["grade", "school", "home_language", "instruction_language", "sex"],
    ),
    planned_metrics=[
        "administration completion rate",
        "item difficulty / proportion correct",
        "missing and unusable evidence rates",
        "teacher scoring agreement on double-scored subset",
        "item response distributions",
    ],
    minimum_reporting=[
        "sample recruitment and exclusions",
        "item exposure counts",
        "missing/unusable data",
        "all item revisions/removals",
        "subgroup descriptive results",
        "limitations",
    ],
    notes=[
        "Pilot results are exploratory and cannot establish clinical or diagnostic validity.",
        "Do not optimize items on the same data later used as independent validation evidence.",
    ],
)


CALIBRATION_PROTOCOL = StudyProtocol(
    study_id="RR-EN-CAL-001",
    title="ReadRight English Calibration Study",
    phase=StudyPhase.CALIBRATION,
    instrument_version="TBD_LOCKED_INSTRUMENT_VERSION",
    engine_version="TBD_LOCKED_ENGINE_VERSION",
    intended_use="Calibrate item behavior and decision policies for the defined teacher-assisted use case.",
    primary_questions=[
        "How difficult and discriminating are retained items?",
        "How reliable are scores or states where reliability is a meaningful property?",
        "Do proposed decision rules generalize across grade and language-context subgroups?",
    ],
    sample=SampleDescription(
        n_total=0,
        grades=["1", "2", "3"],
        languages=["en"],
        schools=None,
        states_or_regions=[],
        sampling_method="Prospective multi-school calibration sample; exact sampling plan preregistered before analysis",
        subgroup_fields=["grade", "school", "home_language", "instruction_language", "sex"],
    ),
    preregistered=False,
    locked_before_analysis=False,
    planned_metrics=[
        "item difficulty",
        "item discrimination",
        "reliability appropriate to each construct",
        "inter-rater agreement for human-scored responses",
        "subgroup item functioning",
        "decision stability under resampling",
    ],
    minimum_reporting=["all prespecified analyses", "deviations from protocol", "confidence intervals", "limitations"],
)


HOLDOUT_PROTOCOL = StudyProtocol(
    study_id="RR-EN-HOLDOUT-001",
    title="ReadRight English Independent Holdout Validation",
    phase=StudyPhase.HOLDOUT_VALIDATION,
    instrument_version="TBD_LOCKED_INSTRUMENT_VERSION",
    engine_version="TBD_LOCKED_ENGINE_VERSION",
    intended_use="Evaluate locked ReadRight decisions on learners not used for item or threshold development.",
    primary_questions=[
        "Do locked measurement and decision rules reproduce outside the calibration data?",
        "What are classification performance and uncertainty against an appropriate external criterion?",
        "Are material performance gaps present across prespecified subgroups?",
    ],
    sample=SampleDescription(
        n_total=0,
        grades=["1", "2", "3"],
        languages=["en"],
        schools=None,
        states_or_regions=[],
        sampling_method="Independent holdout sample; no learner overlap with calibration",
        subgroup_fields=["grade", "school", "home_language", "instruction_language", "sex"],
    ),
    preregistered=False,
    locked_before_analysis=False,
    external_criterion="To be selected and justified before study lock",
    planned_metrics=[
        "sensitivity",
        "specificity",
        "positive predictive value",
        "negative predictive value",
        "AUC where a continuous decision score is defined",
        "calibration where probabilistic outputs are defined",
        "subgroup performance with confidence intervals",
    ],
    minimum_reporting=[
        "criterion definition",
        "blindness/independence procedures",
        "confusion matrix",
        "confidence intervals",
        "subgroup sample sizes",
        "all exclusions",
        "limitations",
    ],
)


PROTOCOLS = {p.study_id: p for p in (PILOT_PROTOCOL, CALIBRATION_PROTOCOL, HOLDOUT_PROTOCOL)}
