import numpy as np
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix, precision_recall_curve
)
from xgboost import XGBClassifier
from typing import Dict, Any, Tuple
import joblib
import os


class StuckPipeXGBoost:
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            "n_estimators": 500,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 5,
            "gamma": 0.1,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "scale_pos_weight": 10,
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "random_state": 42,
            "n_jobs": -1,
            "use_label_encoder": False,
        }
        if params:
            default_params.update(params)

        self.params = default_params
        self.model = XGBClassifier(**default_params)
        self.threshold = 0.5
        self.feature_importance_ = None

    def train(
        self, X_train: np.ndarray, y_train: np.ndarray,
        X_val: np.ndarray = None, y_val: np.ndarray = None
    ) -> Dict[str, float]:
        eval_set = [(X_train, y_train)]
        if X_val is not None:
            eval_set.append((X_val, y_val))

        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=50,
        )

        self.feature_importance_ = self.model.feature_importances_

        if X_val is not None:
            return self.evaluate(X_val, y_val)
        return {}

    def optimize_threshold(self, X_val: np.ndarray, y_val: np.ndarray) -> float:
        probas = self.model.predict_proba(X_val)[:, 1]
        precisions, recalls, thresholds = precision_recall_curve(y_val, probas)
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
        best_idx = np.argmax(f1_scores)
        self.threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
        return self.threshold

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.model.predict_proba(X)[:, 1]
        return (probas >= self.threshold).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        probas = self.predict_proba(X)
        preds = self.predict(X)

        metrics = {
            "roc_auc": roc_auc_score(y, probas),
            "f1_score": f1_score(y, preds),
            "precision": precision_score(y, preds),
            "recall": recall_score(y, preds),
            "threshold": self.threshold,
        }
        return metrics

    def get_feature_importance(self, feature_names: list) -> Dict[str, float]:
        if self.feature_importance_ is None:
            return {}
        importance_dict = dict(zip(feature_names, self.feature_importance_))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "threshold": self.threshold,
            "params": self.params,
            "feature_importance": self.feature_importance_,
        }, path)

    def load(self, path: str):
        data = joblib.load(path)
        self.model = data["model"]
        self.threshold = data["threshold"]
        self.params = data["params"]
        self.feature_importance_ = data["feature_importance"]
