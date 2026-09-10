from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Iterable, Sequence


@dataclass(frozen=True)
class BinaryClassificationMetrics:
    sensitivity: float | None
    specificity: float | None
    ppv: float | None
    npv: float | None
    accuracy: float | None
    tp: int
    tn: int
    fp: int
    fn: int


def _safe_div(num: float, den: float) -> float | None:
    return num / den if den else None


def binary_classification_metrics(
    reference_positive: Sequence[bool], predicted_positive: Sequence[bool]
) -> BinaryClassificationMetrics:
    if len(reference_positive) != len(predicted_positive):
        raise ValueError("Reference and prediction lengths must match")
    if not reference_positive:
        raise ValueError("At least one paired observation is required")

    tp = tn = fp = fn = 0
    for ref, pred in zip(reference_positive, predicted_positive, strict=True):
        if ref and pred:
            tp += 1
        elif not ref and not pred:
            tn += 1
        elif not ref and pred:
            fp += 1
        else:
            fn += 1

    total = tp + tn + fp + fn
    return BinaryClassificationMetrics(
        sensitivity=_safe_div(tp, tp + fn),
        specificity=_safe_div(tn, tn + fp),
        ppv=_safe_div(tp, tp + fp),
        npv=_safe_div(tn, tn + fn),
        accuracy=_safe_div(tp + tn, total),
        tp=tp,
        tn=tn,
        fp=fp,
        fn=fn,
    )


def cronbach_alpha(items_by_person: Sequence[Sequence[float]]) -> float | None:
    """Exploratory alpha for approximately tau-equivalent item sets.

    This is not appropriate for every ReadRight task family. It is exposed as a
    utility, not a universal reliability requirement.
    """
    if len(items_by_person) < 2:
        return None
    k = len(items_by_person[0]) if items_by_person else 0
    if k < 2 or any(len(row) != k for row in items_by_person):
        return None

    cols = list(zip(*items_by_person))
    item_vars = [_sample_variance(list(col)) for col in cols]
    total_scores = [sum(row) for row in items_by_person]
    total_var = _sample_variance(total_scores)
    if total_var == 0:
        return None
    return (k / (k - 1)) * (1 - (sum(item_vars) / total_var))


def percent_agreement(rater_a: Sequence[object], rater_b: Sequence[object]) -> float | None:
    if len(rater_a) != len(rater_b) or not rater_a:
        return None
    return sum(a == b for a, b in zip(rater_a, rater_b, strict=True)) / len(rater_a)


def cohens_kappa(rater_a: Sequence[object], rater_b: Sequence[object]) -> float | None:
    if len(rater_a) != len(rater_b) or not rater_a:
        return None
    observed = percent_agreement(rater_a, rater_b)
    labels = set(rater_a) | set(rater_b)
    n = len(rater_a)
    expected = sum((rater_a.count(label) / n) * (rater_b.count(label) / n) for label in labels)
    if observed is None or expected == 1:
        return None
    return (observed - expected) / (1 - expected)


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float] | None:
    if total <= 0 or successes < 0 or successes > total:
        return None
    p = successes / total
    denom = 1 + (z * z / total)
    centre = (p + z * z / (2 * total)) / denom
    margin = (z / denom) * sqrt((p * (1 - p) / total) + (z * z / (4 * total * total)))
    return max(0.0, centre - margin), min(1.0, centre + margin)


def item_difficulty(binary_scores: Iterable[int]) -> float | None:
    values = list(binary_scores)
    if not values or any(v not in (0, 1) for v in values):
        return None
    return mean(values)


def _sample_variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return sum((x - mu) ** 2 for x in values) / (len(values) - 1)
