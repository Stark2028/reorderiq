import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from reorderiq.features import FEATURES, Fold, connect_orders, snapshot, split_fold


def events(rows):
    frame = pd.DataFrame(rows, columns=["customer_id", "invoice_id", "ordered_at"])
    frame["amount_gbp"] = 10.0
    frame["units"] = 1
    frame["distinct_items"] = 1
    return frame


def test_strict_history_and_half_open_target():
    orders = events(
        [
            (1, "1", "2011-01-02 23:59:59"),
            (1, "2", "2011-01-03 00:00:00"),
            (1, "3", "2011-01-10 00:00:00"),
            (2, "4", "2011-01-03 00:00:00"),
        ]
    )
    with connect_orders(orders) as connection:
        frame = snapshot(connection, "2011-01-03", "2011-01-11")
    assert frame.customer_id.tolist() == [1]  # Buyer 2 does not exist at prediction time.
    assert frame.iloc[0].orders_observed == 1
    assert frame.iloc[0].future_orders == 1
    assert frame.iloc[0].target == 1


def test_future_mutation_cannot_change_features_or_eligibility():
    history = [(1, "1", "2010-12-01"), (2, "2", "2010-12-20")]
    with connect_orders(events(history)) as connection:
        before = snapshot(connection, "2011-01-03", "2011-02-01")
    with connect_orders(
        events(history + [(1, "3", "2011-01-04"), (3, "4", "2011-01-05")])
    ) as connection:
        after = snapshot(connection, "2011-01-03", "2011-02-01")
    assert_frame_equal(before[["customer_id", *FEATURES]], after[["customer_id", *FEATURES]])
    assert before.target.sum() == 0
    assert after.target.sum() == 1


def test_incomplete_labels_and_non_monday_rejected():
    with connect_orders(events([(1, "1", "2010-12-01")])) as connection:
        with pytest.raises(ValueError, match="fully observed"):
            snapshot(connection, "2011-01-03", "2011-01-09")
        with pytest.raises(ValueError, match="Monday"):
            snapshot(connection, "2011-01-04", "2011-02-01")


def test_fold_does_not_use_unmatured_training_labels():
    frame = pd.DataFrame(
        {
            "as_of": ["2010-12-27", "2011-01-03", "2011-01-10", "2011-01-17"],
            "label_end": ["2011-01-03", "2011-01-10", "2011-01-17", "2011-01-24"],
        }
    )
    train, calibration, evaluation = split_fold(
        frame, Fold("test", "2011-01-03", "2011-01-17", "2011-01-24")
    )
    assert train.as_of.tolist() == ["2010-12-27"]
    assert calibration.as_of.tolist() == ["2011-01-03", "2011-01-10"]
    assert evaluation.as_of.tolist() == ["2011-01-17"]
