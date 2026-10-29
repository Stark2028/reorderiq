import numpy as np
import pandas as pd
import pytest

from reorderiq.ingest import normalize
from reorderiq.metrics import evaluate, rank


def test_invoice_lines_returns_duplicates_and_audit():
    raw = pd.DataFrame(
        [
            ["1", "12345", 1, "2011-01-01", 2, 10],
            ["1", "12346", 2, "2011-01-01", 3, 10],
            ["1", "12346", 2, "2011-01-01", 3, 10],
            ["C2", "12345", -1, "2011-01-02", 2, 10],
            ["3", "POST", 1, "2011-01-02", 5, 10],
            ["4", "12345", 1, "2011-01-02", 5, None],
            ["5", "12345", 1, "2011-01-03 12:00", 5, 10],
        ],
        columns=["Invoice", "StockCode", "Quantity", "InvoiceDate", "Price", "Customer ID"],
    )
    raw.InvoiceDate = pd.to_datetime(raw.InvoiceDate, format="mixed")
    orders, audit = normalize(raw)
    assert len(orders) == 1
    assert orders.iloc[0].amount_gbp == 8
    assert orders.iloc[0].distinct_items == 2
    assert audit["exclusions"]["exact_duplicate_line"] == 1
    assert audit["exclusions"]["outside_complete_observation"] == 1
    assert sum(audit["exclusions"].values()) + audit["accepted_lines"] == len(raw)


def test_conflicting_invoice_fails_instead_of_silent_split():
    raw = pd.DataFrame(
        {
            "Invoice": ["1", "1"],
            "StockCode": ["12345", "12346"],
            "Quantity": [1, 1],
            "InvoiceDate": pd.to_datetime(["2011-01-01", "2011-01-02"]),
            "Price": [2, 2],
            "Customer ID": [10, 11],
        }
    )
    with pytest.raises(ValueError, match="Conflicting"):
        normalize(raw, pd.Timestamp("2011-01-03"))


def test_multiminute_invoice_becomes_available_at_last_line():
    raw = pd.DataFrame(
        {
            "Invoice": ["1", "1"],
            "StockCode": ["12345", "12346"],
            "Quantity": [1, 2],
            "InvoiceDate": pd.to_datetime(["2011-01-01 12:01", "2011-01-01 12:03"]),
            "Price": [2, 3],
            "Customer ID": [10, 10],
        }
    )
    orders, audit = normalize(raw, pd.Timestamp("2011-01-03"))
    assert len(orders) == 1
    assert orders.iloc[0].ordered_at == pd.Timestamp("2011-01-01 12:03")
    assert orders.iloc[0].amount_gbp == 8
    assert audit["multi_timestamp_invoices"] == 1


def test_invoice_crossing_observation_end_is_wholly_unobserved():
    raw = pd.DataFrame(
        {
            "Invoice": ["1", "1", "2"],
            "StockCode": ["12345", "12346", "12347"],
            "Quantity": [1, 1, 1],
            "InvoiceDate": pd.to_datetime(
                ["2011-01-02 23:59", "2011-01-03 00:01", "2011-01-01 12:00"]
            ),
            "Price": [2, 3, 4],
            "Customer ID": [10, 10, 20],
        }
    )
    orders, audit = normalize(raw, pd.Timestamp("2011-01-03"))
    assert orders.invoice_id.tolist() == ["2"]
    assert audit["exclusions"]["outside_complete_observation"] == 2


def test_capacity_ties_and_actual_denominator():
    frame = pd.DataFrame(
        {"customer_id": [3, 1, 2], "probability": [0.5, 0.5, 0.5], "target": [1, 0, 1]}
    )
    assert rank(frame).customer_id.tolist() == [1, 2, 3]
    result = evaluate(frame, capacities=(2, 50))
    assert result["precision_2"] == 0.5
    assert result["selected_50"] == 3
    assert result["precision_50"] == 2 / 3
    assert result["lift_50"] == 1


def test_undefined_metrics_and_invalid_probabilities():
    frame = pd.DataFrame({"customer_id": [1, 2], "probability": [0.1, 0.2], "target": [0, 0]})
    result = evaluate(frame)
    assert result["average_precision"] is None
    assert result["lift_50"] is None
    assert result["roc_auc"] is None
    frame.loc[0, "probability"] = np.nan
    with pytest.raises(ValueError, match="finite"):
        evaluate(frame)


@pytest.mark.parametrize("labels", [[0.5, 1], [0, 1.9], [float("nan"), 1]])
def test_fractional_or_missing_targets_are_rejected_before_integer_conversion(labels):
    frame = pd.DataFrame({"customer_id": [1, 2], "probability": [0.2, 0.8], "target": labels})
    with pytest.raises(ValueError, match="binary labels"):
        evaluate(frame)
