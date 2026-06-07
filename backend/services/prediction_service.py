import numpy as np
import os
from typing import Dict, Optional, Any
from backend.models.xgboost_model import StuckPipeXGBoost
from backend.models.lightgbm_model import StuckPipeLightGBM
from backend.training.preprocessing import DrillingDataPreprocessor, NUMERIC_FEATURES
from backend.api.schemas import RiskLevel


class PredictionService:
    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = model_dir
        self.xgb_model: Optional[StuckPipeXGBoost] = None
        self.lgbm_model: Optional[StuckPipeLightGBM] = None
        self.preprocessor: Optional[DrillingDataPreprocessor] = None
        self.models_loaded = {"xgboost": False, "lightgbm": False, "lstm": False}
        self._load_models()

    def _load_models(self):
        try:
            xgb_path = os.path.join(self.model_dir, "xgboost_stuck_pipe.joblib")
            if os.path.exists(xgb_path):
                self.xgb_model = StuckPipeXGBoost()
                self.xgb_model.load(xgb_path)
                self.models_loaded["xgboost"] = True
        except Exception:
            pass

        try:
            lgbm_path = os.path.join(self.model_dir, "lightgbm_stuck_pipe.joblib")
            if os.path.exists(lgbm_path):
                self.lgbm_model = StuckPipeLightGBM()
                self.lgbm_model.load(lgbm_path)
                self.models_loaded["lightgbm"] = True
        except Exception:
            pass

        try:
            prep_path = os.path.join(self.model_dir, "preprocessor")
            if os.path.exists(prep_path):
                self.preprocessor = DrillingDataPreprocessor()
                self.preprocessor.load(prep_path)
        except Exception:
            pass

    def predict(self, parameters: Dict[str, float], model_name: str = "xgboost") -> Dict[str, Any]:
        if not any(self.models_loaded.values()):
            return self._simulation_prediction(parameters)

        try:
            feature_values = self._prepare_features(parameters)

            if model_name == "xgboost" and self.xgb_model:
                probability = float(self.xgb_model.predict_proba(feature_values.reshape(1, -1))[0])
            elif model_name == "lightgbm" and self.lgbm_model:
                probability = float(self.lgbm_model.predict_proba(feature_values.reshape(1, -1))[0])
            else:
                return self._simulation_prediction(parameters)

            return self._build_prediction_result(parameters, probability, model_name)

        except Exception:
            return self._simulation_prediction(parameters)

    def _prepare_features(self, parameters: Dict[str, float]) -> np.ndarray:
        if self.preprocessor and self.preprocessor.feature_names:
            feature_values = []
            for feat in self.preprocessor.feature_names:
                feature_values.append(parameters.get(feat, 0.0))
            return np.array(feature_values)

        return np.array([parameters.get(f, 0.0) for f in NUMERIC_FEATURES])

    def _simulation_prediction(self, parameters: Dict[str, float]) -> Dict[str, Any]:
        diff_p = parameters.get("differential_pressure", 0)
        hci = parameters.get("hole_cleaning_index", 0.8)
        vibration = parameters.get("vibration_level", 2)
        torque_fluct = parameters.get("torque_fluctuation", 0)
        cuttings = parameters.get("cuttings_volume", 5)

        risk_score = (
            min(1.0, diff_p / 6000) * 0.25 +
            (1 - hci) * 0.25 +
            min(1.0, vibration / 12) * 0.2 +
            min(1.0, torque_fluct) * 0.15 +
            min(1.0, cuttings / 25) * 0.15
        )
        probability = np.clip(risk_score + np.random.normal(0, 0.05), 0.01, 0.95)

        return self._build_prediction_result(parameters, probability, "simulation")

    def _build_prediction_result(self, parameters: Dict[str, float], probability: float, model_name: str) -> Dict[str, Any]:
        risk_level = self._get_risk_level(probability)

        diff_stick = min(0.95, parameters.get("differential_pressure", 0) / 6000 + np.random.normal(0, 0.05))
        mech_stick = min(0.95, (1 - parameters.get("hole_cleaning_index", 0.8)) + parameters.get("cuttings_volume", 5) / 40)
        instability = min(0.95, parameters.get("wellbore_instability_score", 0.3))

        return {
            "stuck_pipe_probability": probability,
            "risk_level": risk_level,
            "differential_sticking_risk": max(0, diff_stick),
            "mechanical_sticking_risk": max(0, mech_stick),
            "drilling_instability_score": max(0, instability),
            "confidence": 0.85 if model_name != "simulation" else 0.65,
            "model_used": model_name,
        }

    def _get_risk_level(self, probability: float) -> RiskLevel:
        if probability >= 0.8:
            return RiskLevel.CRITICAL
        elif probability >= 0.6:
            return RiskLevel.HIGH_RISK
        elif probability >= 0.4:
            return RiskLevel.WARNING
        elif probability >= 0.2:
            return RiskLevel.LOW_RISK
        return RiskLevel.NORMAL
