from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillNode:
    id: str
    language: str
    name: str
    domain: str
    prerequisites: tuple[str, ...] = ()


ENGLISH_SKILLS: dict[str, SkillNode] = {
    "EN-ORAL-COMP": SkillNode("EN-ORAL-COMP", "en", "Oral language comprehension", "oral_language"),
    "EN-PHON-AWARE": SkillNode("EN-PHON-AWARE", "en", "Phoneme awareness", "phonology"),
    "EN-PHON-BLEND-CVC": SkillNode(
        "EN-PHON-BLEND-CVC",
        "en",
        "CVC phoneme blending",
        "phonology",
        ("EN-PHON-AWARE",),
    ),
    "EN-PHON-SEG": SkillNode(
        "EN-PHON-SEG",
        "en",
        "Phoneme segmentation",
        "phonology",
        ("EN-PHON-AWARE",),
    ),
    "EN-LETTER-RECOG": SkillNode("EN-LETTER-RECOG", "en", "Letter recognition", "print_code"),
    "EN-GPC": SkillNode(
        "EN-GPC",
        "en",
        "Grapheme-phoneme mapping",
        "print_code",
        ("EN-LETTER-RECOG",),
    ),
    "EN-DECODE-CVC": SkillNode(
        "EN-DECODE-CVC",
        "en",
        "Simple word decoding",
        "decoding",
        ("EN-GPC", "EN-PHON-BLEND-CVC"),
    ),
    "EN-DECODE-NONWORD": SkillNode(
        "EN-DECODE-NONWORD",
        "en",
        "Unfamiliar/nonword decoding",
        "decoding",
        ("EN-GPC", "EN-PHON-BLEND-CVC"),
    ),
    "EN-WORD-AUTO": SkillNode(
        "EN-WORD-AUTO",
        "en",
        "Word recognition automaticity",
        "fluency",
        ("EN-DECODE-CVC",),
    ),
    "EN-ORF": SkillNode(
        "EN-ORF",
        "en",
        "Connected-text oral reading fluency",
        "fluency",
        ("EN-WORD-AUTO",),
    ),
    "EN-READ-COMP": SkillNode(
        "EN-READ-COMP",
        "en",
        "Reading comprehension",
        "comprehension",
        ("EN-ORAL-COMP", "EN-DECODE-CVC"),
    ),
    "EN-SPELL": SkillNode(
        "EN-SPELL",
        "en",
        "Spelling/encoding",
        "encoding",
        ("EN-PHON-SEG", "EN-GPC"),
    ),
    "EN-RAN": SkillNode("EN-RAN", "en", "Rapid automatized naming", "automaticity"),
    "EN-PHON-MEM": SkillNode("EN-PHON-MEM", "en", "Phonological memory", "memory"),
}


HINDI_SKILLS: dict[str, SkillNode] = {
    "HI-ORAL-COMP": SkillNode("HI-ORAL-COMP", "hi", "Oral language comprehension", "oral_language"),
    "HI-PHON-AWARE": SkillNode("HI-PHON-AWARE", "hi", "Phonological awareness", "phonology"),
    "HI-AKSHARA-RECOG": SkillNode("HI-AKSHARA-RECOG", "hi", "Akshara recognition", "print_code"),
    "HI-AKSHARA-SOUND-BASIC": SkillNode(
        "HI-AKSHARA-SOUND-BASIC",
        "hi",
        "Akshara-sound mapping",
        "print_code",
        ("HI-AKSHARA-RECOG",),
    ),
    "HI-MATRA-INTEGRATION": SkillNode(
        "HI-MATRA-INTEGRATION",
        "hi",
        "Matra integration",
        "print_code",
        ("HI-AKSHARA-SOUND-BASIC",),
    ),
    "HI-WORD-DECODE": SkillNode(
        "HI-WORD-DECODE",
        "hi",
        "Word decoding",
        "decoding",
        ("HI-AKSHARA-SOUND-BASIC", "HI-MATRA-INTEGRATION"),
    ),
    "HI-ORF": SkillNode(
        "HI-ORF",
        "hi",
        "Connected-text oral reading fluency",
        "fluency",
        ("HI-WORD-DECODE",),
    ),
    "HI-READ-COMP": SkillNode(
        "HI-READ-COMP",
        "hi",
        "Reading comprehension",
        "comprehension",
        ("HI-ORAL-COMP", "HI-WORD-DECODE"),
    ),
    "HI-SPELL": SkillNode(
        "HI-SPELL",
        "hi",
        "Spelling/encoding",
        "encoding",
        ("HI-AKSHARA-SOUND-BASIC",),
    ),
}


SKILLS = {**ENGLISH_SKILLS, **HINDI_SKILLS}


def get_skill(skill_id: str) -> SkillNode | None:
    return SKILLS.get(skill_id)


def prerequisites_for(skill_id: str) -> tuple[str, ...]:
    skill = get_skill(skill_id)
    return skill.prerequisites if skill else ()
