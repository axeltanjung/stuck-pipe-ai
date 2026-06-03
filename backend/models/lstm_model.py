import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
from typing import Dict, Tuple
import os


class DrillingSequenceDataset(Dataset):
    def __init__(self, sequences: np.ndarray, labels: np.ndarray):
        self.sequences = torch.FloatTensor(sequences)
        self.labels = torch.FloatTensor(labels)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


class TemporalAttention(nn.Module):
    def __init__(self, hidden_size: int):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.Tanh(),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, lstm_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        attention_weights = torch.softmax(self.attention(lstm_output), dim=1)
        context = torch.sum(attention_weights * lstm_output, dim=1)
        return context, attention_weights


class DrillingLSTM(nn.Module):
    def __init__(
        self, input_size: int, hidden_size: int = 128,
        num_layers: int = 3, dropout: float = 0.3
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.batch_norm = nn.BatchNorm1d(input_size)

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )

        self.attention = TemporalAttention(hidden_size * 2)

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, features = x.shape
        x = x.permute(0, 2, 1)
        x = self.batch_norm(x)
        x = x.permute(0, 2, 1)

        lstm_out, _ = self.lstm(x)
        context, _ = self.attention(lstm_out)
        output = self.classifier(context)
        return output.squeeze(-1)


class StuckPipeLSTMModel:
    def __init__(
        self, input_size: int, hidden_size: int = 128,
        num_layers: int = 3, learning_rate: float = 0.001,
        sequence_length: int = 50, device: str = None
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.sequence_length = sequence_length
        self.input_size = input_size

        self.model = DrillingLSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
        ).to(self.device)

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=learning_rate, weight_decay=1e-4
        )
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="min", patience=5, factor=0.5
        )
        self.criterion = nn.BCELoss()
        self.threshold = 0.5

    def train_epoch(self, dataloader: DataLoader) -> float:
        self.model.train()
        total_loss = 0
        for sequences, labels in dataloader:
            sequences = sequences.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(sequences)
            loss = self.criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            total_loss += loss.item()

        return total_loss / len(dataloader)

    def validate(self, dataloader: DataLoader) -> Tuple[float, Dict[str, float]]:
        self.model.eval()
        total_loss = 0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for sequences, labels in dataloader:
                sequences = sequences.to(self.device)
                labels = labels.to(self.device)

                outputs = self.model(sequences)
                loss = self.criterion(outputs, labels)
                total_loss += loss.item()

                all_preds.extend(outputs.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        binary_preds = (all_preds >= self.threshold).astype(int)

        metrics = {
            "val_loss": total_loss / len(dataloader),
            "roc_auc": roc_auc_score(all_labels, all_preds) if len(np.unique(all_labels)) > 1 else 0,
            "f1_score": f1_score(all_labels, binary_preds),
            "precision": precision_score(all_labels, binary_preds, zero_division=0),
            "recall": recall_score(all_labels, binary_preds, zero_division=0),
        }

        return total_loss / len(dataloader), metrics

    def train_model(
        self, X_train: np.ndarray, y_train: np.ndarray,
        X_val: np.ndarray, y_val: np.ndarray,
        epochs: int = 50, batch_size: int = 256
    ) -> Dict[str, list]:
        train_dataset = DrillingSequenceDataset(X_train, y_train)
        val_dataset = DrillingSequenceDataset(X_val, y_val)

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

        history = {"train_loss": [], "val_loss": [], "roc_auc": [], "f1_score": []}
        best_auc = 0
        patience_counter = 0
        patience = 10

        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss, metrics = self.validate(val_loader)
            self.scheduler.step(val_loss)

            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)
            history["roc_auc"].append(metrics["roc_auc"])
            history["f1_score"].append(metrics["f1_score"])

            if metrics["roc_auc"] > best_auc:
                best_auc = metrics["roc_auc"]
                patience_counter = 0
                self._save_best_weights()
            else:
                patience_counter += 1

            if (epoch + 1) % 5 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Loss: {train_loss:.4f} - Val AUC: {metrics['roc_auc']:.4f}")

            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                self._load_best_weights()
                break

        return history

    def predict(self, X: np.ndarray, batch_size: int = 256) -> np.ndarray:
        self.model.eval()
        dataset = DrillingSequenceDataset(X, np.zeros(len(X)))
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        predictions = []
        with torch.no_grad():
            for sequences, _ in dataloader:
                sequences = sequences.to(self.device)
                outputs = self.model(sequences)
                predictions.extend(outputs.cpu().numpy())

        return np.array(predictions)

    def _save_best_weights(self):
        self._best_weights = self.model.state_dict().copy()

    def _load_best_weights(self):
        if hasattr(self, "_best_weights"):
            self.model.load_state_dict(self._best_weights)

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "threshold": self.threshold,
            "input_size": self.input_size,
            "sequence_length": self.sequence_length,
        }, path)

    def load(self, path: str):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.threshold = checkpoint["threshold"]
