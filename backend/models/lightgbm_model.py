import numpy as np
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, precision_recall_curve
from sklearn.calibration import CalibratedClassifierCV
from lightgbm import LGBMClassifier
from typing import Dict, Any
import joblib
import os


class StuckPipeLightGBM:
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            "n_estimators": 600,
            "max_depth": 7,
            "learning_rate": 0.05,
            "num_leaves": 63,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_samples": 20,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "is_unbalance": True,
            "objective": "binary",
            "metric": "auc",
            "random_state": 42,
            "n_jobs": -1,
            "verbose": -1,
        }
        if params:
            default_params.update(params)

        self.params = default_params
        self.model = LGBMClassifier(**default_params)
        self.calibrated_model = None
        self.threshold = 0.5
        self.feature_importance_ = None

    def train(
        self, X_train: np.ndarray, y_train: np.ndarray,
        X_val: np.ndarray = None, y_val: np.ndarray = None
    ) -> Dict[str, float]:
        callbacks = []

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)] if X_val is not None else None,
            callbacks=callbacks,
        )

        self.feature_importance_ = self.model.feature_importances_

        if X_val is not None:
            return self.evaluate(X_val, y_val)
        return {}

    def calibrate(self, X_val: np.ndarray, y_val: np.ndarray):
        self.calibrated_model = CalibratedClassifierCV(
            self.model, method="isotonic", cv="prefit"
        )
        self.calibrated_model.fit(X_val, y_val)

    def optimize_threshold(self, X_val: np.ndarray, y_val: np.ndarray) -> float:
        probas = self.predict_proba(X_val)
        precisions, recalls, thresholds = precision_recall_curve(y_val, probas)
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
        best_idx = np.argmax(f1_scores)
        self.threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
        return self.threshold

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return (probas >= self.threshold).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.calibrated_model is not None:
            return self.calibrated_model.predict_proba(X)[:, 1]
        return self.model.predict_proba(X)[:, 1]

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        probas = self.predict_proba(X)
        preds = self.predict(X)
        return {
            "roc_auc": roc_auc_score(y, probas),
            "f1_score": f1_score(y, preds),
            "precision": precision_score(y, preds),
            "recall": recall_score(y, preds),
            "threshold": self.threshold,
        }

    def get_risk_ranking(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return np.argsort(-probas)

    def get_feature_importance(self, feature_names: list) -> Dict[str, float]:
        if self.feature_importance_ is None:
            return {}
        importance_dict = dict(zip(feature_names, self.feature_importance_))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "calibrated_model": self.calibrated_model,
            "threshold": self.threshold,
            "params": self.params,
            "feature_importance": self.feature_importance_,
        }, path)

    def load(self, path: str):
        data = joblib.load(path)
        self.model = data["model"]
        self.calibrated_model = data["calibrated_model"]
        self.threshold = data["threshold"]
        self.params = data["params"]
        self.feature_importance_ = data["feature_importance"]
