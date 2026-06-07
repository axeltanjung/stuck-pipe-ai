import time
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import uuid

from backend.api.schemas import (
    DrillingDataInput, PredictionResponse, AlertResponse,
    DashboardSummary, WellDetail, RecommendationResponse,
    ExplanationResponse, HealthResponse, RiskLevel, AlertSeverity
)
from backend.services.prediction_service import PredictionService
from backend.services.recommendation_engine import DrillingRecommendationEngine
from backend.alerts.alert_engine import AlertEngine
from backend.utils.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Stuck Pipe AI - Drilling Risk Intelligence",
    description="AI-powered drilling risk monitoring and stuck pipe prediction platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

prediction_service = PredictionService(model_dir=settings.model_path)
recommendation_engine = DrillingRecommendationEngine()
alert_engine = AlertEngine()


def _generate_simulated_wells() -> List[Dict[str, Any]]:
    rng = np.random.default_rng(int(time.time()) % 1000)
    wells = []
    for i in range(8):
        risk = rng.uniform(0.05, 0.85)
        wells.append({
            "well_id": f"WELL-{i+1:03d}",
            "depth": rng.uniform(5000, 20000),
            "risk": risk,
            "risk_level": _risk_level_from_prob(risk).value,
            "formation": rng.choice(["sandstone", "shale", "limestone", "dolomite"]),
            "phase": rng.choice(["surface", "intermediate", "production", "horizontal"]),
            "region": rng.choice(["Gulf of Mexico", "North Sea", "Permian Basin"]),
        })
    return wells


def _risk_level_from_prob(prob: float) -> RiskLevel:
    if prob >= 0.8:
        return RiskLevel.CRITICAL
    elif prob >= 0.6:
        return RiskLevel.HIGH_RISK
    elif prob >= 0.4:
        return RiskLevel.WARNING
    elif prob >= 0.2:
        return RiskLevel.LOW_RISK
    return RiskLevel.NORMAL


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded=prediction_service.models_loaded,
        uptime_seconds=time.time() - START_TIME,
    )


@app.post("/predict/stuck-pipe", response_model=PredictionResponse)
async def predict_stuck_pipe(data: DrillingDataInput):
    parameters = data.model_dump(exclude={"well_id", "formation_type", "drilling_phase"})
    result = prediction_service.predict(parameters, model_name=settings.default_model)

    alerts = alert_engine.evaluate(data.well_id, parameters, result["stuck_pipe_probability"])

    return PredictionResponse(
        well_id=data.well_id,
        stuck_pipe_probability=result["stuck_pipe_probability"],
        risk_level=result["risk_level"],
        differential_sticking_risk=result["differential_sticking_risk"],
        mechanical_sticking_risk=result["mechanical_sticking_risk"],
        drilling_instability_score=result["drilling_instability_score"],
        confidence=result["confidence"],
        model_used=result["model_used"],
        timestamp=datetime.now(),
    )


@app.post("/predict/risk")
async def predict_risk_batch(data: List[DrillingDataInput]):
    results = []
    for item in data:
        parameters = item.model_dump(exclude={"well_id", "formation_type", "drilling_phase"})
        result = prediction_service.predict(parameters)
        result["well_id"] = item.well_id
        result["timestamp"] = datetime.now().isoformat()
        results.append(result)
    return results


@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(well_id: str = Query(None)):
    alerts = alert_engine.get_active_alerts(well_id)

    if not alerts:
        rng = np.random.default_rng(42)
        sample_alerts = []
        for i in range(5):
            risk = rng.uniform(0.3, 0.9)
            sample_alerts.append(AlertResponse(
                alert_id=str(uuid.uuid4())[:8],
                well_id=f"WELL-{rng.integers(1, 9):03d}",
                severity=AlertSeverity.HIGH if risk > 0.6 else AlertSeverity.MEDIUM,
                alert_type="stuck_pipe_warning",
                message=f"Elevated stuck pipe risk: {risk:.1%}",
                risk_probability=risk,
                triggered_at=datetime.now(),
                recommendations=["Increase circulation", "Monitor torque"],
                parameters={"torque": rng.uniform(8000, 20000), "vibration_level": rng.uniform(3, 10)},
            ))
        return sample_alerts

    return [
        AlertResponse(
            alert_id=a.alert_id,
            well_id=a.well_id,
            severity=a.severity,
            alert_type=a.alert_type,
            message=a.message,
            risk_probability=a.risk_probability,
            triggered_at=a.triggered_at,
            recommendations=a.recommendations,
            parameters=a.parameters,
        )
        for a in alerts
    ]


