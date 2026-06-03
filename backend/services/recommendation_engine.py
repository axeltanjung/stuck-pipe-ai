from typing import Dict, List, Any
from backend.api.schemas import RiskLevel


class DrillingRecommendationEngine:
    def __init__(self):
        self.recommendation_rules = self._build_rules()

    def _build_rules(self) -> Dict[str, Dict]:
        return {
            "reduce_wob": {
                "title": "Reduce Weight on Bit",
                "description": "Decrease WOB to reduce mechanical friction and sticking tendency",
                "conditions": {"wob_high": True, "torque_elevated": True},
                "expected_reduction": 0.15,
                "priority": "high",
                "category": "mechanical",
                "implementation": "Gradually reduce WOB by 5-10 klbs while monitoring ROP. Target minimum WOB for adequate penetration rate.",
            },
            "increase_circulation": {
                "title": "Increase Circulation Rate",
                "description": "Improve annular velocity for better cuttings transport and hole cleaning",
                "conditions": {"hole_cleaning_poor": True, "cuttings_high": True},
                "expected_reduction": 0.20,
                "priority": "high",
                "category": "hydraulics",
                "implementation": "Increase pump rate by 50-100 GPM. Verify ECD stays within safe window. Monitor returns for cuttings loading.",
            },
            "reduce_rpm": {
                "title": "Reduce Rotary Speed",
                "description": "Lower RPM to mitigate stick-slip vibration and reduce lateral forces",
                "conditions": {"vibration_high": True, "stick_slip_high": True},
                "expected_reduction": 0.12,
                "priority": "medium",
                "category": "mechanical",
                "implementation": "Reduce RPM by 20-40. Monitor vibration response. Consider anti-stick-slip systems.",
            },
            "perform_reaming": {
                "title": "Perform Backreaming",
                "description": "Ream wellbore to remove ledges and clean micro-doglegs",
                "conditions": {"drag_high": True, "depth_transition": True},
                "expected_reduction": 0.18,
                "priority": "medium",
                "category": "operational",
                "implementation": "Pull back 2-3 stands while rotating and circulating. Ream down slowly to original depth.",
            },
            "optimize_mud": {
                "title": "Optimize Mud Properties",
                "description": "Adjust mud weight and rheology for current formation conditions",
                "conditions": {"differential_pressure_high": True, "formation_reactive": True},
                "expected_reduction": 0.22,
                "priority": "high",
                "category": "fluids",
                "implementation": "Reduce mud weight if overbalance exceeds 500 psi. Increase low-shear-rate viscosity for better hole cleaning.",
            },
            "wiper_trip": {
                "title": "Perform Wiper Trip",
                "description": "Condition hole through short trip to identify and clear tight spots",
                "conditions": {"cuttings_accumulation": True, "long_static": True},
                "expected_reduction": 0.15,
                "priority": "medium",
                "category": "operational",
                "implementation": "Pull pipe 500-1000ft above current depth while circulating. Lower back slowly with full flow.",
            },
            "viscous_sweep": {
                "title": "Pump Viscous Sweep",
                "description": "High-viscosity pill to improve cuttings removal from hole",
                "conditions": {"hole_cleaning_poor": True, "cuttings_accumulation": True},
                "expected_reduction": 0.16,
                "priority": "medium",
                "category": "fluids",
                "implementation": "Pump 30-50 bbl high-vis sweep (120-150 FV). Circulate to surface and monitor returns.",
            },
        }

    def generate_recommendations(
        self, parameters: Dict[str, float], risk_probability: float, risk_level: RiskLevel
    ) -> List[Dict[str, Any]]:
        applicable = []

        conditions = self._evaluate_conditions(parameters)

        for rule_id, rule in self.recommendation_rules.items():
            rule_conditions = rule["conditions"]
            matches = sum(1 for k, v in rule_conditions.items() if conditions.get(k, False) == v)
            relevance = matches / len(rule_conditions) if rule_conditions else 0

            if relevance >= 0.5 or risk_probability > 0.6:
                applicable.append({
                    "id": rule_id,
                    "title": rule["title"],
                    "description": rule["description"],
                    "expected_risk_reduction": rule["expected_reduction"],
                    "priority": rule["priority"],
                    "category": rule["category"],
                    "implementation": rule["implementation"],
                    "relevance_score": relevance,
                })

        applicable.sort(key=lambda x: (-x["relevance_score"], x["expected_risk_reduction"]))
        return applicable[:5]

    def _evaluate_conditions(self, params: Dict[str, float]) -> Dict[str, bool]:
        return {
            "wob_high": params.get("wob", 0) > 30,
            "torque_elevated": params.get("torque", 0) > 15000,
            "hole_cleaning_poor": params.get("hole_cleaning_index", 1) < 0.5,
            "cuttings_high": params.get("cuttings_volume", 0) > 15,
            "vibration_high": params.get("vibration_level", 0) > 7,
            "stick_slip_high": params.get("stick_slip_index", 0) > 0.5,
            "drag_high": params.get("drag_force", 0) > 50,
            "depth_transition": True,
            "differential_pressure_high": params.get("differential_pressure", 0) > 3000,
            "formation_reactive": params.get("wellbore_instability_score", 0) > 0.5,
            "cuttings_accumulation": params.get("cuttings_accumulation_risk", 0) > 10,
            "long_static": params.get("connection_time", 0) > 10,
        }

    def estimate_combined_reduction(self, recommendations: List[Dict]) -> float:
        if not recommendations:
            return 0
        reductions = [r["expected_risk_reduction"] for r in recommendations[:3]]
        combined = 1 - np.prod([1 - r for r in reductions])
        return min(0.5, combined)


import numpy as np
