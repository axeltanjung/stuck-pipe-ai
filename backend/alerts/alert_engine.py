from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import uuid

from backend.api.schemas import AlertSeverity


@dataclass
class DrillingAlert:
    alert_id: str
    well_id: str
    severity: AlertSeverity
    alert_type: str
    message: str
    risk_probability: float
    triggered_at: datetime
    recommendations: List[str]
    parameters: Dict[str, float]
    acknowledged: bool = False


class AlertEngine:
    def __init__(self):
        self.active_alerts: List[DrillingAlert] = []
        self.alert_history: List[DrillingAlert] = []
        self.thresholds = {
            "stuck_probability_critical": 0.8,
            "stuck_probability_high": 0.6,
            "stuck_probability_warning": 0.4,
            "stuck_probability_low": 0.2,
            "torque_spike_threshold": 1.5,
            "pressure_spike_threshold": 500,
            "vibration_critical": 10,
            "vibration_warning": 7,
            "drag_increase_threshold": 1.3,
            "hole_cleaning_poor": 0.4,
        }

    def evaluate(self, well_id: str, parameters: Dict[str, float], prediction: float) -> List[DrillingAlert]:
        new_alerts = []

        risk_alert = self._check_stuck_probability(well_id, prediction, parameters)
        if risk_alert:
            new_alerts.append(risk_alert)

        torque_alert = self._check_torque_anomaly(well_id, parameters)
        if torque_alert:
            new_alerts.append(torque_alert)

        pressure_alert = self._check_pressure_instability(well_id, parameters)
        if pressure_alert:
            new_alerts.append(pressure_alert)

        vibration_alert = self._check_vibration(well_id, parameters)
        if vibration_alert:
            new_alerts.append(vibration_alert)

        cleaning_alert = self._check_hole_cleaning(well_id, parameters)
        if cleaning_alert:
            new_alerts.append(cleaning_alert)

        for alert in new_alerts:
            self.active_alerts.append(alert)
            self.alert_history.append(alert)

        return new_alerts

    def _check_stuck_probability(self, well_id: str, probability: float, params: Dict) -> Optional[DrillingAlert]:
        if probability >= self.thresholds["stuck_probability_critical"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.CRITICAL,
                alert_type="stuck_pipe_critical",
                message=f"CRITICAL: Stuck pipe probability at {probability:.1%}. Immediate action required.",
                risk_probability=probability,
                triggered_at=datetime.now(),
                recommendations=[
                    "IMMEDIATELY increase circulation rate",
                    "Reduce WOB to minimum safe level",
                    "Begin pipe rotation/reciprocation",
                    "Prepare spotting fluid for potential freeing attempt",
                    "Alert rig supervisor and drilling superintendent",
                ],
                parameters=params,
            )
        elif probability >= self.thresholds["stuck_probability_high"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.HIGH,
                alert_type="stuck_pipe_high_risk",
                message=f"HIGH RISK: Stuck pipe probability at {probability:.1%}. Preventive action needed.",
                risk_probability=probability,
                triggered_at=datetime.now(),
                recommendations=[
                    "Increase circulation rate by 15-20%",
                    "Reduce connection time",
                    "Perform short wiper trips",
                    "Monitor torque and drag trends closely",
                    "Review mud properties and adjust if needed",
                ],
                parameters=params,
            )
        elif probability >= self.thresholds["stuck_probability_warning"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.MEDIUM,
                alert_type="stuck_pipe_warning",
                message=f"WARNING: Stuck pipe probability elevated at {probability:.1%}.",
                risk_probability=probability,
                triggered_at=datetime.now(),
                recommendations=[
                    "Monitor drilling parameters closely",
                    "Ensure adequate hole cleaning practices",
                    "Consider increasing flow rate",
                    "Review upcoming formation transitions",
                ],
                parameters=params,
            )
        return None

    def _check_torque_anomaly(self, well_id: str, params: Dict) -> Optional[DrillingAlert]:
        torque = params.get("torque", 0)
        torque_fluctuation = params.get("torque_fluctuation", 0)

        if torque_fluctuation > self.thresholds["torque_spike_threshold"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.HIGH,
                alert_type="torque_anomaly",
                message=f"Torque fluctuation detected: {torque_fluctuation:.2f}x above baseline. Current torque: {torque:.0f} ft-lbs.",
                risk_probability=min(0.8, torque_fluctuation / 3),
                triggered_at=datetime.now(),
                recommendations=[
                    "Reduce RPM to minimize stick-slip",
                    "Consider reducing WOB",
                    "Monitor for progressive torque increase",
                    "Perform backreaming if safe",
                ],
                parameters=params,
            )
        return None

    def _check_pressure_instability(self, well_id: str, params: Dict) -> Optional[DrillingAlert]:
        pressure_spike = params.get("pressure_spike_score", 0)

        if pressure_spike > 0.7:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.HIGH,
                alert_type="pressure_instability",
                message=f"Standpipe pressure instability detected. Spike score: {pressure_spike:.2f}.",
                risk_probability=pressure_spike,
                triggered_at=datetime.now(),
                recommendations=[
                    "Check for partial pack-off conditions",
                    "Verify pump efficiency",
                    "Slowly increase flow rate to clear obstruction",
                    "Prepare to pull out of hole if condition worsens",
                ],
                parameters=params,
            )
        return None

    def _check_vibration(self, well_id: str, params: Dict) -> Optional[DrillingAlert]:
        vibration = params.get("vibration_level", 0)

        if vibration >= self.thresholds["vibration_critical"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.CRITICAL,
                alert_type="severe_vibration",
                message=f"CRITICAL vibration level: {vibration:.1f}g. BHA damage risk.",
                risk_probability=min(0.9, vibration / 12),
                triggered_at=datetime.now(),
                recommendations=[
                    "IMMEDIATELY reduce WOB",
                    "Reduce RPM to break stick-slip cycle",
                    "Consider pulling out of hole for BHA inspection",
                    "Evaluate bit condition",
                ],
                parameters=params,
            )
        elif vibration >= self.thresholds["vibration_warning"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.MEDIUM,
                alert_type="elevated_vibration",
                message=f"Elevated vibration: {vibration:.1f}g. Monitor closely.",
                risk_probability=min(0.6, vibration / 10),
                triggered_at=datetime.now(),
                recommendations=[
                    "Adjust WOB/RPM combination",
                    "Monitor stick-slip index",
                    "Consider activating vibration dampening tools",
                ],
                parameters=params,
            )
        return None

    def _check_hole_cleaning(self, well_id: str, params: Dict) -> Optional[DrillingAlert]:
        hci = params.get("hole_cleaning_index", 1.0)
        cuttings = params.get("cuttings_volume", 0)

        if hci < self.thresholds["hole_cleaning_poor"]:
            return DrillingAlert(
                alert_id=str(uuid.uuid4())[:8],
                well_id=well_id,
                severity=AlertSeverity.HIGH,
                alert_type="poor_hole_cleaning",
                message=f"Poor hole cleaning detected. HCI: {hci:.2f}, Cuttings: {cuttings:.1f}%.",
                risk_probability=min(0.7, (1 - hci)),
                triggered_at=datetime.now(),
                recommendations=[
                    "Increase flow rate to improve annular velocity",
                    "Consider sweeps with high-viscosity pills",
                    "Increase pipe rotation speed",
                    "Perform backreaming to re-clean hole sections",
                    "Review mud rheology and adjust for better cuttings transport",
                ],
                parameters=params,
            )
        return None

    def get_active_alerts(self, well_id: Optional[str] = None) -> List[DrillingAlert]:
        if well_id:
            return [a for a in self.active_alerts if a.well_id == well_id]
        return self.active_alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def clear_resolved(self, well_id: str, current_probability: float):
        self.active_alerts = [
            a for a in self.active_alerts
            if not (a.well_id == well_id and current_probability < self.thresholds["stuck_probability_low"])
        ]
