from collections import Counter

from readright.assessment.task_bank import META, STIMULI, TASKS, bank_summary, tasks_for_skill


def test_english_bank_contains_134_original_pilot_items():
    english = [task for task in TASKS.values() if task.language == "en"]
    assert len(english) == 134


def test_every_english_item_is_explicitly_unvalidated():
    english = [task for task in TASKS.values() if task.language == "en"]
    assert english
    for task in english:
        assert META[task.id].pilot_only is True
        assert META[task.id].calibration_status == "UNVALIDATED_PILOT"
        assert STIMULI[task.id]["validation_status"] == "UNVALIDATED_PILOT"
        assert STIMULI[task.id]["difficulty_is_estimate"] is True


def test_bank_has_broad_construct_coverage():
    counts = Counter(task.skill_id for task in TASKS.values() if task.language == "en")
    required = {
        "EN-ORAL-COMP",
        "EN-PHON-ISOLATE",
        "EN-PHON-BLEND-CVC",
        "EN-PHON-SEG",
        "EN-PHON-MANIP",
        "EN-LETTER-RECOG",
        "EN-GPC",
        "EN-PHON-MEM",
        "EN-RAN",
        "EN-DECODE-CVC",
        "EN-DECODE-NONWORD",
        "EN-WORD-AUTO",
        "EN-ORF",
        "EN-READ-COMP",
        "EN-SPELL",
    }
    assert required.issubset(counts)


def test_equivalent_forms_exist_for_core_error_sensitive_skills():
    for skill in ["EN-GPC", "EN-PHON-BLEND-CVC", "EN-PHON-SEG", "EN-DECODE-CVC", "EN-DECODE-NONWORD"]:
        assert len(tasks_for_skill(skill, "en")) >= 6


def test_ran_forms_warn_that_item_knowledge_must_be_established():
    for task in tasks_for_skill("EN-RAN", "en"):
        assert "Confirm" in (task.prompt.teacher_text or "")
        assert "known" in (task.prompt.teacher_text or "")


def test_summary_exposes_validation_state():
    summary = bank_summary()
    assert summary["english_items"] == 134
    assert summary["english_status"] == "UNVALIDATED_PILOT"
