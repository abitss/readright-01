# ReadRight Adaptive Assessment Policy v1

Policy version: `assessment-v1-adaptive-pilot-2026-09`
Scientific status: `UNVALIDATED_PILOT`

## Purpose

Assessment Engine v1 is an adaptive evidence-collection system. It does not diagnose dyslexia, assign permanent learner labels, or establish mastery. Its job is to collect the minimum useful evidence required for the next responsible instructional inference.

## Core loop

`Anchor -> Observe -> Quality Gate -> Sampling State -> Resolve Contradiction -> Probe Prerequisite -> Advance Frontier -> Stop/Abstain`

## Sampling states

These states describe the quality and replication of evidence collected during an assessment. They are not learner-state or mastery labels.

- `UNSEEN`
- `UNUSABLE_ONLY`
- `ASSISTED_ONLY`
- `POSITIVE_SAMPLE`
- `NEGATIVE_SAMPLE`
- `REPLICATED_POSITIVE`
- `REPLICATED_NEGATIVE`
- `CONFLICTING`

A single correct item produces only `POSITIVE_SAMPLE`. A single incorrect item produces only `NEGATIVE_SAMPLE`.

## Baseline policy

English baseline broad sequence:

1. Oral language comprehension
2. Grapheme-phoneme mapping
3. Real-word decoding
4. Nonword decoding
5. Word automaticity
6. Oral reading fluency
7. Reading comprehension
8. Spelling/encoding

The sequence is a transparent pilot administration policy, not a normative developmental scale.

If a higher-level skill shows replicated negative evidence, the engine probes unresolved prerequisites before interpreting the higher-level failure. If a prerequisite is a latent construct without direct tasks, the policy uses an explicitly configured observable probe family. For example, unresolved English phoneme-awareness context may be explored using phoneme-isolation or segmentation tasks.

## Equivalent-form rule

A negative, assisted-only, or unusable observation does not immediately alter interpretation. The engine first requests another unused task from the same equivalent-form group where possible.

Mixed independent correct and incorrect evidence creates `CONFLICTING`, which triggers another equivalent-form probe before the engine moves on.

## Focused probe policy

Focused probes require an explicit `target_skill_id`. Free-text teacher concern is stored as context but is never converted into a scientific target by an LLM.

The engine may probe prerequisites of the target skill when they are unresolved.

## Progress probe policy

Progress probes stay narrow and use unused parallel/equivalent-form tasks. They do not broaden into diagnostic exploration.

## Task utility

V1 uses an interpretable heuristic that prioritizes unresolved evidence while penalizing burden and extreme estimated difficulty. This value is NOT psychometric information gain and MUST NOT be presented as a validated probability.

After sufficient calibration data exist, this layer may be replaced with validated item-information/expected-information-gain methods.

## Stopping rules

Pilot caps:

- Baseline: max 24 tasks or 12 estimated minutes
- Focused probe: max 10 tasks or 5 estimated minutes
- Progress probe: max 6 tasks or 3 estimated minutes

Other stop outcomes:

- `EVIDENCE_COLLECTED`
- `MORE_EVIDENCE_REQUIRED`
- `CONFLICTING_EVIDENCE`
- `UNUSABLE_CONTEXT`
- `SESSION_LIMIT_REACHED`

The engine is explicitly allowed to abstain.

## Auditability

Each selected task records:

- task ID
- skill ID
- decision kind
- human-readable reason
- pilot utility score, if used
- policy version

This makes every assessment branch replayable and reviewable.

## Validation boundary

The constructs are grounded in established foundational-literacy assessment practice, but ReadRight's exact items, sequence, difficulty estimates, equivalent-form assumptions, utility heuristic, replication rules, and stopping thresholds remain pilot hypotheses until expert review and empirical validation are completed.
