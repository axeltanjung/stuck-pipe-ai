from pydantic import BaseModel, Field
from typing import List, Dict, Any
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    NORMAL = "normal"
    LOW_RISK = "low_risk"
    WARNING = "warning"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DrillingDataInput(BaseModel):
    well_id: str
    depth: float = Field(ge=0, le=30000)
    hole_depth: float = Field(ge=0, le=30000)
    wob: float = Field(ge=0, le=100, description="Weight on Bit (klbs)")
    rpm: float = Field(ge=0, le=300)
    torque: float = Field(ge=0, le=80000)
    hook_load: float = Field(ge=0, le=1000)
    standpipe_pressure: float = Field(ge=0, le=8000)
    mud_flow_rate: float = Field(ge=0, le=1500)
    mud_density: float = Field(ge=6, le=20, description="ppg")
    ecd: float = Field(ge=6, le=22)
    flow_out: float = Field(ge=0, le=1500)
    cuttings_volume: float = Field(ge=0, le=50)
    mud_viscosity: float = Field(ge=10, le=150)
    vibration_level: float = Field(ge=0, le=20)
    stick_slip_index: float = Field(ge=0, le=1)
    rop: float = Field(ge=0, le=300)
    bit_wear: float = Field(ge=0, le=1)
    hole_cleaning_index: float = Field(ge=0, le=1)
    connection_time: float = Field(ge=0)
    reaming_frequency: float = Field(ge=0)
    tripping_speed: float = Field(ge=0)
    pump_pressure: float = Field(ge=0, le=6000)
    temperature: float = Field(ge=50, le=500)
    differential_pressure: float = Field(ge=0, le=10000)
    formation_type: str = "sandstone"
    drilling_phase: str = "production"


class PredictionResponse(BaseModel):
    well_id: str
    stuck_pipe_probability: float
    risk_level: RiskLevel
    differential_sticking_risk: float
    mechanical_sticking_risk: float
    drilling_instability_score: float
    confidence: float
    model_used: str
    timestamp: datetime


class AlertResponse(BaseModel):
    alert_id: str
    well_id: str
    severity: AlertSeverity
    alert_type: str
    message: str
    risk_probability: float
    triggered_at: datetime
    recommendations: List[str]
    parameters: Dict[str, float]


class DashboardSummary(BaseModel):
    total_wells: int
    active_wells: int
    high_risk_wells: int
    critical_alerts: int
    average_risk: float
    drilling_instability_index: float
    wells_summary: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    recent_alerts: List[AlertResponse]


class WellDetail(BaseModel):
    well_id: str
    current_depth: float
    total_depth: float
    current_risk: float
    risk_level: RiskLevel
    formation_type: str
    drilling_phase: str
    parameters: Dict[str, float]
    risk_history: List[Dict[str, Any]]
    active_alerts: List[AlertResponse]


class RecommendationResponse(BaseModel):
    well_id: str
    risk_level: RiskLevel
    recommendations: List[Dict[str, Any]]
    expected_risk_reduction: float
    priority: str


class ExplanationResponse(BaseModel):
    well_id: str
    prediction: float
    risk_level: RiskLevel
    top_risk_drivers: Dict[str, float]
    top_protective_factors: Dict[str, float]
    explanation_text: str
    confidence: float


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]
    uptime_seconds: float
