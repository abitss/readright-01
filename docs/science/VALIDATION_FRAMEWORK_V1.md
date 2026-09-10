# ReadRight Validation Framework v1

Status: research framework, not a validation claim.
Framework version: `validation-framework-v1-2026-09`

## Purpose

ReadRight must distinguish three things that are often wrongly collapsed:

1. a scientifically plausible construct,
2. a technically functioning assessment engine,
3. a validated measurement and decision system for a defined use and population.

ReadRight currently has (1) and an early pilot form of (2). This framework governs the work required before making (3).

## Governing principle

Validity is not a property of software in the abstract. Evidence must support the interpretation and use of results for a defined population, context, language, administration mode, and decision.

Therefore ReadRight will never use a single universal `validated=true` flag. Every validation conclusion must specify:

- instrument version,
- engine/policy version,
- intended use,
- target grade/language/context,
- sample,
- external criterion when relevant,
- metrics and confidence intervals,
- limitations,
- reviewer approval.

## Four evidence phases

### Phase 0: Expert and content review

Before child field data are used for psychometric claims:

- literacy experts review construct representation,
- language experts review wording and phonological/orthographic appropriateness,
- teachers review administration feasibility,
- bias/fairness review flags culturally or linguistically loaded material,
- administration and scoring instructions are frozen for the study version.

Output: revised pilot bank and documented change log. No validity claim.

### Phase 1: Pilot / feasibility

Primary purpose: find broken items, administration problems, missing data, ambiguity, and floor/ceiling behavior.

Report at minimum:

- recruitment and exclusions,
- exposure count per item,
- completion rate,
- unusable-evidence rate,
- proportion correct / response distribution,
- teacher scoring disagreement on double-scored responses,
- subgroup descriptive summaries,
- every item changed or removed after the pilot.

Pilot data are exploratory. They must not be described publicly as independent validation.

### Phase 2: Calibration

Use a prospectively specified multi-school sample to develop the retained instrument and decision policy.

Depending on the construct and item format, analyses may include:

- item difficulty,
- item discrimination,
- dimensionality checks,
- reliability appropriate to the intended interpretation,
- inter-rater reliability for teacher-scored responses,
- alternate-form / test-retest evidence where appropriate,
- item and decision behavior across prespecified subgroups,
- threshold/cut-rule development,
- bootstrap or resampling stability,
- missing-data and evidence-quality sensitivity analyses.

Cronbach alpha is not a universal ReadRight quality metric. It is only appropriate for item sets where its assumptions and intended interpretation make sense.

Calibration data may be used to change items, weights, thresholds, and policies. For exactly that reason, the same learners cannot then be called an independent validation sample.

### Phase 3: Independent holdout validation

Before the study begins:

- lock instrument version,
- lock engine/policy version,
- lock primary outcomes,
- define external criterion and adjudication procedure,
- define exclusions,
- define subgroup analyses,
- define missing-data handling,
- preregister where feasible.

No learner used to tune items or thresholds may be in this holdout set.

For any binary risk/decision classification, report the full confusion matrix and at least:

- sensitivity,
- specificity,
- PPV,
- NPV,
- confidence intervals,
- prevalence in the validation sample.

Where an underlying continuous score/risk statistic exists, also consider ROC/AUC and calibration analysis. Do not report AUC merely because it is fashionable if the system does not produce a defensible continuous decision variable.

### Phase 4: External replication

A stronger evidence tier uses schools, researchers, regions, or samples materially independent of the original development process.

This phase evaluates transportability and known limits. It is where claims can begin to expand beyond the narrow original study context if the evidence supports that expansion.

## Reliability plan

ReadRight will match reliability evidence to the type of output.

### Human-scored responses

Use double scoring on a prespecified subset. Report percent agreement plus an agreement coefficient appropriate to the scale, such as Cohen's kappa for nominal/binary scoring. Where ordinal or continuous ratings are introduced, use corresponding reliability statistics rather than forcing kappa.

### Parallel/equivalent forms

For repeated adaptive probes, evaluate comparability of forms and systematic differences in difficulty. A form cannot be called equivalent merely because developers intended it to be equivalent.

### Test-retest

Use only where the construct should reasonably remain stable over the retest interval and where learning/practice effects are controlled or interpreted.

### Internal consistency

Use only for coherent multi-item scales where internal consistency is a meaningful property. Do not apply alpha to heterogeneous adaptive task batteries and call the whole engine reliable.

## Validity evidence plan

