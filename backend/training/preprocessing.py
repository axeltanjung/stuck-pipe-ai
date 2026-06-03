import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os


NUMERIC_FEATURES = [
    "depth", "hole_depth", "wob", "rpm", "torque", "hook_load",
    "standpipe_pressure", "mud_flow_rate", "mud_density", "ecd",
    "flow_out", "cuttings_volume", "mud_viscosity", "vibration_level",
    "stick_slip_index", "rop", "bit_wear", "hole_cleaning_index",
    "connection_time", "reaming_frequency", "tripping_speed",
    "pump_pressure", "temperature", "torque_fluctuation",
    "pressure_spike_score", "drag_force", "drag_trend",
    "cuttings_accumulation_risk", "wellbore_instability_score",
    "differential_pressure",
]

CATEGORICAL_FEATURES = ["formation_type", "drilling_phase", "region", "rig_type"]

TARGET_COLUMN = "stuck_pipe_risk"

SECONDARY_TARGETS = [
    "stuck_pipe_probability",
    "differential_sticking_risk",
    "mechanical_sticking_risk",
    "drilling_instability_score",
]


class DrillingDataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.is_fitted = False

    def load_data(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, parse_dates=["timestamp"])
        df = df.sort_values(["well_id", "timestamp"]).reset_index(drop=True)
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in NUMERIC_FEATURES:
            if col in df.columns:
                df[col] = df.groupby("well_id")[col].transform(
                    lambda x: x.fillna(method="ffill").fillna(method="bfill").fillna(x.median())
                )

        for col in CATEGORICAL_FEATURES:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mode()[0])

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in ["torque", "standpipe_pressure", "hook_load", "vibration_level"]:
            if col in df.columns:
                df[f"{col}_rolling_mean_10"] = df.groupby("well_id")[col].transform(
                    lambda x: x.rolling(window=10, min_periods=1).mean()
                )
                df[f"{col}_rolling_std_10"] = df.groupby("well_id")[col].transform(
                    lambda x: x.rolling(window=10, min_periods=1).std().fillna(0)
                )
                df[f"{col}_rolling_max_20"] = df.groupby("well_id")[col].transform(
                    lambda x: x.rolling(window=20, min_periods=1).max()
                )
                df[f"{col}_rate_of_change"] = df.groupby("well_id")[col].transform(
                    lambda x: x.diff().fillna(0)
                )

        if "torque" in df.columns and "rpm" in df.columns:
            df["torque_per_rpm"] = df["torque"] / (df["rpm"] + 1e-6)

        if "wob" in df.columns and "rop" in df.columns:
            df["mechanical_specific_energy"] = df["wob"] / (df["rop"] + 1e-6)

        if "mud_flow_rate" in df.columns and "flow_out" in df.columns:
            df["flow_differential"] = df["mud_flow_rate"] - df["flow_out"]

        if "ecd" in df.columns and "mud_density" in df.columns:
            df["ecd_margin"] = df["ecd"] - df["mud_density"]

        if "hook_load" in df.columns:
            df["hook_load_deviation"] = df.groupby("well_id")["hook_load"].transform(
                lambda x: (x - x.mean()) / (x.std() + 1e-6)
            )

        if "cuttings_volume" in df.columns:
            df["cuttings_trend"] = df.groupby("well_id")["cuttings_volume"].transform(
                lambda x: x.rolling(window=50, min_periods=1).mean()
            )

        return df

    def encode_categoricals(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        for col in CATEGORICAL_FEATURES:
            if col in df.columns:
                if fit:
                    le = LabelEncoder()
                    df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
                else:
                    le = self.label_encoders[col]
                    df[f"{col}_encoded"] = df[col].astype(str).map(
                        lambda x: le.transform([x])[0] if x in le.classes_ else -1
                    )
        return df

    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        engineered_cols = [c for c in df.columns if any(
            c.endswith(suffix) for suffix in
            ["_rolling_mean_10", "_rolling_std_10", "_rolling_max_20", "_rate_of_change"]
        )]
        derived_cols = [
            "torque_per_rpm", "mechanical_specific_energy", "flow_differential",
            "ecd_margin", "hook_load_deviation", "cuttings_trend"
        ]
        encoded_cols = [f"{col}_encoded" for col in CATEGORICAL_FEATURES if f"{col}_encoded" in df.columns]

        feature_cols = NUMERIC_FEATURES + engineered_cols
        feature_cols += [c for c in derived_cols if c in df.columns]
        feature_cols += encoded_cols

        feature_cols = [c for c in feature_cols if c in df.columns]
        return list(dict.fromkeys(feature_cols))

    def prepare_data(
        self, df: pd.DataFrame, fit: bool = True, test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        df = self.handle_missing_values(df)
        df = self.engineer_features(df)
        df = self.encode_categoricals(df, fit=fit)

        feature_cols = self.get_feature_columns(df)
        self.feature_names = feature_cols

        X = df[feature_cols].values
        y = df[TARGET_COLUMN].values

        if fit:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            self.scaler.fit(X_train)
            X_train = self.scaler.transform(X_train)
            X_test = self.scaler.transform(X_test)
            self.is_fitted = True
            return X_train, X_test, y_train, y_test, feature_cols
        else:
            X = self.scaler.transform(X)
            return X, None, None, None, feature_cols

    def prepare_sequences(
        self, df: pd.DataFrame, sequence_length: int = 50
    ) -> Tuple[np.ndarray, np.ndarray]:
        df = self.handle_missing_values(df)
        df = self.engineer_features(df)
        df = self.encode_categoricals(df, fit=False)

        feature_cols = self.feature_names if self.feature_names else self.get_feature_columns(df)

        sequences = []
        labels = []

        for well_id in df["well_id"].unique():
            well_data = df[df["well_id"] == well_id].sort_values("timestamp")
            X_well = well_data[feature_cols].values
            y_well = well_data[TARGET_COLUMN].values

            X_well = self.scaler.transform(X_well) if self.is_fitted else X_well

            for i in range(len(X_well) - sequence_length):
                sequences.append(X_well[i:i + sequence_length])
                labels.append(y_well[i + sequence_length])

        return np.array(sequences), np.array(labels)

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.scaler, os.path.join(path, "scaler.joblib"))
        joblib.dump(self.label_encoders, os.path.join(path, "label_encoders.joblib"))
        joblib.dump(self.feature_names, os.path.join(path, "feature_names.joblib"))

    def load(self, path: str):
        self.scaler = joblib.load(os.path.join(path, "scaler.joblib"))
        self.label_encoders = joblib.load(os.path.join(path, "label_encoders.joblib"))
        self.feature_names = joblib.load(os.path.join(path, "feature_names.joblib"))
        self.is_fitted = True
