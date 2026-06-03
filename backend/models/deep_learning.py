import torch
import torch.nn as nn
import numpy as np
from typing import Tuple


class DrillingLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 3,
                 dropout: float = 0.3, bidirectional: bool = True):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
            bidirectional=bidirectional,
        )

        lstm_output_size = hidden_size * 2 if bidirectional else hidden_size

        self.attention = nn.Sequential(
            nn.Linear(lstm_output_size, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )

        self.classifier = nn.Sequential(
            nn.Linear(lstm_output_size, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)

        attention_weights = self.attention(lstm_out)
        attention_weights = torch.softmax(attention_weights, dim=1)
        context = torch.sum(attention_weights * lstm_out, dim=1)

        output = self.classifier(context)
        return output.squeeze(-1)


class TemporalTransformer(nn.Module):
    def __init__(self, input_size: int, d_model: int = 128, nhead: int = 8,
                 num_layers: int = 4, dropout: float = 0.2, max_seq_len: int = 100):
        super().__init__()
        self.input_projection = nn.Linear(input_size, d_model)
        self.positional_encoding = nn.Parameter(torch.randn(1, max_seq_len, d_model) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.classifier = nn.Sequential(
            nn.Linear(d_model, 256),
            nn.GELU(),
            nn.LayerNorm(256),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.LayerNorm(128),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )

        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        x = self.input_projection(x)
        x = x + self.positional_encoding[:, :seq_len, :]

        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)

        x = self.transformer(x)
        cls_output = x[:, 0, :]

        output = self.classifier(cls_output)
        return output.squeeze(-1)


class DeepLearningTrainer:
    def __init__(self, model_type: str = "lstm", input_size: int = 31, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if model_type == "lstm":
            self.model = DrillingLSTM(input_size=input_size).to(self.device)
        else:
            self.model = TemporalTransformer(input_size=input_size).to(self.device)

        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=50)

    def train_epoch(self, X: np.ndarray, y: np.ndarray, batch_size: int = 256) -> float:
        self.model.train()
        total_loss = 0
        n_batches = 0

        indices = np.random.permutation(len(X))
        for i in range(0, len(X), batch_size):
            batch_idx = indices[i:i + batch_size]
            X_batch = torch.FloatTensor(X[batch_idx]).to(self.device)
            y_batch = torch.FloatTensor(y[batch_idx]).to(self.device)

            self.optimizer.zero_grad()
            predictions = self.model(X_batch)
            loss = self.criterion(predictions, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        self.scheduler.step()
        return total_loss / max(n_batches, 1)

    def evaluate(self, X: np.ndarray, y: np.ndarray, batch_size: int = 512) -> Tuple[float, np.ndarray]:
        self.model.eval()
        predictions = []
        total_loss = 0
        n_batches = 0

        with torch.no_grad():
            for i in range(0, len(X), batch_size):
                X_batch = torch.FloatTensor(X[i:i + batch_size]).to(self.device)
                y_batch = torch.FloatTensor(y[i:i + batch_size]).to(self.device)

                preds = self.model(X_batch)
                loss = self.criterion(preds, y_batch)
                total_loss += loss.item()
                n_batches += 1
                predictions.extend(preds.cpu().numpy())

        avg_loss = total_loss / max(n_batches, 1)
        return avg_loss, np.array(predictions)

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray, epochs: int = 50) -> dict:
        best_val_loss = float("inf")
        best_state = None
        history = {"train_loss": [], "val_loss": []}

        for epoch in range(epochs):
            train_loss = self.train_epoch(X_train, y_train)
            val_loss, _ = self.evaluate(X_val, y_val)

            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        if best_state:
            self.model.load_state_dict(best_state)

        return history

    def save(self, path: str):
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()

    def predict(self, X: np.ndarray, batch_size: int = 512) -> np.ndarray:
        self.model.eval()
        predictions = []
        with torch.no_grad():
            for i in range(0, len(X), batch_size):
                X_batch = torch.FloatTensor(X[i:i + batch_size]).to(self.device)
                preds = self.model(X_batch)
                predictions.extend(preds.cpu().numpy())
        return np.array(predictions)