ReadRight will accumulate multiple kinds of evidence rather than search for one magic coefficient.

### Content evidence

Experts judge whether tasks adequately represent the target reading construct and whether administration introduces construct-irrelevant difficulty.

### Relations to other variables

Compare ReadRight outputs with justified external measures/criteria. Expected convergent and discriminant patterns must be stated before analysis.

### Response-process evidence

Study whether children and teachers are actually performing the cognitive/administration process the task intends. Cognitive interviews and structured observation can expose items that appear statistically fine but are misunderstood.

### Internal structure

Where a latent score model is used, evaluate whether the structure of response data supports that model. Do not claim latent dimensions that have not been tested.

### Consequences and decision utility

Track false positives, false negatives, abstentions, teacher burden, unnecessary interventions, delayed support, and whether recommended actions improve subsequent evidence. High apparent accuracy is not sufficient if errors cause harmful or systematically unfair decisions.

## Fairness and subgroup analysis

Before analysis, define relevant subgroup variables that can affect interpretation, for example:

- grade,
- school/context,
- home language,
- language of instruction,
- sex,
- geography where relevant and ethically collected.

For every subgroup analysis:

- report subgroup n,
- report uncertainty/confidence intervals,
- do not interpret unstable tiny cells as real differences,
- investigate material item or decision differences,
- distinguish measurement bias from true construct distribution differences.

Where sample size and model assumptions permit, use DIF or an appropriate equivalent item-bias method. DIF findings trigger investigation; they are not automatically proof that an item is unfair.

ReadRight should not collect sensitive attributes merely because a statistical package can analyze them. Collection must have a defined fairness purpose, lawful/ethical basis, and data-minimization plan.

## Adaptive assessment validation

ReadRight is adaptive, therefore validation cannot stop at item-level statistics.

Evaluate the full policy:

- exposure rates,
- path distributions,
- average and tail session length,
- evidence-quality failure rates,
- stopping outcomes,
- abstention frequency,
- contradiction frequency,
- subgroup differences in selected paths,
- whether different valid paths lead to stable instructional conclusions,
- robustness to a small number of item scoring errors.

The adaptive selector must be versioned. Any substantive selector change creates a new engine/policy version requiring renewed evidence.

## Intervention and verification validation

Assessment validity does not automatically validate ReadRight interventions.

Separately evaluate:

- intervention fidelity,
- immediate acquisition response,
- independence,
- transfer to untrained material,
- retention over time,
- nonresponse and alternative hypotheses.

A successful intervention response can support an instructional hypothesis, but it must not be converted into a clinical diagnosis.

## Claim gate

Software cannot automatically promote ReadRight to `VALIDATED`.

The product may display `SUPPORTED_FOR_DEFINED_USE` only when all of the following are documented:

1. evidence comes from a locked independent holdout or external validation study,
2. the report conclusion itself is `SUPPORTED_FOR_DEFINED_USE`,
3. limitations are explicit,
4. scientific review/approval is documented,
5. the public claim exactly matches the population, language, context, instrument version, engine version, and use studied.

Pilot status remains `UNVALIDATED_PILOT` regardless of impressive-looking metrics.

## Data split rule

At minimum maintain logical separation between:

- `DEVELOPMENT/PILOT`,
- `CALIBRATION`,
- `HOLDOUT_VALIDATION`,
- `EXTERNAL_VALIDATION`.

A learner/study record cannot silently migrate from calibration into holdout because this would leak development information into validation.

## Versioning rule

Freeze and record:

- task bank version,
- task content hash/revision,
- scoring rules,
- evidence-quality policy,
- adaptive selector version,
- learner-state version,
- bottleneck/hypothesis version,
- intervention policy version,
- verification policy version.

If a materially relevant component changes, previous validation evidence may no longer transfer completely. The change must be classified and the required revalidation level documented.

## Initial ReadRight study sequence

1. Expert/linguistic review of English Task Bank v1.
2. Small feasibility/cognitive pilot.
3. Item revision and freeze of English pilot v2.
4. Multi-school calibration study.
5. Lock decision rules.
6. Independent holdout study with an appropriate external criterion.
7. Fairness/subgroup review.
8. External replication.
9. Only then consider a narrowly worded validated-use claim.

Hindi follows its own language-specific sequence and cannot inherit English validation.

## Current product claim

Current ReadRight status remains:

`SCIENTIFICALLY DESIGNED / UNVALIDATED PILOT`

That is not a weakness. It is the scientifically correct state until evidence justifies a stronger claim.
