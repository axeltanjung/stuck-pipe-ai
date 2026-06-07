import os
import json
import mlflow
import mlflow.sklearn
import mlflow.pytorch
import pandas as pd
from datetime import datetime
from typing import Dict

from backend.training.preprocessing import DrillingDataPreprocessor
from backend.models.xgboost_model import StuckPipeXGBoost
from backend.models.lightgbm_model import StuckPipeLightGBM
from backend.models.lstm_model import StuckPipeLSTMModel


class StuckPipeTrainingPipeline:
    def __init__(self, data_path: str, output_dir: str = "data/models", mlflow_uri: str = "http://localhost:5000"):
        self.data_path = data_path
        self.output_dir = output_dir
        self.mlflow_uri = mlflow_uri

        os.makedirs(output_dir, exist_ok=True)
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment("stuck_pipe_prediction")

        self.preprocessor = DrillingDataPreprocessor()
        self.xgb_model = None
        self.lgbm_model = None
        self.lstm_model = None
        self.results: Dict[str, Dict] = {}

    def run_full_pipeline(self):
        print("=" * 60)
        print("STUCK PIPE PREDICTION - TRAINING PIPELINE")
        print("=" * 60)

        print("\n[1/7] Loading and preprocessing data...")
        df = self.preprocessor.load_data(self.data_path)
        print(f"  Loaded {len(df):,} rows, {df['well_id'].nunique()} wells")

        print("\n[2/7] Feature engineering and preparation...")
        X_train, X_test, y_train, y_test, feature_names = self.preprocessor.prepare_data(df)
        print(f"  Train: {X_train.shape}, Test: {X_test.shape}")
        print(f"  Features: {len(feature_names)}")
        print(f"  Positive rate: {y_train.mean():.4f}")

        print("\n[3/7] Training XGBoost model...")
        self._train_xgboost(X_train, y_train, X_test, y_test, feature_names)

        print("\n[4/7] Training LightGBM model...")
        self._train_lightgbm(X_train, y_train, X_test, y_test, feature_names)

        print("\n[5/7] Training LSTM model...")
        self._train_lstm(df, feature_names)

        print("\n[6/7] Saving preprocessor and models...")
        self.preprocessor.save(os.path.join(self.output_dir, "preprocessor"))
        self._save_results()

        print("\n[7/7] Pipeline complete!")
        self._print_summary()

    def _train_xgboost(self, X_train, y_train, X_test, y_test, feature_names):
        with mlflow.start_run(run_name=f"xgboost_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            self.xgb_model = StuckPipeXGBoost()
            metrics = self.xgb_model.train(X_train, y_train, X_test, y_test)
            self.xgb_model.optimize_threshold(X_test, y_test)
            metrics = self.xgb_model.evaluate(X_test, y_test)

            mlflow.log_params(self.xgb_model.params)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(self.xgb_model.model, "xgboost_model")

            importance = self.xgb_model.get_feature_importance(feature_names)
            mlflow.log_dict(importance, "feature_importance.json")

            self.xgb_model.save(os.path.join(self.output_dir, "xgboost_stuck_pipe.joblib"))
            self.results["xgboost"] = metrics
            print(f"  ROC AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f}")

    def _train_lightgbm(self, X_train, y_train, X_test, y_test, feature_names):
        with mlflow.start_run(run_name=f"lightgbm_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            self.lgbm_model = StuckPipeLightGBM()
            metrics = self.lgbm_model.train(X_train, y_train, X_test, y_test)
            self.lgbm_model.calibrate(X_test, y_test)
            self.lgbm_model.optimize_threshold(X_test, y_test)
            metrics = self.lgbm_model.evaluate(X_test, y_test)

            mlflow.log_params(self.lgbm_model.params)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(self.lgbm_model.model, "lightgbm_model")

            importance = self.lgbm_model.get_feature_importance(feature_names)
            mlflow.log_dict(importance, "feature_importance.json")

            self.lgbm_model.save(os.path.join(self.output_dir, "lightgbm_stuck_pipe.joblib"))
            self.results["lightgbm"] = metrics
            print(f"  ROC AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f}")

    def _train_lstm(self, df: pd.DataFrame, feature_names: list):
        with mlflow.start_run(run_name=f"lstm_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            sequence_length = 50
            X_seq, y_seq = self.preprocessor.prepare_sequences(df, sequence_length=sequence_length)

            split_idx = int(len(X_seq) * 0.8)
            X_train_seq = X_seq[:split_idx]
            y_train_seq = y_seq[:split_idx]
            X_val_seq = X_seq[split_idx:]
            y_val_seq = y_seq[split_idx:]

            input_size = X_train_seq.shape[2]
            self.lstm_model = StuckPipeLSTMModel(
                input_size=input_size,
                hidden_size=128,
                num_layers=3,
                sequence_length=sequence_length,
            )

            history = self.lstm_model.train_model(
                X_train_seq, y_train_seq,
                X_val_seq, y_val_seq,
                epochs=30,
                batch_size=256,
            )

            metrics = {
                "roc_auc": max(history["roc_auc"]) if history["roc_auc"] else 0,
                "f1_score": max(history["f1_score"]) if history["f1_score"] else 0,
                "final_train_loss": history["train_loss"][-1] if history["train_loss"] else 0,
                "final_val_loss": history["val_loss"][-1] if history["val_loss"] else 0,
            }

            mlflow.log_params({
                "input_size": input_size,
                "hidden_size": 128,
                "num_layers": 3,
                "sequence_length": sequence_length,
            })
            mlflow.log_metrics(metrics)

            model_path = os.path.join(self.output_dir, "lstm_stuck_pipe.pt")
            self.lstm_model.save(model_path)
            mlflow.log_artifact(model_path)

            self.results["lstm"] = metrics
            print(f"  ROC AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f}")

    def _save_results(self):
        results_path = os.path.join(self.output_dir, "training_results.json")
        with open(results_path, "w") as f:
            json.dump(self.results, f, indent=2)

    def _print_summary(self):
        print("\n" + "=" * 60)
        print("TRAINING RESULTS SUMMARY")
        print("=" * 60)
        for model_name, metrics in self.results.items():
            print(f"\n{model_name.upper()}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.4f}")


if __name__ == "__main__":
    pipeline = StuckPipeTrainingPipeline(
        data_path="data/raw/drilling_telemetry.csv",
        output_dir="data/models",
        mlflow_uri="http://localhost:5000",
    )
    pipeline.run_full_pipeline()
