"""SQL snapshots with explicit temporal guards and fixed feature names."""

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = [
    "recency_days",
    "observed_tenure_days",
    "orders_observed",
    "spend_observed",
    "mean_basket_gbp",
    "mean_distinct_items",
    "mean_gap_days",
    "orders_7d",
    "orders_30d",
    "orders_90d",
    "orders_180d",
    "spend_30d",
    "spend_90d",
    "units_30d",
    "cadence_ratio",
    "recent_order_share",
    "recent_spend_share",
]


@dataclass(frozen=True)
class Fold:
    name: str
    fit_end: str
    evaluation_start: str
    evaluation_end: str


FOLDS = [
    Fold("dev_1", "2010-12-06", "2011-01-03", "2011-03-07"),
    Fold("dev_2", "2011-03-07", "2011-05-02", "2011-07-04"),
    Fold("final", "2011-07-04", "2011-09-05", "2011-12-05"),
]


def protocol() -> dict:
    return {
        "version": 1,
        "horizon_days": 7,
        "active_days": 180,
        "snapshot_start": "2010-04-05",
        "seed": 20261029,
        "folds": [asdict(fold) for fold in FOLDS],
        "features": FEATURES,
        "model_settings": {
            "gradient_boosting": {
                "max_iter": 120,
                "max_leaf_nodes": 15,
                "learning_rate": 0.07,
                "l2_regularization": 5.0,
                "early_stopping": False,
            },
            "logistic": {"C": 1.0, "max_iter": 1200},
            "calibration": "logistic sigmoid on clipped logits, C=1",
        },
    }


def connect_orders(orders: pd.DataFrame) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    frame = orders.copy()
    frame["ordered_at"] = pd.to_datetime(frame.ordered_at).dt.strftime("%Y-%m-%d %H:%M:%S")
    frame.to_sql("orders", connection, index=False)
    connection.execute("CREATE INDEX order_time ON orders(ordered_at)")
    connection.execute("CREATE INDEX buyer_time ON orders(customer_id, ordered_at)")
    return connection


def snapshot(
    connection: sqlite3.Connection, as_of: str | pd.Timestamp, observation_end: str | pd.Timestamp
) -> pd.DataFrame:
    origin = pd.Timestamp(as_of)
    end = origin + pd.Timedelta(days=7)
    if origin.tzinfo is not None or origin != origin.normalize() or origin.day_of_week != 0:
        raise ValueError("Snapshot must be a Monday at midnight in source wall time")
    if end > pd.Timestamp(observation_end):
        raise ValueError("Label window is not fully observed")
    sql = (Path(__file__).parent / "sql" / "snapshot.sql").read_text(encoding="utf-8")
    frame = pd.read_sql_query(
        sql,
        connection,
        params={
            "as_of": origin.strftime("%Y-%m-%d %H:%M:%S"),
            "label_end": end.strftime("%Y-%m-%d %H:%M:%S"),
            "active_days": 180,
        },
    )
    frame["cadence_ratio"] = np.minimum(
        frame.recency_days / np.maximum(frame.mean_gap_days, 1), 365
    )
    frame["recent_order_share"] = frame.orders_30d / np.maximum(frame.orders_90d, 1)
    frame["recent_spend_share"] = frame.spend_30d / np.maximum(frame.spend_90d, 0.01)
    frame["cohort"] = np.select(
        [frame.observed_tenure_days <= 30, frame.orders_90d >= 4],
        ["newly_observed", "frequent"],
        default="occasional",
    )
    return frame


def build_snapshots(
    orders: pd.DataFrame, observation_end: str, start: str = "2010-04-05"
) -> pd.DataFrame:
    with connect_orders(orders) as connection:
        origins = pd.date_range(
            start, pd.Timestamp(observation_end) - pd.Timedelta(days=7), freq="W-MON"
        )
        frames = []
        for index, origin in enumerate(origins):
            frames.append(snapshot(connection, origin, observation_end))
            if index % 15 == 0:
                print(f"SQL snapshot {index + 1}/{len(origins)}: {origin.date()}", flush=True)
    if not frames:
        raise ValueError("No fully observed snapshots")
    return pd.concat(frames, ignore_index=True)


def split_fold(frame: pd.DataFrame, fold: Fold) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    origins = pd.to_datetime(frame.as_of)
    ends = pd.to_datetime(frame.label_end)
    fit_end, eval_start, eval_end = map(
        pd.Timestamp, [fold.fit_end, fold.evaluation_start, fold.evaluation_end]
    )
    if not fit_end < eval_start < eval_end:
        raise ValueError("Fold boundaries must be strictly chronological")
    train = frame[(origins < fit_end) & (ends <= fit_end)].copy()
    calibration = frame[(origins >= fit_end) & (origins < eval_start) & (ends <= eval_start)].copy()
    evaluation = frame[(origins >= eval_start) & (origins < eval_end) & (ends <= eval_end)].copy()
    if any(part.empty for part in [train, calibration, evaluation]):
        raise ValueError(f"Empty temporal partition in {fold.name}")
    return train, calibration, evaluation
