from pathlib import Path

import pandas as pd
import pytest

from reorderiq.features import connect_orders, snapshot
from reorderiq.io import read_json, sha256_file, write_json
from reorderiq.metrics import summarize
from reorderiq.verify import verify_run


@pytest.fixture
def experiment(tmp_path: Path):
    orders = pd.DataFrame(
        {
            "customer_id": [1, 2, 1, 2],
            "invoice_id": ["1", "2", "3", "4"],
            "ordered_at": pd.to_datetime(["2010-12-20", "2010-12-25", "2011-01-04", "2011-01-11"]),
            "amount_gbp": [10.0, 20.0, 30.0, 40.0],
            "units": [1, 2, 3, 4],
            "distinct_items": [1, 1, 1, 1],
        }
    )
    with connect_orders(orders) as connection:
        frames = [snapshot(connection, date, "2011-01-18") for date in ["2011-01-03", "2011-01-10"]]
    base = pd.concat(frames, ignore_index=True)
    predictions, summaries = [], {}
    for model_id in ["recency", "logistic"]:
        frame = base.copy()
        frame["model_id"] = model_id
        frame["probability"] = frame.customer_id.map({1: 0.8, 2: 0.2})
        frame["raw_probability"] = frame.probability
        predictions.append(frame)
        summaries[model_id] = summarize(frame)
    orders.to_parquet(tmp_path / "orders.parquet", index=False)
    pd.concat(predictions, ignore_index=True).to_parquet(
        tmp_path / "predictions.parquet", index=False
    )
    write_json(tmp_path / "audit.json", {"observation_end_exclusive": "2011-01-18"})
    write_json(tmp_path / "report.json", {"selected_model": "recency", "final": summaries})
    write_json(tmp_path / "selection.json", {"selected_model": "recency"})
    write_json(
        tmp_path / "manifest.json",
        {
            "status": "complete",
            "run_id": "test-only",
            "selection_sha256": sha256_file(tmp_path / "selection.json"),
            "files": {file.name: sha256_file(file) for file in tmp_path.iterdir()},
        },
    )
    return tmp_path


def replace_predictions(run_dir, frame):
    path = run_dir / "predictions.parquet"
    frame.to_parquet(path, index=False)
    manifest = read_json(run_dir / "manifest.json")
    manifest["files"][path.name] = sha256_file(path)
    write_json(run_dir / "manifest.json", manifest)


def test_consistent_experiment_is_verified(experiment):
    result = verify_run(experiment)
    assert result["status"] == "passed"
    assert result["models"] == 2


def test_candidate_with_different_buyers_cannot_pass_using_same_target_array(experiment):
    frame = pd.read_parquet(experiment / "predictions.parquet")
    frame.loc[frame.model_id == "logistic", "customer_id"] += 1000
    replace_predictions(experiment, frame)
    with pytest.raises(ValueError, match="snapshot keys"):
        verify_run(experiment)


def test_missing_candidate_is_rejected_even_if_remaining_metrics_match(experiment):
    frame = pd.read_parquet(experiment / "predictions.parquet")
    replace_predictions(experiment, frame[frame.model_id == "recency"])
    with pytest.raises(ValueError, match="candidate population"):
        verify_run(experiment)


def test_duplicate_candidate_buyer_weeks_are_rejected(experiment):
    frame = pd.read_parquet(experiment / "predictions.parquet")
    replace_predictions(experiment, pd.concat([frame, frame.iloc[[0]]], ignore_index=True))
    with pytest.raises(ValueError, match="Duplicate"):
        verify_run(experiment)