@app.get("/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary():
    wells = _generate_simulated_wells()
    risks = [w["risk"] for w in wells]

    risk_dist = {"normal": 0, "low_risk": 0, "warning": 0, "high_risk": 0, "critical": 0}
    for w in wells:
        risk_dist[w["risk_level"]] += 1

    alerts = alert_engine.get_active_alerts()
    recent_alerts = [
        AlertResponse(
            alert_id=a.alert_id, well_id=a.well_id, severity=a.severity,
            alert_type=a.alert_type, message=a.message, risk_probability=a.risk_probability,
            triggered_at=a.triggered_at, recommendations=a.recommendations, parameters=a.parameters,
        ) for a in alerts[:5]
    ]

    return DashboardSummary(
        total_wells=len(wells),
        active_wells=len(wells),
        high_risk_wells=sum(1 for r in risks if r >= 0.6),
        critical_alerts=risk_dist.get("critical", 0),
        average_risk=float(np.mean(risks)),
        drilling_instability_index=float(np.mean(risks) * 1.2),
        wells_summary=wells,
        risk_distribution=risk_dist,
        recent_alerts=recent_alerts,
    )


@app.get("/well/{well_id}", response_model=WellDetail)
async def get_well_detail(well_id: str):
    rng = np.random.default_rng(hash(well_id) % 2**31)
    current_risk = rng.uniform(0.1, 0.8)
    depth = rng.uniform(8000, 18000)

    risk_history = []
    for i in range(50):
        risk_val = max(0.05, current_risk + rng.normal(0, 0.1) - 0.002 * (50 - i))
        risk_history.append({
            "depth": depth - (50 - i) * 100,
            "risk": min(0.95, risk_val),
            "timestamp": datetime.now().isoformat(),
        })

    return WellDetail(
        well_id=well_id,
        current_depth=depth,
        total_depth=depth + rng.uniform(1000, 5000),
        current_risk=current_risk,
        risk_level=_risk_level_from_prob(current_risk),
        formation_type=rng.choice(["sandstone", "shale", "limestone"]),
        drilling_phase=rng.choice(["production", "intermediate", "horizontal"]),
        parameters={
            "wob": float(rng.uniform(10, 40)),
            "rpm": float(rng.uniform(60, 160)),
            "torque": float(rng.uniform(5000, 25000)),
            "rop": float(rng.uniform(20, 100)),
            "mud_density": float(rng.uniform(9, 14)),
            "ecd": float(rng.uniform(10, 15)),
            "vibration_level": float(rng.uniform(1, 8)),
            "hole_cleaning_index": float(rng.uniform(0.4, 0.9)),
        },
        risk_history=risk_history,
        active_alerts=[],
    )


@app.get("/recommendation", response_model=RecommendationResponse)
async def get_recommendations(well_id: str = "WELL-001"):
    rng = np.random.default_rng(hash(well_id) % 2**31)
    params = {
        "wob": float(rng.uniform(20, 45)),
        "torque": float(rng.uniform(10000, 30000)),
        "hole_cleaning_index": float(rng.uniform(0.3, 0.7)),
        "cuttings_volume": float(rng.uniform(8, 25)),
        "vibration_level": float(rng.uniform(3, 10)),
        "stick_slip_index": float(rng.uniform(0.2, 0.8)),
        "drag_force": float(rng.uniform(20, 80)),
        "differential_pressure": float(rng.uniform(1000, 5000)),
        "wellbore_instability_score": float(rng.uniform(0.3, 0.8)),
        "cuttings_accumulation_risk": float(rng.uniform(5, 20)),
        "connection_time": float(rng.uniform(3, 15)),
    }

    risk_prob = rng.uniform(0.4, 0.8)
    risk_level = _risk_level_from_prob(risk_prob)
    recommendations = recommendation_engine.generate_recommendations(params, risk_prob, risk_level)

    return RecommendationResponse(
        well_id=well_id,
        risk_level=risk_level,
        recommendations=recommendations,
        expected_risk_reduction=sum(r["expected_risk_reduction"] for r in recommendations[:3]) * 0.6,
        priority="high" if risk_prob > 0.6 else "medium",
    )


@app.get("/explain-risk", response_model=ExplanationResponse)
async def explain_risk(well_id: str = "WELL-001"):
    rng = np.random.default_rng(hash(well_id) % 2**31)
    probability = rng.uniform(0.3, 0.8)

    drivers = {
        "differential_pressure": float(rng.uniform(0.1, 0.4)),
        "torque_fluctuation": float(rng.uniform(0.05, 0.3)),
        "cuttings_volume": float(rng.uniform(0.05, 0.25)),
        "vibration_level": float(rng.uniform(0.03, 0.2)),
        "hole_cleaning_index": float(rng.uniform(0.02, 0.15)),
    }

    protective = {
        "mud_flow_rate": float(rng.uniform(-0.15, -0.05)),
        "rop": float(rng.uniform(-0.1, -0.03)),
        "rpm": float(rng.uniform(-0.08, -0.02)),
    }

    return ExplanationResponse(
        well_id=well_id,
        prediction=probability,
        risk_level=_risk_level_from_prob(probability),
        top_risk_drivers=drivers,
        top_protective_factors=protective,
        explanation_text="High differential pressure and torque fluctuation are primary risk drivers. Cuttings accumulation suggests inadequate hole cleaning.",
        confidence=0.82,
    )
