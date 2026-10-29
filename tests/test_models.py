import numpy as np
import pandas as pd
import pytest

from reorderiq.features import FEATURES
from reorderiq.models import fit_model
from reorderiq.pipeline import choose_model


def sample(origin, end, size=80):
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({feature: rng.uniform(1, 30, size) for feature in FEATURES})
    frame["customer_id"] = np.arange(size)
    frame["orders_observed"] = 1 + ((31 - frame.recency_days) / 4).astype(int)
    frame["observed_tenure_days"] = 100.0
    frame["as_of"] = origin
    frame["label_end"] = end
    frame["target"] = (frame.recency_days < 13).astype(int)
    return frame


@pytest.mark.parametrize("model_id", ["recency", "gamma_poisson", "logistic", "gradient_boosting"])
def test_candidates_produce_bounded_monotone_calibrated_probabilities(model_id):
    train = sample("2011-01-03", "2011-01-10")
    calibration = sample("2011-01-10", "2011-01-17")
    bundle = fit_model(model_id, train, calibration)
    raw, calibrated = bundle.predict(calibration)
    assert np.isfinite(raw).all() and np.isfinite(calibrated).all()
    assert ((calibrated >= 0) & (calibrated <= 1)).all()
    assert bundle.calibrator.coef_[0, 0] >= 0


def test_calibration_overlap_rejected():
    with pytest.raises(ValueError, match="overlap"):
        fit_model("recency", sample("2011-01-03", "2011-01-10"), sample("2011-01-03", "2011-01-10"))


def test_model_selection_rejects_final_results():
    with pytest.raises(ValueError, match="development"):
        choose_model({"dev_1": {}, "dev_2": {}, "final": {}})
