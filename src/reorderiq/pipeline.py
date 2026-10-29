"""Reproducible experiment orchestration: development selection precedes final evaluation."""

import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits

from .features import FEATURES, FOLDS, build_snapshots, protocol, split_fold
from .ingest import prepare
from .io import code_fingerprint, read_json, sha256_file, write_json
from .metrics import paired_stability, summarize
from .models import MODEL_NAMES, fit_model


def choose_model(development: dict) -> tuple[str, dict]:
    if set(development) != {"dev_1", "dev_2"}:
        raise ValueError("Selection accepts the two development folds only")
    table = {}
    for model_id in MODEL_NAMES:
        records = [development[name][model_id]["macro_weekly"] for name in sorted(development)]
        table[model_id] = {
            "mean_weekly_ap": float(np.mean([r["average_precision"] for r in records])),
            "mean_weekly_brier": float(np.mean([r["brier"] for r in records])),
        }
    chosen = min(
        table, key=lambda key: (-table[key]["mean_weekly_ap"], table[key]["mean_weekly_brier"], key)
    )
    return chosen, table


def score(bundle, frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    raw, calibrated = bundle.predict(frame)
    result["raw_probability"] = raw
    result["probability"] = calibrated
    result["model_id"] = bundle.model_id
    return result


def feature_importance(bundle, frame: pd.DataFrame, seed: int) -> list[dict]:
    sample = frame.sample(min(4000, len(frame)), random_state=seed).copy()
    _, original = bundle.predict(sample)
    baseline = average_precision_score(sample.target, original)
    rng = np.random.default_rng(seed)
    result = []
    for feature in FEATURES:
        differences = []
        for _ in range(2):
            shuffled = sample.copy()
            shuffled[feature] = rng.permutation(shuffled[feature].to_numpy())
            _, probabilities = bundle.predict(shuffled)
            differences.append(baseline - average_precision_score(sample.target, probabilities))
        result.append({"feature": feature, "ap_drop": float(np.mean(differences))})
    return sorted(result, key=lambda record: -record["ap_drop"])


def make_markdown(report: dict) -> str:
    lines = [
        "# ReorderIQ measured experiment",
        "",
        f"Run: `{report['run_id']}`",
        "",
        f"Selected on development folds: **{MODEL_NAMES[report['selected_model']]}**.",
        "",
        "All metrics below are from the final temporal holdout. Models remain frozen throughout each fold.",
        "",
        "| Candidate | Mean weekly AP | Brier (lower) | Precision @50 | Lift @50 |",
        "|---|---:|---:|---:|---:|",
    ]
    for model_id, summary in report["final"].items():
        metrics = summary["macro_weekly"]
        lines.append(
            f"| {MODEL_NAMES[model_id]} | {metrics['average_precision']:.4f} | {metrics['brier']:.4f} | {metrics['precision_50']:.3f} | {metrics['lift_50']:.2f} |"
        )
    chosen = report["final"][report["selected_model"]]
    lines.extend(
        [
            "",
            f"Final population: {chosen['buyer_weeks']:,} buyer-weeks, {chosen['unique_buyers']:,} distinct observed buyers, {chosen['weeks']} weekly origins.",
            "",
            "## Interpretation and limits",
            "",
            "Average precision is computed separately each week, then equally averaged. Capacity denominators use the actual selected population. Lift is predictive enrichment over that week's order rate; it is not incremental orders caused by contact.",
            "",
            "Dataset: Chen, D. (2012), Online Retail II, UCI, DOI:10.24432/C5CG6D, CC BY 4.0. UK giftware transactions from 2009-2011; many buyers are wholesalers. These are not Udaan records or current Indian retail conditions. Currency is GBP.",
            "",
            "The target is a positive merchandise order placed, not net retained purchases, profit or permanent churn. Cancellations and non-merchandise lines are excluded, and future returns never rewrite historical eligibility. First-seen tenure is left truncated.",
            "",
            "Calibration uses a separate later interval. The final period is evaluated after development-only model selection; no final-period tuning is authorized by this result. Other candidates are published for transparency, not to retrospectively replace the selected model.",
            "",
            "Temporal block intervals describe stability over the observed test weeks; they do not establish causal, independent-buyer or population-wide significance. Permutation importance is predictive association and can understate correlated features.",
            "",
            "See manifest.json, selection.json, report.json, snapshots.parquet, predictions.parquet and model bundles for exact provenance and reproduction evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def run_experiment(data_dir: Path, runs_dir: Path) -> Path:
    settings = protocol()
    frozen_code = code_fingerprint()
    processed = data_dir / "processed"
    orders_path = processed / "orders.parquet"
    audit_path = processed / "audit.json"
    if not orders_path.exists() or not audit_path.exists():
        prepare(data_dir)
    audit = read_json(audit_path)
    if sha256_file(orders_path) != audit["orders_sha256"]:
        raise ValueError("Normalized orders disagree with ingestion audit; rerun prepare")
    orders = pd.read_parquet(orders_path)
    package_root = Path(__file__).parent
    feature_signature = hashlib.sha256(
        (
            audit["orders_sha256"]
            + json.dumps(settings, sort_keys=True)
            + sha256_file(package_root / "features.py")
            + sha256_file(package_root / "sql" / "snapshot.sql")
        ).encode()
    ).hexdigest()
    snapshots_path = processed / f"snapshots-{feature_signature[:12]}.parquet"
    if snapshots_path.exists():
        cache = read_json(snapshots_path.with_suffix(".json"))
        if cache["sha256"] != sha256_file(snapshots_path):
            raise ValueError("Snapshot cache hash mismatch")
        snapshots = pd.read_parquet(snapshots_path)
    else:
        snapshots = build_snapshots(orders, audit["observation_end_exclusive"])
        snapshots.to_parquet(snapshots_path, index=False)
        write_json(
            snapshots_path.with_suffix(".json"),
            {"feature_signature": feature_signature, "sha256": sha256_file(snapshots_path)},
        )
    if (
        snapshots.duplicated(["as_of", "customer_id"]).any()
        or not np.isfinite(snapshots[FEATURES].to_numpy()).all()
    ):
        raise ValueError("Invalid or duplicate feature snapshots")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + feature_signature[:8]
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    with ZipFile(run_dir / "source.zip", "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(package_root.rglob("*")):
            if path.is_file() and (
                path.suffix in {".py", ".sql", ".html", ".css", ".js", ".woff2"}
                or path.name == "LICENSE.txt"
            ):
                archive.write(path, path.relative_to(package_root).as_posix())
    write_json(run_dir / "config.json", settings)
    write_json(run_dir / "audit.json", audit)
    orders.to_parquet(run_dir / "orders.parquet", index=False)
    snapshots.to_parquet(run_dir / "snapshots.parquet", index=False)
    development = {}
    fold_details = {}
    seed = settings["seed"]
    # Bound parallel native BLAS/OpenMP pools for reproducible local CPU use.
    with threadpool_limits(limits=1):
        for fold in FOLDS[:2]:
            train, calibration, evaluation = split_fold(snapshots, fold)
            fold_details[fold.name] = {
                "train_rows": len(train),
                "calibration_rows": len(calibration),
                "evaluation_rows": len(evaluation),
            }
            development[fold.name] = {}
            for model_id in MODEL_NAMES:
                print(
                    f"{fold.name}: fitting {model_id} ({len(train):,} training buyer-weeks)",
                    flush=True,
                )
                bundle = fit_model(model_id, train, calibration, seed)
                development[fold.name][model_id] = summarize(score(bundle, evaluation))
        selected, selection_table = choose_model(development)
        selection = {
            "selected_model": selected,
            "basis": "equal-weight development-fold mean weekly AP; lower Brier tie break",
            "candidates": selection_table,
            "development_folds": [f.name for f in FOLDS[:2]],
            "written_before_final_fit": True,
            "locked_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        write_json(run_dir / "selection.json", selection)
        selection_hash = sha256_file(run_dir / "selection.json")
        print(f"Development choice frozen: {selected}. Opening final holdout now.", flush=True)
        fold = FOLDS[-1]
        train, calibration, evaluation = split_fold(snapshots, fold)
        fold_details[fold.name] = {
            "train_rows": len(train),
            "calibration_rows": len(calibration),
            "evaluation_rows": len(evaluation),
        }
        final, predictions, calibration_parameters = {}, [], {}
        chosen_bundle = None
        for model_id in MODEL_NAMES:
            print(f"final: fitting {model_id}", flush=True)
            bundle = fit_model(model_id, train, calibration, seed)
            predicted = score(bundle, evaluation)
            predictions.append(predicted)
            final[model_id] = summarize(predicted)
            calibration_parameters[model_id] = {
                "slope": float(bundle.calibrator.coef_[0, 0]),
                "intercept": float(bundle.calibrator.intercept_[0]),
            }
            joblib.dump(bundle, run_dir / f"model-{model_id}.joblib")
            if model_id == selected:
                chosen_bundle = bundle
        importance = feature_importance(chosen_bundle, evaluation, seed)
    pd.concat(predictions, ignore_index=True).to_parquet(
        run_dir / "predictions.parquet", index=False
    )
    if sha256_file(run_dir / "selection.json") != selection_hash:
        raise ValueError("Model selection record changed during final evaluation")
    report = {
        "run_id": run_id,
        "selected_model": selected,
        "model_names": MODEL_NAMES,
        "snapshot_count": int(snapshots.as_of.nunique()),
        "source": "UCI Online Retail II · UK giftware · GBP · 2009–2011",
        "target": "any positive merchandise order in the next seven days",
        "development": development,
        "selection": selection,
        "fold_sizes": fold_details,
        "final": final,
        "comparison_to_recency": paired_stability(final[selected], final["recency"], seed),
        "comparison_to_gamma_poisson": paired_stability(
            final[selected], final["gamma_poisson"], seed
        ),
        "calibration_parameters": calibration_parameters,
        "feature_importance": importance,
        "feature_importance_method": "two permutations, fixed sample up to 4,000 final buyer-weeks; AP drop; association only",
        "limitations": [
            "Public UK giftware benchmark, not Udaan data",
            "Purchase propensity does not identify an effect of outreach",
            "Historical first-seen tenure is left truncated",
            "Positive placed-order target excludes cancellations, adjustments and non-merchandise lines",
            "Models frozen within each fold; holiday and seasonal drift remain",
            "Short test period limits stability-interval interpretation",
        ],
    }
    write_json(run_dir / "report.json", report)
    (run_dir / "REPORT.md").write_text(make_markdown(report), encoding="utf-8")
    if code_fingerprint() != frozen_code:
        raise ValueError("Source changed during experiment; this run remains incomplete")
    manifest = {
        "status": "complete",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.system(),
        "seed": seed,
        "code_sha256": frozen_code,
        "source_workbook_sha256": audit["workbook_sha256"],
        "feature_signature": feature_signature,
        "selection_sha256": selection_hash,
        "versions": {
            package: importlib.metadata.version(package)
            for package in ["numpy", "pandas", "scipy", "scikit-learn", "pyarrow", "joblib"]
        },
        "files": {
            path.name: sha256_file(path) for path in sorted(run_dir.iterdir()) if path.is_file()
        },
    }
    write_json(run_dir / "manifest.json", manifest)
    write_json(runs_dir / "latest.json", {"run_id": run_id})
    print(
        f"Complete: {run_dir}\nSelected: {selected}\n"
        + make_markdown(report).split("## Interpretation")[0],
        flush=True,
    )
    return run_dir
