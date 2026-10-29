"""Explicit denominators, deterministic ranking and temporal stability intervals."""

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def rank(frame: pd.DataFrame, score: str = "probability") -> pd.DataFrame:
    return frame.sort_values([score, "customer_id"], ascending=[False, True], kind="stable")


def calibration_bins(y, probabilities, bins: int = 10) -> list[dict]:
    y = np.asarray(y, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    indices = np.minimum((p * bins).astype(int), bins - 1)
    result = []
    for index in range(bins):
        mask = indices == index
        count = int(mask.sum())
        result.append(
            {
                "lower": index / bins,
                "upper": (index + 1) / bins,
                "count": count,
                "predicted": float(p[mask].mean()) if count else None,
                "observed": float(y[mask].mean()) if count else None,
            }
        )
    return result


def evaluate(frame: pd.DataFrame, score: str = "probability", capacities=(50, 100)) -> dict:
    if frame.empty:
        raise ValueError("Cannot evaluate an empty population")
    labels = frame.target.to_numpy()
    # Validate before integer conversion; otherwise fractional labels silently
    # truncate (for example 0.5 -> 0), producing plausible but invalid metrics.
    if not np.isin(labels, [0, 1]).all():
        raise ValueError("Evaluation requires binary labels and finite probabilities in [0,1]")
    y = labels.astype(int)
    p = frame[score].to_numpy(dtype=float)
    if not np.isin(y, [0, 1]).all() or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("Evaluation requires binary labels and finite probabilities in [0,1]")
    positives = int(y.sum())
    base = float(y.mean())
    bins = calibration_bins(y, p)
    result = {
        "population": len(frame),
        "positives": positives,
        "base_rate": base,
        "average_precision": float(average_precision_score(y, p)) if positives else None,
        "brier": float(brier_score_loss(y, p)),
        "roc_auc": float(roc_auc_score(y, p)) if 0 < positives < len(y) else None,
        "ece": sum(
            b["count"] / len(y) * abs(b["predicted"] - b["observed"]) for b in bins if b["count"]
        ),
    }
    ordered = rank(frame, score)
    for capacity in capacities:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        selected = ordered.head(capacity)
        captured = int(selected.target.sum())
        precision = captured / len(selected)
        result[f"selected_{capacity}"] = len(selected)
        result[f"captured_{capacity}"] = captured
        result[f"precision_{capacity}"] = precision
        result[f"recall_{capacity}"] = captured / positives if positives else None
        result[f"lift_{capacity}"] = precision / base if positives else None
    return result


def weekly_metrics(frame: pd.DataFrame, score="probability") -> list[dict]:
    return [
        {"as_of": str(origin), **evaluate(group, score)}
        for origin, group in frame.groupby("as_of", sort=True)
    ]


def summarize(frame: pd.DataFrame) -> dict:
    weeks = weekly_metrics(frame)
    keys = [key for key in weeks[0] if key != "as_of"]
    macro = {
        key: float(np.mean([week[key] for week in weeks if week[key] is not None]))
        if any(week[key] is not None for week in weeks)
        else None
        for key in keys
    }
    return {
        "buyer_weeks": len(frame),
        "unique_buyers": int(frame.customer_id.nunique()),
        "weeks": len(weeks),
        "macro_weekly": macro,
        "pooled": evaluate(frame, capacities=()),
        "raw_probability_metrics": {
            key: value
            for key, value in evaluate(frame, "raw_probability", capacities=()).items()
            if key in {"brier", "ece", "average_precision"}
        },
        "weekly": weeks,
        "calibration": calibration_bins(frame.target, frame.probability),
        "cohorts": {
            str(cohort): {
                "buyer_weeks": len(group),
                "base_rate": float(group.target.mean()),
                "brier": float(brier_score_loss(group.target, group.probability)),
                "average_precision": float(average_precision_score(group.target, group.probability))
                if group.target.sum()
                else None,
            }
            for cohort, group in frame.groupby("cohort", sort=True)
        },
    }


def paired_stability(candidate: dict, baseline: dict, seed=20261029, repetitions=1000) -> dict:
    left = pd.DataFrame(candidate["weekly"]).set_index("as_of")
    right = pd.DataFrame(baseline["weekly"]).set_index("as_of")
    if not left.index.equals(right.index):
        raise ValueError("Paired comparisons require exactly the same weekly origins")
    rng = np.random.default_rng(seed)
    n = len(left)
    block = min(4, n)
    starts = rng.integers(0, n - block + 1, size=(repetitions, int(np.ceil(n / block))))
    draws = (starts[:, :, None] + np.arange(block)).reshape(repetitions, -1)[:, :n]
    results = {}
    for metric in ["average_precision", "precision_50", "brier"]:
        deltas = left[metric].to_numpy(dtype=float) - right[metric].to_numpy(dtype=float)
        if not np.isfinite(deltas).all():
            results[metric] = None
            continue
        sample_means = deltas[draws].mean(axis=1)
        results[metric] = {
            "mean_difference": float(deltas.mean()),
            "lower": float(np.quantile(sample_means, 0.025)),
            "upper": float(np.quantile(sample_means, 0.975)),
            "higher_is_better": metric != "brier",
        }
    return {
        "method": "paired non-circular moving blocks of four test weeks; descriptive stability interval",
        "block_weeks": block,
        "repetitions": repetitions,
        "metrics": results,
    }
