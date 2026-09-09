from __future__ import annotations

from readright.assessment.models import AssessmentTask, TaskPrompt
from readright.assessment.task_bank import TaskMeta

VERSION = "EN-TASKBANK-V1-PILOT-2026-09"
STATUS = "UNVALIDATED_PILOT"


def _task(*, id: str, skill: str, type: str, learner: str, teacher: str,
          difficulty: float, targets: list[str], family: str, group: str,
          capture: str = "voice", display: str | None = None,
          spoken: str | None = None, expected: list[str] | None = None,
          prerequisites: tuple[str, ...] = (), seconds: int = 15):
    task = AssessmentTask(
        id=id,
        language="en",
        skill_id=skill,
        type=type,
        prompt=TaskPrompt(learner_text=learner, spoken_prompt=spoken, teacher_text=teacher),
        capture=capture,
        difficulty=difficulty,
        estimated_seconds=seconds,
        evidence_targets=targets,
    )
    meta = TaskMeta(family, group, prerequisites)
    return task, meta, display, expected or []


def build_english_v1():
    tasks: dict[str, AssessmentTask] = {}
    meta: dict[str, TaskMeta] = {}
    stimuli: dict[str, dict] = {}

    def add(result):
        task, task_meta, display, expected = result
        tasks[task.id] = task
        meta[task.id] = task_meta
        stimuli[task.id] = {
            "display": display,
            "expected": expected,
            "bank_version": VERSION,
            "validation_status": STATUS,
            "difficulty_is_estimate": True,
            "expert_review": "PENDING",
            "bias_review": "PENDING",
            "linguistic_review": "PENDING",
        }

    # Oral language comprehension: original ReadRight items.
    oral = [
        ("Riya put her red pencil inside the small box.", "Where did Riya put the pencil?", ["inside the small box", "in the small box", "the box"], .25),
        ("The dog slept under the table while the family ate dinner.", "Where was the dog?", ["under the table"], .25),
        ("Arun wore a raincoat because dark clouds filled the sky.", "Why did Arun wear a raincoat?", ["because it might rain", "because of the rain"], .35),
        ("Meena had two mangoes. She gave one mango to her brother.", "How many mangoes did Meena have left?", ["one", "1"], .35),
        ("Before Neel opened his book, he washed his hands and sat at the desk.", "What did Neel do just before he opened his book?", ["sat at the desk"], .45),
        ("The little plant bent toward the window where sunlight entered the room.", "Why might the plant bend toward the window?", ["to get sunlight", "for light"], .50),
        ("Sara packed a bottle, a cap, and a towel before leaving for the swimming pool.", "Where was Sara probably going?", ["the swimming pool", "the pool"], .45),
        ("Vikram finished his homework before he went outside to play cricket.", "What happened first?", ["he finished his homework", "homework"], .35),
    ]
    for i, (spoken, learner, expected, difficulty) in enumerate(oral, 1):
        add(_task(id=f"en-oral-comp-{i:03d}", skill="EN-ORAL-COMP", type="listen_and_respond",
                  learner=learner, teacher="Read the sentence exactly once at a natural pace. Repeat only when the protocol requests it.",
                  spoken=spoken, difficulty=difficulty, targets=["oral_language_comprehension"],
                  family="oral_comprehension", group=f"EN-ORAL-COMP-EQ-{1 if i <= 4 else 2}", expected=expected, seconds=25))

    # Phoneme isolation.
    isolation = [("map", "first", "/m/"), ("sun", "first", "/s/"), ("fish", "first", "/f/"), ("top", "first", "/t/"),
                 ("map", "last", "/p/"), ("sun", "last", "/n/"), ("leaf", "last", "/f/"), ("dog", "last", "/g/")]
    for i, (word, position, answer) in enumerate(isolation, 1):
        add(_task(id=f"en-phon-isolate-{i:03d}", skill="EN-PHON-ISOLATE", type="listen_and_respond",
                  learner=f"What is the {position} sound in the word?", teacher=f"Say '{word}' once. Do not stretch the target sound.",
                  spoken=word, difficulty=.25 if position == "first" else .35, targets=["phoneme_isolation"],
                  family="phoneme_isolation", group=f"EN-PHON-ISOLATE-{position.upper()}", expected=[answer],
                  prerequisites=("EN-PHON-AWARE",)))

    # Phoneme blending.
    blend = [
        ("map", "/m/ /a/ /p/", .25), ("sat", "/s/ /a/ /t/", .25), ("fish", "/f/ /i/ /sh/", .35),
        ("sun", "/s/ /u/ /n/", .25), ("log", "/l/ /o/ /g/", .30), ("red", "/r/ /e/ /d/", .30),
        ("ship", "/sh/ /i/ /p/", .35), ("chat", "/ch/ /a/ /t/", .35),
        ("stop", "/s/ /t/ /o/ /p/", .50), ("frog", "/f/ /r/ /o/ /g/", .50),
        ("milk", "/m/ /i/ /l/ /k/", .50), ("hand", "/h/ /a/ /n/ /d/", .50),
    ]
    for i, (answer, spoken, difficulty) in enumerate(blend, 1):
        add(_task(id=f"en-blend-{i:03d}", skill="EN-PHON-BLEND-CVC", type="listen_and_respond",
                  learner="What word do these sounds make?", teacher="Say each phoneme cleanly with equal brief pauses and no cue.",
                  spoken=spoken, difficulty=difficulty, targets=["phoneme_blending"], family="phoneme_blending",
                  group="EN-BLEND-CVC-EQ" if spoken.count("/") == 6 else "EN-BLEND-CLUSTER-EQ",
                  expected=[answer], prerequisites=("EN-PHON-AWARE",), seconds=18))

    # Phoneme segmentation.
    segmentation = [
        ("map", "/m/ /a/ /p/", .25), ("sun", "/s/ /u/ /n/", .25), ("red", "/r/ /e/ /d/", .30),
        ("fish", "/f/ /i/ /sh/", .35), ("ship", "/sh/ /i/ /p/", .35), ("chat", "/ch/ /a/ /t/", .35),
        ("stop", "/s/ /t/ /o/ /p/", .50), ("frog", "/f/ /r/ /o/ /g/", .50),
        ("milk", "/m/ /i/ /l/ /k/", .50), ("hand", "/h/ /a/ /n/ /d/", .50),
        ("nest", "/n/ /e/ /s/ /t/", .50), ("jump", "/j/ /u/ /m/ /p/", .50),
    ]
    for i, (word, expected, difficulty) in enumerate(segmentation, 1):
        add(_task(id=f"en-seg-{i:03d}", skill="EN-PHON-SEG", type="listen_and_respond",
                  learner="Tell me every sound you hear in the word.", teacher=f"Say '{word}' once as a whole word. Do not segment it.",
                  spoken=word, difficulty=difficulty, targets=["phoneme_segmentation"], family="phoneme_segmentation",
                  group="EN-SEG-CVC-EQ" if expected.count("/") == 6 else "EN-SEG-CLUSTER-EQ", expected=[expected],
                  prerequisites=("EN-PHON-AWARE",), seconds=18))

    # Higher-load phoneme manipulation, conditional only.
    manipulation = [
        ("Say smile without /s/.", "mile", .55), ("Say stop without /s/.", "top", .55),
        ("Say clap without /k/.", "lap", .60), ("Say train without /t/.", "rain", .60),
        ("Change the first sound in map from /m/ to /t/.", "tap", .60),
        ("Change the first sound in sun from /s/ to /r/.", "run", .60),
        ("Change the last sound in map from /p/ to /t/.", "mat", .65),
        ("Change the last sound in fish from /sh/ to /t/.", "fit", .70),
    ]
    for i, (learner, expected, difficulty) in enumerate(manipulation, 1):
        add(_task(id=f"en-phon-manip-{i:03d}", skill="EN-PHON-MANIP", type="listen_and_respond",
                  learner=learner, teacher="Conditional probe. Do not use before basic phoneme skills have been sampled.",
                  difficulty=difficulty, targets=["phoneme_manipulation"], family="phoneme_manipulation",
                  group="EN-PHON-MANIP-EQ", expected=[expected], prerequisites=("EN-PHON-ISOLATE", "EN-PHON-SEG"), seconds=20))

    # Letter recognition.
    for i, letter in enumerate(["m", "s", "t", "p", "a", "i"], 1):
        add(_task(id=f"en-letter-name-{i:03d}", skill="EN-LETTER-RECOG", type="letter_name",
                  learner="What is the name of this letter?", teacher="Show the lowercase letter alone. Do not name or sound it first.",
                  display=letter, difficulty=.15, targets=["letter_recognition"], family="letter_recognition",
                  group="EN-LETTER-NAME-EQ", expected=[letter], seconds=10))

    # Grapheme-phoneme mapping.
    mappings = [("m", "/m/"), ("s", "/s/"), ("t", "/t/"), ("p", "/p/"), ("n", "/n/"), ("f", "/f/"),
                ("l", "/l/"), ("r", "/r/"), ("d", "/d/"), ("g", "/g/"), ("h", "/h/"), ("b", "/b/"),
                ("a", "/a/"), ("i", "/i/"), ("o", "/o/"), ("u", "/u/")]
    for i, (letter, sound) in enumerate(mappings, 1):
        add(_task(id=f"en-gpc-{i:03d}", skill="EN-GPC", type="letter_sound",
                  learner="What sound does this letter usually make here?", teacher="Show the lowercase letter alone. Do not provide a sound cue.",
                  display=letter, difficulty=.15 if i <= 12 else .25, targets=["grapheme_phoneme_mapping"],
                  family="grapheme_phoneme_mapping", group="EN-GPC-CONS-EQ" if i <= 12 else "EN-GPC-VOWEL-EQ",
                  expected=[sound], prerequisites=("EN-LETTER-RECOG",), seconds=10))

    # Phonological memory through nonword repetition.
    nonword_memory = [("pem", .30), ("zup", .30), ("feg", .30), ("nob", .30),
                      ("mavik", .50), ("sopel", .50), ("dunam", .55), ("ralip", .55)]
    for i, (nonword, difficulty) in enumerate(nonword_memory, 1):
        add(_task(id=f"en-phon-mem-{i:03d}", skill="EN-PHON-MEM", type="nonword_repeat",
                  learner="Repeat exactly what I say.", teacher="Say the nonword once at a natural pace. Do not show print.",
                  spoken=nonword, difficulty=difficulty, targets=["phonological_memory", "sequence_retention"],
                  family="phonological_memory", group="EN-PHON-MEM-CVC-EQ" if i <= 4 else "EN-PHON-MEM-MULTI-EQ",
                  expected=[nonword], seconds=15))

    # Rapid automatized naming. These forms are invalid if symbol/object knowledge is not secure.
    ran_forms = [
        ("digits", ["2", "7", "4", "9", "3", "7", "2", "3", "9", "4", "4", "2", "9", "7", "3", "9", "3", "7", "4", "2"]),
        ("letters", ["m", "s", "t", "p", "n", "t", "m", "n", "s", "p", "p", "s", "n", "m", "t", "n", "t", "p", "s", "m"]),
        ("colors", ["red", "blue", "green", "black", "yellow", "green", "red", "yellow", "blue", "black", "black", "red", "blue", "green", "yellow", "yellow", "black", "green", "red", "blue"]),
        ("objects", ["cat", "sun", "fish", "book", "tree", "fish", "cat", "tree", "sun", "book", "book", "sun", "tree", "fish", "cat", "tree", "book", "cat", "sun", "fish"]),
    ]
    for i, (kind, grid) in enumerate(ran_forms, 1):
        add(_task(id=f"en-ran-{i:03d}", skill="EN-RAN", type="ran_grid",
                  learner="Name each item from left to right as quickly and accurately as you can.",
                  teacher="Confirm every item is known before timing. If not, mark this RAN form invalid.",
                  capture="timed_voice", display=" | ".join(grid), difficulty=.35 if i <= 2 else .40,
                  targets=["rapid_naming_speed", "rapid_naming_accuracy"], family="rapid_naming",
                  group=f"EN-RAN-{kind.upper()}-EQ", expected=grid, seconds=35))

    # Real-word decoding.
    real_words = [("map", .25), ("sun", .25), ("red", .25), ("fish", .35), ("ship", .35), ("chat", .35),
                  ("stop", .45), ("hand", .45), ("milk", .45), ("jump", .45), ("nest", .45), ("frog", .50)]
    for i, (word, difficulty) in enumerate(real_words, 1):
        add(_task(id=f"en-word-decode-{i:03d}", skill="EN-DECODE-CVC", type="word_decode",
                  learner="Read this word aloud.", teacher="Show only the printed word. Do not pronounce or define it.",
                  display=word, difficulty=difficulty, targets=["real_word_decoding"], family="real_word_decoding",
                  group="EN-WORD-CVC-EQ" if i <= 6 else "EN-WORD-CLUSTER-EQ", expected=[word],
                  prerequisites=("EN-GPC", "EN-PHON-BLEND-CVC"), seconds=12))

    # Nonword decoding.
    nonwords = [("pem", .30), ("zup", .30), ("feg", .30), ("vot", .30), ("saf", .30), ("jup", .30),
                ("plim", .50), ("steg", .50), ("frup", .50), ("dasp", .50), ("nelt", .50), ("grib", .55)]
    for i, (word, difficulty) in enumerate(nonwords, 1):
        add(_task(id=f"en-nonword-decode-{i:03d}", skill="EN-DECODE-NONWORD", type="word_decode",
                  learner="Read this made-up word aloud.", teacher="Tell the learner it is made up. Do not pronounce it first.",
                  display=word, difficulty=difficulty, targets=["nonword_decoding"], family="nonword_decoding",
                  group="EN-NONWORD-CVC-EQ" if i <= 6 else "EN-NONWORD-CLUSTER-EQ", expected=[word],
                  prerequisites=("EN-GPC", "EN-PHON-BLEND-CVC"), seconds=14))

    # Word-reading automaticity grids.
    word_grids = [
        ["the", "and", "you", "was", "is", "to", "in", "it", "the", "you", "and", "in", "was", "to", "is", "it", "you", "the", "to", "and"],
        ["come", "have", "said", "what", "one", "there", "some", "were", "have", "come", "one", "said", "there", "what", "were", "some"],
        ["cat", "sun", "map", "fish", "red", "ship", "map", "cat", "ship", "sun", "fish", "red", "cat", "map", "sun", "red", "ship", "fish"],
        ["stop", "hand", "milk", "jump", "nest", "frog", "jump", "milk", "stop", "frog", "hand", "nest", "milk", "jump", "frog", "stop", "nest", "hand"],
    ]
    for i, grid in enumerate(word_grids, 1):
        add(_task(id=f"en-word-auto-{i:03d}", skill="EN-WORD-AUTO", type="timed_word_grid",
                  learner="Read the words from left to right as quickly and accurately as you can.",
                  teacher="Start timing with the first word. Record errors and self-corrections.", capture="timed_voice",
                  display=" | ".join(grid), difficulty=.40 if i <= 2 else .50, targets=["word_reading_rate", "word_reading_accuracy"],
                  family="word_automaticity", group="EN-WORD-AUTO-HF-EQ" if i <= 2 else "EN-WORD-AUTO-DECODED-EQ",
                  expected=grid, prerequisites=("EN-DECODE-CVC",), seconds=45))

    # Original connected-text passages. These are pilot passages, not copied standardized passages.
    passages = [
        ("The Lost Cap", "Ravi put his blue cap on the bench before the game. When the game ended, the cap was gone. He looked under the bench and beside the tree. Then he saw a small dog carrying something blue. Ravi called softly, and the dog dropped the cap near his feet. Ravi laughed, picked it up, and thanked the dog's owner."),
        ("A Seed in the Cup", "Mina filled a paper cup with soil and pushed a bean seed into the middle. Each morning she added a little water and placed the cup near the window. For several days, nothing changed. On the fifth morning, a green shoot appeared. Mina measured it with a ruler and wrote the number in her notebook."),
        ("The Quiet Library", "Samir liked the school library because it was calm after lunch. One afternoon he found a book about birds that travel very long distances. He read about a tiny bird that crossed the sea each year. Samir copied the bird's name onto a card so he could search for more information at home."),
        ("The Broken Kite", "Anaya's kite rose high until a strong gust pulled the string against a rough branch. The string snapped, and the kite landed in a field. Anaya and her cousin walked carefully around the fence and found it near a bush. They tied a new string to the frame and tested the kite again in a safer open space."),
    ]
    for i, (title, passage) in enumerate(passages, 1):
        add(_task(id=f"en-orf-{i:03d}", skill="EN-ORF", type="passage_read_aloud",
                  learner="Read this passage aloud. Keep going until I ask you to stop.",
                  teacher="Use standardized timing. Record words read, errors, self-corrections, and elapsed time. Do not coach.",
                  capture="timed_voice", display=f"{title}\n\n{passage}", difficulty=.55 if i <= 2 else .60,
                  targets=["oral_reading_fluency", "connected_text_accuracy"], family="oral_reading_fluency",
                  group="EN-ORF-PASSAGE-EQ", prerequisites=("EN-WORD-AUTO",), seconds=90))

    comprehension = [
        (1, "What colour was Ravi's cap?", ["blue"], "literal", .35),
        (1, "Why did Ravi call softly to the dog?", ["to get the cap back", "so the dog would drop the cap"], "inferential", .50),
        (2, "Where did Mina place the cup?", ["near the window", "by the window"], "literal", .35),
        (2, "Why did Mina write a number in her notebook?", ["to record the plant's growth", "to record how tall the shoot was"], "inferential", .50),
        (3, "What kind of book did Samir find?", ["a book about birds", "birds"], "literal", .35),
        (3, "Why did Samir copy the bird's name onto a card?", ["to search for more information at home", "to look it up later"], "inferential", .50),
        (4, "Where did the kite land?", ["in a field", "the field"], "literal", .35),
        (4, "Why did they test the kite in a safer open space?", ["to avoid another accident", "because it was safer away from obstacles"], "inferential", .55),
    ]
    for i, (passage_no, learner, expected, kind, difficulty) in enumerate(comprehension, 1):
        add(_task(id=f"en-read-comp-{i:03d}", skill="EN-READ-COMP", type="passage_question",
                  learner=learner, teacher=f"Ask after en-orf-{passage_no:03d}. Do not reveal or reread the answer-bearing sentence.",
                  difficulty=difficulty, targets=[f"reading_comprehension_{kind}"], family=f"reading_comprehension_{kind}",
                  group=f"EN-COMP-{kind.upper()}-EQ", expected=expected, prerequisites=("EN-ORAL-COMP", "EN-DECODE-CVC"), seconds=20))

    # Spelling and productive encoding.
    spelling = [("map", .30), ("sun", .30), ("red", .30), ("fish", .40), ("ship", .40), ("stop", .50),
                ("hand", .50), ("milk", .50), ("jump", .50), ("nest", .50), ("pem", .45), ("zup", .45)]
    for i, (word, difficulty) in enumerate(spelling, 1):
        nonword = i > 10
        add(_task(id=f"en-spell-{i:03d}", skill="EN-SPELL", type="spelling_dictation",
                  learner="Write the word you hear.", teacher="Say the target once and repeat once if the protocol permits. Do not spell it.",
                  capture="written_response", spoken=word, difficulty=difficulty, targets=["spelling_encoding"],
                  family="spelling_nonword" if nonword else "spelling_word",
                  group="EN-SPELL-NONWORD-EQ" if nonword else ("EN-SPELL-CVC-EQ" if i <= 5 else "EN-SPELL-CLUSTER-EQ"),
                  expected=[word], prerequisites=("EN-PHON-SEG", "EN-GPC"), seconds=25))

    return tasks, meta, stimuli
