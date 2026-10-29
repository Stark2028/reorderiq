"""Recompute evidence from trusted local artifacts, including actual order labels."""

from pathlib import Path

import numpy as np
import pandas as pd

from .features import FEATURES, connect_orders, snapshot
from .io import read_json, sha256_file
from .metrics import summarize


def verify_run(run_dir: Path) -> dict:
    manifest = read_json(run_dir / "manifest.json")
    if manifest["status"] != "complete":
        raise ValueError("Run is incomplete")
    for name, digest in manifest["files"].items():
        if Path(name).name != name or sha256_file(run_dir / name) != digest:
            raise ValueError(f"Artifact integrity check failed: {name}")
    report = read_json(run_dir / "report.json")
    selection = read_json(run_dir / "selection.json")
    if (
        report["selected_model"] != selection["selected_model"]
        or sha256_file(run_dir / "selection.json") != manifest["selection_sha256"]
    ):
        raise ValueError("Selection record is inconsistent")
    predictions = pd.read_parquet(run_dir / "predictions.parquet")
    orders = pd.read_parquet(run_dir / "orders.parquet")
    audit = read_json(run_dir / "audit.json")
    reference = predictions[predictions.model_id == report["selected_model"]]
    expected_models = set(report["final"])
    if predictions.empty or set(predictions.model_id) != expected_models or reference.empty:
        raise ValueError("Prediction models disagree with the declared candidate population")
    if predictions.duplicated(["model_id", "as_of", "customer_id"]).any():
        raise ValueError("Duplicate buyer snapshot within a candidate model")
    reference = reference.sort_values(["as_of", "customer_id"]).reset_index(drop=True)
    for model_id, frame in predictions.groupby("model_id"):
        ordered = frame.sort_values(["as_of", "customer_id"]).reset_index(drop=True)
        if not ordered[["as_of", "customer_id"]].equals(reference[["as_of", "customer_id"]]):
            raise ValueError(f"Candidate {model_id} evaluated on inconsistent buyer snapshot keys")
        if not np.array_equal(ordered.target.to_numpy(), reference.target.to_numpy()):
            raise ValueError("Models evaluated on inconsistent targets")
    with connect_orders(orders) as connection:
        for origin, saved in reference.groupby("as_of", sort=True):
            rebuilt = snapshot(connection, origin, audit["observation_end_exclusive"])
            saved = saved.sort_values("customer_id").reset_index(drop=True)
            rebuilt = rebuilt.sort_values("customer_id").reset_index(drop=True)
            if not saved.customer_id.equals(rebuilt.customer_id):
                raise ValueError(f"Population mismatch at {origin}")
            if not np.array_equal(saved.target.to_numpy(), rebuilt.target.to_numpy()):
                raise ValueError(f"Order labels disagree at {origin}")
            if not np.allclose(saved[FEATURES], rebuilt[FEATURES], rtol=0, atol=1e-10):
                raise ValueError(f"Historical features disagree at {origin}")
    for model_id, frame in predictions.groupby("model_id"):
        recomputed = summarize(frame)
        recorded = report["final"][model_id]
        for key, value in recomputed["macro_weekly"].items():
            expected = recorded["macro_weekly"][key]
            if value is None and expected is None:
                continue
            if not np.isclose(value, expected, rtol=0, atol=1e-12):
                raise ValueError(f"Metric mismatch for {model_id}: {key}")
    return {
        "status": "passed",
        "run_id": manifest["run_id"],
        "artifact_files": len(manifest["files"]),
        "recomputed_weekly_populations": int(reference.as_of.nunique()),
        "recomputed_buyer_weeks": len(reference),
        "models": int(predictions.model_id.nunique()),
        "checks": [
            "all recorded artifact hashes",
            "frozen development selection",
            "SQL populations rebuilt from orders",
            "labels rebuilt from actual future orders",
            "pre-cutoff features rebuilt",
            "reported macro metrics recomputed",
            "exact shared buyer snapshot keys and targets across candidates",
        ],
    }
