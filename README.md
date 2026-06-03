# 🛢️ StuckPipe AI — Drilling Risk Intelligence Platform

**AI-Powered Stuck Pipe Prediction & Drilling Optimization System**

An enterprise-grade machine learning platform that predicts stuck pipe incidents, monitors drilling risk in near-real-time, and provides AI-driven operational recommendations to prevent costly drilling failures.

---

## 📋 Table of Contents

- [Project Background](#project-background)
- [Business Benefits](#business-benefits)
- [Domain Knowledge](#domain-knowledge)
- [System Architecture](#system-architecture)
- [AI/ML Architecture](#aiml-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Future Improvements](#future-improvements)

---

## Project Background

### What is Stuck Pipe?

Stuck pipe is one of the most expensive and disruptive problems in oil and gas drilling operations. It occurs when the drillstring becomes immobilized in the wellbore and cannot be rotated or moved axially. This can happen due to:

- **Differential sticking** — when the drillstring is held against the wellbore wall by differential pressure between the mud column and formation pressure
- **Mechanical sticking** — caused by wellbore geometry issues, cuttings accumulation, key seating, or formation collapse
- **Pack-off** — when cuttings or cavings accumulate around the BHA

### Why is it Expensive?

A single stuck pipe incident can cost:
- **$100K – $5M+** depending on severity and location
- **Days to weeks** of non-productive time (NPT)
- Potential loss of the bottom hole assembly ($500K+)
- Sidetracking costs ($2M – $10M)
- Fishing operations ($200K – $1M)

Industry estimates indicate stuck pipe accounts for **25-30% of all drilling NPT**, representing billions of dollars annually across the global drilling industry.

### Limitations of Traditional Monitoring

- Reactive rather than proactive
- Relies on driller experience and intuition
- No systematic integration of multiple parameter trends
- Difficult to detect gradual degradation patterns
- Shift changes lead to knowledge gaps

---

## Business Benefits

| Benefit | Impact |
|---------|--------|
| Reduced NPT | 30-50% reduction in stuck pipe incidents |
| Lower drilling costs | $200K-$2M saved per prevented event |
| Improved efficiency | 15-25% faster drilling through optimized parameters |
| Reduced fishing operations | Prevent BHA loss and associated costs |
| Improved safety | Early warning reduces high-pressure operational decisions |
| Proactive risk mitigation | Hours of advance warning before incidents |

---

## Domain Knowledge

### Drilling Process

The rotary drilling process involves rotating a drill bit at the bottom of a string of drill pipe to create a wellbore. Key aspects:

- **Weight on Bit (WOB)** — Axial force applied to the bit for rock destruction
- **Rotary Speed (RPM)** — Rotation rate of the drillstring
- **Torque** — Rotational force required to turn the drillstring
- **Rate of Penetration (ROP)** — Speed of drilling progress

### Differential Sticking

Occurs when:
- High overbalance pressure pushes pipe against a permeable formation
- Creates a "suction cup" effect holding the pipe stationary
- Risk increases with: high mud weight, long static time, thick filter cake

### Mechanical Sticking

Caused by:
- **Cuttings accumulation** — inadequate hole cleaning leads to pack-off
- **Key seating** — pipe wears a groove in the formation at doglegs
- **Wellbore collapse** — unstable formations cave into the wellbore
- **Undergauge hole** — bit wear creates a smaller hole than the stabilizers

### Hole Cleaning

Critical factors for preventing mechanical sticking:
- Annular velocity (flow rate vs. annular area)
- Mud rheology (viscosity and yield point)
- Pipe rotation and eccentricity
- Wellbore inclination
- Cuttings bed formation in deviated wells

### Drilling Vibrations

- **Stick-slip** — torsional oscillation causing intermittent sticking and release
- **Lateral vibration** — bit whirl causing BHA damage
- **Axial vibration** — bit bounce reducing efficiency

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NGINX Reverse Proxy                       │
├─────────────────┬───────────────────────┬───────────────────────┤
│                 │                       │                       │
│  ┌──────────┐   │  ┌────────────────┐   │  ┌────────────────┐  │
│  │ Frontend │   │  │ FastAPI Backend │   │  │ MLflow Server  │  │
│  │ React +  │   │  │                │   │  │                │  │
│  │ Vite     │   │  │ /predict       │   │  │ Experiments    │  │
│  │          │   │  │ /alerts        │   │  │ Model Registry │  │
│  │ Dashboard│   │  │ /dashboard     │   │  │ Artifacts      │  │
│  └──────────┘   │  │ /recommend     │   │  └────────────────┘  │
│                 │  │ /explain       │   │                       │
│                 │  └───────┬────────┘   │                       │
│                 │          │            │                       │
│                 │  ┌───────▼────────┐   │                       │
│                 │  │  ML Models     │   │                       │
│                 │  │  ┌──────────┐  │   │                       │
│                 │  │  │ XGBoost  │  │   │                       │
│                 │  │  │ LightGBM │  │   │                       │
│                 │  │  │ LSTM     │  │   │                       │
│                 │  │  └──────────┘  │   │                       │
│                 │  └───────┬────────┘   │                       │
│                 │          │            │                       │
│                 │  ┌───────▼────────┐   │                       │
│                 │  │ SQLite DB      │   │                       │
│                 │  └────────────────┘   │                       │
└─────────────────┴───────────────────────┴───────────────────────┘
```

---

## AI/ML Architecture

### Models

| Model | Purpose | Architecture |
|-------|---------|-------------|
| XGBoost | Primary stuck pipe classifier | Gradient-boosted trees, 500 estimators |
| LightGBM | High-performance benchmark | Leaf-wise growth, probability calibration |
| LSTM | Sequential pattern detection | Bi-directional LSTM with temporal attention |

### ML Pipeline

1. **Data Preprocessing** — Missing value imputation, outlier handling
2. **Feature Engineering** — Rolling statistics, rate-of-change, derived indicators
3. **Sequence Generation** — Time-window preparation for LSTM
4. **Model Training** — With class imbalance handling and threshold optimization
5. **Hyperparameter Tuning** — Grid search with cross-validation
6. **Model Evaluation** — ROC AUC, F1, Precision, Recall
7. **Explainability** — SHAP values for prediction interpretation
8. **MLflow Tracking** — Experiment management and model registry

### Alert Engine Logic

```
Probability > 80% → CRITICAL
Probability > 60% → HIGH RISK
Probability > 40% → WARNING
Probability > 20% → LOW RISK
Probability ≤ 20% → NORMAL
```

Additional triggers: torque spikes, pressure instability, vibration anomalies, poor hole cleaning.

---

## Features

- **Real-time Risk Prediction** — Batch inference simulating near-real-time analysis
- **Multi-Model Ensemble** — XGBoost, LightGBM, and LSTM working together
- **Explainable AI** — SHAP-based feature contribution analysis
- **Intelligent Alerts** — Context-aware severity levels with actionable recommendations
- **Drilling Optimization** — AI-driven parameter adjustment suggestions
- **Executive Dashboard** — Fleet-wide risk overview with KPIs
- **Well Detail Views** — Deep-dive into individual well performance
- **Export Capabilities** — CSV and report downloads

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| ML | XGBoost, LightGBM, PyTorch (LSTM), scikit-learn, SHAP |
| Tracking | MLflow |
| Frontend | React 18, Vite, TailwindCSS, Recharts, Framer Motion |
| Database | SQLite |
| Deployment | Docker, docker-compose, Nginx |

---

## Getting Started

### Prerequisites

- Docker & docker-compose
- (Optional) Python 3.11+, Node.js 20+

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-username/stuck-pipe-ai.git
cd stuck-pipe-ai

# Copy environment variables
cp .env.example .env

# Build and start all services
docker-compose up --build

# Access the application:
# Dashboard: http://localhost:3000
# API Docs:  http://localhost:8000/docs
# MLflow:    http://localhost:5000
```

### Local Development (Without Docker)

#### Backend
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python -m backend.data_generator.synthetic_stuck_pipe_generator

# Train models
python -m backend.training.train_pipeline

# Start API server
uvicorn backend.api.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### MLflow
```bash
mlflow server --backend-store-uri sqlite:///mlflow/db/mlflow.db \
              --default-artifact-root ./mlflow/artifacts \
              --host 0.0.0.0 --port 5000
```

---

## Deployment

### Docker Architecture

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | React dashboard (Nginx) |
| backend | 8000 | FastAPI prediction service |
| mlflow | 5000 | Experiment tracking server |
| nginx | 80 | Reverse proxy (all-in-one access) |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite connection string | `sqlite:///./data/stuckpipe.db` |
| `MLFLOW_TRACKING_URI` | MLflow server URL | `http://localhost:5000` |
| `MODEL_PATH` | Trained model directory | `./data/models` |
| `DEFAULT_MODEL` | Default prediction model | `xgboost` |
| `PREDICTION_THRESHOLD` | Classification threshold | `0.5` |

---

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/predict/stuck-pipe` | Single prediction |
| POST | `/predict/risk` | Batch prediction |
| GET | `/alerts` | Active alerts |
| GET | `/dashboard/summary` | Executive overview data |
| GET | `/well/{well_id}` | Well detail information |
| GET | `/recommendation` | AI recommendations |
| GET | `/explain-risk` | SHAP explanation |

### Example Request

```bash
curl -X POST http://localhost:8000/predict/stuck-pipe \
  -H "Content-Type: application/json" \
  -d '{
    "well_id": "WELL-001",
    "depth": 12000,
    "hole_depth": 12050,
    "wob": 32.5,
    "rpm": 120,
    "torque": 18000,
    "hook_load": 280,
    "standpipe_pressure": 3200,
    "mud_flow_rate": 650,
    "mud_density": 11.5,
    "ecd": 12.1,
    "flow_out": 620,
    "cuttings_volume": 15,
    "mud_viscosity": 55,
    "vibration_level": 6.5,
    "stick_slip_index": 0.45,
    "rop": 45,
    "bit_wear": 0.3,
    "hole_cleaning_index": 0.55,
    "connection_time": 8,
    "reaming_frequency": 2,
    "tripping_speed": 1500,
    "pump_pressure": 2800,
    "temperature": 180,
    "differential_pressure": 2500
  }'
```

### Example Response

```json
{
  "well_id": "WELL-001",
  "stuck_pipe_probability": 0.72,
  "risk_level": "high_risk",
  "differential_sticking_risk": 0.45,
  "mechanical_sticking_risk": 0.58,
  "drilling_instability_score": 0.52,
  "confidence": 0.85,
  "model_used": "xgboost",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

---

## Future Improvements

- **Real-time Telemetry Integration** — WITSML/WITS data stream ingestion
- **Reinforcement Learning** — Autonomous drilling parameter optimization
- **Digital Twin Integration** — Physics-based wellbore simulation coupling
- **Edge Deployment** — On-rig model inference for low-latency predictions
- **Autonomous Drilling Assistant** — Closed-loop control system integration
- **Multi-well Correlation** — Offset well learning for new well predictions
- **Formation Ahead Prediction** — Seismic-to-drilling parameter mapping
- **NLP Reporting** — Automated daily drilling report generation
- **Transfer Learning** — Pre-trained models adaptable to new basins/formations

---

## Project Structure

```
stuck-pipe-ai/
├── backend/
│   ├── api/                  # FastAPI application
│   │   ├── main.py          # Main app with all endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── models/              # ML model implementations
│   │   ├── xgboost_model.py
│   │   ├── lightgbm_model.py
│   │   └── lstm_model.py
│   ├── training/            # Training pipeline
│   │   ├── preprocessing.py # Feature engineering
│   │   └── train_pipeline.py # Full MLflow training
│   ├── alerts/              # Alert engine
│   │   └── alert_engine.py
│   ├── services/            # Business logic
│   │   ├── prediction_service.py
│   │   └── recommendation_engine.py
│   ├── explainability/      # SHAP explanations
│   ├── data_generator/      # Synthetic data creation
│   │   └── synthetic_stuck_pipe_generator.py
│   └── utils/               # Config, logging
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # 5 dashboard pages
│   │   └── services/        # API client
│   ├── package.json
│   └── tailwind.config.js
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   ├── mlflow.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

**Built for the drilling industry. Powered by AI.**
