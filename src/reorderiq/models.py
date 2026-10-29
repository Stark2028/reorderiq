"""Fixed candidate models and independent, monotone probability calibration."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from .features import FEATURES, protocol

MODEL_NAMES = {
    "recency": "Recency baseline",
    "gamma_poisson": "Gamma–Poisson",
    "logistic": "Logistic regression",
    "gradient_boosting": "Gradient boosting",
}


class RecencyModel:
    def fit(self, frame: pd.DataFrame, y=None):
        return self

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        return np.exp(-frame.recency_days.to_numpy(dtype=float) / 30)


class GammaPoisson:
    """Repeat events after first observed order, with exposure in days.

    Stationary Gamma-Poisson baseline. This is not Udaan's modified model and
    does not model dropout, seasonality or causal effects of outreach.
    """

    def fit(self, frame: pd.DataFrame, y=None):
        latest = frame.sort_values("as_of").drop_duplicates("customer_id", keep="last")
        counts = np.maximum(latest.orders_observed.to_numpy(dtype=float) - 1, 0)
        exposure = np.maximum(latest.observed_tenure_days.to_numpy(dtype=float), 1)

        def objective(parameters):
            alpha, beta = np.exp(parameters)
            logp = (
                gammaln(counts + alpha)
                - gammaln(alpha)
                - gammaln(counts + 1)
                + alpha * (np.log(beta) - np.log(beta + exposure))
                + counts * (np.log(exposure) - np.log(beta + exposure))
            )
            return -float(np.mean(logp))

        result = minimize(
            objective, np.log([1.0, 30.0]), method="L-BFGS-B", bounds=[(-7, 9), (-7, 13)]
        )
        if not result.success or not np.isfinite(result.fun):
            raise ValueError(f"Gamma-Poisson fit failed: {result.message}")
        self.alpha, self.beta = np.exp(result.x)
        return self

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        shape = self.alpha + np.maximum(frame.orders_observed.to_numpy(dtype=float) - 1, 0)
        rate = self.beta + np.maximum(frame.observed_tenure_days.to_numpy(dtype=float), 1)
        return -np.expm1(shape * (np.log(rate) - np.log(rate + 7)))


def logit(probability: np.ndarray) -> np.ndarray:
    clipped = np.clip(probability, 1e-6, 1 - 1e-6)
    return np.log(clipped / (1 - clipped)).reshape(-1, 1)


@dataclass
class ModelBundle:
    model_id: str
    estimator: object
    calibrator: LogisticRegression

    def raw_probability(self, frame: pd.DataFrame) -> np.ndarray:
        if self.model_id in {"recency", "gamma_poisson"}:
            return self.estimator.predict_proba(frame)
        return self.estimator.predict_proba(frame[FEATURES])[:, 1]

    def predict(self, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        raw = self.raw_probability(frame)
        return raw, self.calibrator.predict_proba(logit(raw))[:, 1]


def fit_model(
    model_id: str, train: pd.DataFrame, calibration: pd.DataFrame, seed: int = 20261029
) -> ModelBundle:
    if train.target.nunique() != 2 or calibration.target.nunique() != 2:
        raise ValueError("Both classes are required in training and calibration")
    if pd.to_datetime(train.label_end).max() > pd.to_datetime(calibration.as_of).min():
        raise ValueError("Training labels overlap calibration origins")
    if model_id == "recency":
        estimator = RecencyModel().fit(train)
    elif model_id == "gamma_poisson":
        estimator = GammaPoisson().fit(train)
    elif model_id == "logistic":
        estimator = make_pipeline(
            FunctionTransformer(np.log1p, feature_names_out="one-to-one"),
            StandardScaler(),
            LogisticRegression(**protocol()["model_settings"]["logistic"], random_state=seed),
        )
        estimator.fit(train[FEATURES], train.target)
    elif model_id == "gradient_boosting":
        estimator = HistGradientBoostingClassifier(
            **protocol()["model_settings"]["gradient_boosting"], random_state=seed
        )
        estimator.fit(train[FEATURES], train.target)
    else:
        raise ValueError(f"Unknown model: {model_id}")
    bundle = ModelBundle(model_id, estimator, None)
    calibrator = LogisticRegression(C=1.0, max_iter=1000, random_state=seed)
    calibrator.fit(logit(bundle.raw_probability(calibration)), calibration.target)
    if calibrator.coef_[0, 0] < 0:
        raise ValueError(
            f"{model_id}: calibration reversed ranking; inspect the development protocol"
        )
    bundle.calibrator = calibrator
    return bundle
