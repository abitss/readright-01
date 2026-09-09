# ReadRight Assessment Engine v1

Status: **scientific development specification**

ReadRight v1 is an evidence-collection and decision-support engine for foundational reading. It is **not** a clinical diagnostic instrument and must not claim that a learner has dyslexia or another disorder.

## Evidence base used for the v1 architecture

The architecture is grounded in established reading-assessment constructs rather than a single proprietary test:

- International Dyslexia Association: oral language, phonological awareness/processing, memory, rapid naming, word recognition, decoding with unfamiliar/nonwords, fluency, comprehension and spelling.
- What Works Clearinghouse foundational-reading guidance: oral/academic language, awareness of speech sounds and their link to print, decoding/word analysis, connected-text accuracy/fluency/comprehension.
- DIBELS 8: repeated curriculum-based measures including phonemic segmentation, nonsense-word decoding, word-reading fluency and oral-reading fluency; its technical documentation also stresses reliability, validity and the danger of relying on a single measure for high-stakes decisions.
- NCII screening standards: classification accuracy, reliability, validity, statistical bias and sample representativeness are separate requirements.
- NIPUN Bharat Foundational Learning Study: oral-language comprehension, phonological awareness, decoding, reading comprehension and oral-reading fluency with comprehension across Indian languages.
- DALI-DAB: Indian bilingual/biliterate assessment work using literacy tests and mediator skills in English, Hindi and Marathi, standardized on 1,013 children.

## Critical rule

**Research-backed constructs do not automatically make ReadRight's own tasks validated.**

Every ReadRight item, score interpretation, adaptive rule and stopping rule remains pilot/developmental until it is calibrated and validated on an appropriate learner sample.

## Engine pipeline

```
Skill Graph
    ↓
Task Bank
    ↓
Evidence Event
    ↓
Evidence Quality Gate
    ↓
Adaptive Task Selector
    ↓
Contradiction Check
    ↓
Stopping Rule
```

The output of this layer is structured evidence and uncertainty. Barrier inference and intervention selection happen downstream.

## 1. Skill Graph

The graph defines what each task is intended to inform and which prerequisite skills may need probing when performance breaks.

The first English graph contains the following broad nodes:

- oral language comprehension
- phoneme awareness
- phoneme blending
- phoneme segmentation
- letter recognition
- grapheme-phoneme mapping
- decoding
- unfamiliar/nonword decoding
- word recognition/automaticity
- connected-text fluency
- reading comprehension
- spelling/encoding
- rapid naming
- phonological memory

Hindi uses a separate language graph rather than a translated English graph. Initial nodes include oral language, phonological awareness, akshara knowledge, akshara-sound mapping, matra integration, word decoding, connected-text reading, comprehension and spelling/encoding.

## 2. Task Bank

Each task must contain:

- stable task ID
- language
- target skill(s)
- task family
- evidence tier
- difficulty metadata
- prerequisite skills
- equivalent-form group
- administration instructions
- expected response type
- capture mode
- estimated burden/time
- review status
- calibration status

Development items must be marked `pilot_only=true` until psychometric calibration.

Do not copy copyrighted standardized test items into ReadRight.

## 3. Evidence Event

Raw observation and inference remain separate.

The event stores what happened:

- task presented
- raw response
- scorer/teacher judgment
- latency
- prompt/assistance level
- self-correction
- capture method
- quality flags
- teacher confirmation
- timestamp

It does **not** store a diagnosis or a permanent learner label.

## 4. Evidence Quality

Quality is categorical in v1 to avoid fake precision.

Possible bands:

- `HIGH`
- `MODERATE`
- `LOW`
- `UNUSABLE`

Examples:

- language mismatch, capture failure or interrupted task -> unusable
- full model or strong hint -> low evidence for independent mastery
- repeated prompt or uncertain audio -> moderate
- independent, clear and teacher-confirmed response -> high

These are operational evidence-usability rules, not normative cut scores.

## 5. Adaptive Selector

V1 does not use a black-box model.

Selection is transparent and deterministic:

1. start from an age/grade/language-appropriate anchor
2. collect more than one independent observation before treating a target as sufficiently sampled
3. if evidence conflicts, request an equivalent-form probe
4. if a higher-level task fails, consider prerequisite probes
5. avoid repeating an identical item
6. prefer tasks that reduce current uncertainty with the least burden
7. stop rather than fabricate a conclusion when the bank cannot resolve uncertainty

Information-gain or IRT-based selection can replace parts of this after calibration data exist.

## 6. Contradiction Testing

Contradiction is a first-class output, not an error.

Examples:

- independent correct and independent incorrect responses across equivalent tasks
- strong real-word reading but repeated unfamiliar/nonword failure
- strong oral blending but poor printed decoding

When conflict exists, the engine should schedule a disambiguating task or return `CONFLICTING_EVIDENCE`.

## 7. Stopping Rules

A session may stop because:

- intended evidence targets have been sufficiently sampled under the current pilot policy
- evidence remains conflicting after available disambiguation tasks
- language/context makes evidence invalid
- learner fatigue or distress is reported
- task bank is exhausted
- pilot time/task safety cap is reached

A safety cap is not a mastery cutoff.

Possible outcomes:

- `EVIDENCE_COLLECTED`
- `MORE_EVIDENCE_REQUIRED`
- `CONFLICTING_EVIDENCE`
- `UNUSABLE_CONTEXT`
- `SESSION_LIMIT_REACHED`

## 8. Validation roadmap

### Stage A: expert content review

Literacy specialists, teachers and language experts review construct alignment, wording, cultural/linguistic appropriateness and scoring rules.

### Stage B: cognitive pilot

Observe how children interpret tasks. Remove ambiguous or instruction-heavy items.

### Stage C: item calibration

Estimate item difficulty, discrimination, inter-rater agreement, test-retest/alternate-form behavior and differential item functioning where appropriate.

### Stage D: external validity

Compare ReadRight evidence/state estimates against qualified human assessment and validated/standardized measures where licensing permits.

### Stage E: classification and fairness

Only if ReadRight is later used for screening/risk classification, evaluate sensitivity, specificity, PPV, NPV, calibration, subgroup performance, statistical bias and representative samples.

### Stage F: independent holdout validation

Use new schools/children not involved in rule creation or calibration.

## Non-negotiables

1. One failed task never equals a learner label.
2. ASR never outranks a clear teacher-confirmed observation in v1.
3. Experimental gaze/acoustic signals cannot independently alter core learner state.
4. The engine may say `MORE_EVIDENCE_REQUIRED`.
5. Every task-selection and stopping decision must be auditable.
6. Every engine decision records a policy/version identifier.
