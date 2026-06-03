import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os
import json
from dataclasses import dataclass


@dataclass
class WellConfig:
    well_id: str
    total_depth: float
    formation_sequence: List[str]
    mud_weight_range: Tuple[float, float]
    base_rop: float
    region: str
    rig_type: str


FORMATION_TYPES = [
    "sandstone", "shale", "limestone", "dolomite", "claystone",
    "siltstone", "marl", "anhydrite", "salt", "granite"
]

DRILLING_PHASES = [
    "surface", "intermediate", "production", "horizontal", "vertical"
]

REGIONS = ["Gulf of Mexico", "North Sea", "Permian Basin", "Middle East", "West Africa"]
RIG_TYPES = ["Jack-Up", "Semi-Submersible", "Drillship", "Land Rig", "Platform"]


class DrillingPhysicsEngine:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def compute_ecd(self, mud_density: float, annular_pressure_loss: float, tvd: float) -> float:
        return mud_density + (annular_pressure_loss / (0.052 * tvd)) if tvd > 0 else mud_density

    def compute_differential_pressure(self, mud_density: float, pore_pressure_gradient: float, tvd: float) -> float:
        return (mud_density - pore_pressure_gradient) * 0.052 * tvd

    def compute_drag_force(self, hook_load: float, buoyant_weight: float, friction_factor: float) -> float:
        return abs(hook_load - buoyant_weight) * friction_factor

    def compute_torque(self, wob: float, rpm: float, bit_diameter: float, friction: float) -> float:
        base_torque = wob * bit_diameter * friction / 2
        rpm_factor = 1.0 + 0.001 * rpm
        return base_torque * rpm_factor

    def simulate_stuck_probability(
        self, diff_pressure: float, static_time: float,
        cuttings_vol: float, hole_cleaning_idx: float,
        drag_trend: float, vibration: float
    ) -> float:
        diff_stick_risk = min(1.0, diff_pressure / 5000 * 0.3)
        mech_stick_risk = min(1.0, (1 - hole_cleaning_idx) * 0.4 + cuttings_vol / 30 * 0.3)
        dynamic_risk = min(1.0, vibration / 10 * 0.2 + drag_trend * 0.1)
        time_factor = min(1.0, static_time / 60 * 0.2)
        total_risk = diff_stick_risk + mech_stick_risk + dynamic_risk + time_factor
        return min(0.95, max(0.01, total_risk))


class SyntheticDrillingDataGenerator:
    def __init__(self, num_wells: int = 15, rows_per_well: int = 18000, seed: int = 42):
        self.num_wells = num_wells
        self.rows_per_well = rows_per_well
        self.rng = np.random.default_rng(seed)
        self.physics = DrillingPhysicsEngine(seed)
        self.wells = self._create_well_configs()

    def _create_well_configs(self) -> List[WellConfig]:
        wells = []
        for i in range(self.num_wells):
            num_formations = self.rng.integers(4, 8)
            formations = list(self.rng.choice(FORMATION_TYPES, size=num_formations, replace=True))
            well = WellConfig(
                well_id=f"WELL-{i+1:03d}",
                total_depth=self.rng.uniform(8000, 22000),
                formation_sequence=formations,
                mud_weight_range=(self.rng.uniform(8.5, 10.0), self.rng.uniform(12.0, 16.5)),
                base_rop=self.rng.uniform(15, 80),
                region=self.rng.choice(REGIONS),
                rig_type=self.rng.choice(RIG_TYPES),
            )
            wells.append(well)
        return wells

    def _get_formation_at_depth(self, well: WellConfig, depth: float) -> str:
        section_length = well.total_depth / len(well.formation_sequence)
        idx = min(int(depth / section_length), len(well.formation_sequence) - 1)
        return well.formation_sequence[idx]

    def _get_drilling_phase(self, depth: float, total_depth: float) -> str:
        ratio = depth / total_depth
        if ratio < 0.15:
            return "surface"
        elif ratio < 0.4:
            return "intermediate"
        elif ratio < 0.7:
            return "production"
        elif ratio < 0.85:
            return "horizontal"
        else:
            return "vertical"

    def _generate_base_parameters(self, well: WellConfig, n: int) -> Dict[str, np.ndarray]:
        depths = np.linspace(100, well.total_depth, n)
        hole_depths = depths + self.rng.uniform(0, 50, n)

        mud_weight_min, mud_weight_max = well.mud_weight_range
        mud_density = np.linspace(mud_weight_min, mud_weight_max, n) + self.rng.normal(0, 0.05, n)

        wob = self.rng.uniform(5, 45, n) * (1 + 0.3 * np.sin(np.linspace(0, 8 * np.pi, n)))
        rpm = self.rng.uniform(40, 180, n) + self.rng.normal(0, 5, n)
        rpm = np.clip(rpm, 20, 220)

        base_rop = well.base_rop * (1 + 0.5 * np.sin(np.linspace(0, 4 * np.pi, n)))
        rop = base_rop + self.rng.normal(0, 5, n)
        rop = np.clip(rop, 1, 200)

        flow_rate = self.rng.uniform(200, 900, n) + self.rng.normal(0, 20, n)
        standpipe_pressure = self.rng.uniform(1500, 4500, n) + depths * 0.05

        hook_load = 100 + depths * 0.015 + self.rng.normal(0, 10, n)
        torque = wob * 0.8 + rpm * 0.3 + self.rng.normal(0, 500, n)
        torque = np.clip(torque, 500, 50000)

        return {
            "depth": depths,
            "hole_depth": hole_depths,
            "wob": wob,
            "rpm": rpm,
            "rop": rop,
            "torque": torque,
            "hook_load": hook_load,
            "standpipe_pressure": standpipe_pressure,
            "mud_flow_rate": flow_rate,
            "mud_density": mud_density,
        }

    def _generate_mud_parameters(self, n: int, depths: np.ndarray, mud_density: np.ndarray) -> Dict[str, np.ndarray]:
        ecd = mud_density + self.rng.uniform(0.1, 0.8, n) + depths * 0.00001
        flow_out = self.rng.uniform(180, 850, n) + self.rng.normal(0, 15, n)
        cuttings_volume = self.rng.uniform(1, 25, n) + np.abs(self.rng.normal(0, 3, n))
        mud_viscosity = self.rng.uniform(30, 80, n) + self.rng.normal(0, 3, n)

        return {
            "ecd": ecd,
            "flow_out": flow_out,
            "cuttings_volume": cuttings_volume,
            "mud_viscosity": mud_viscosity,
        }

    def _generate_dynamics(self, n: int, wob: np.ndarray, rpm: np.ndarray) -> Dict[str, np.ndarray]:
        vibration = self.rng.exponential(2, n) + wob * 0.01
        vibration = np.clip(vibration, 0.1, 15)

        stick_slip = np.where(rpm < 80, self.rng.uniform(0.3, 0.9, n), self.rng.uniform(0, 0.4, n))
        bit_wear = np.linspace(0, 1, n) + self.rng.normal(0, 0.05, n)
        bit_wear = np.clip(bit_wear, 0, 1)

        hole_cleaning = 1.0 - (self.rng.uniform(0, 0.5, n) + np.abs(self.rng.normal(0, 0.1, n)))
        hole_cleaning = np.clip(hole_cleaning, 0.1, 1.0)

        return {
            "vibration_level": vibration,
            "stick_slip_index": stick_slip,
            "bit_wear": bit_wear,
            "hole_cleaning_index": hole_cleaning,
        }

    def _generate_operational(self, n: int) -> Dict[str, np.ndarray]:
        connection_time = self.rng.exponential(5, n) + 2
        reaming_freq = self.rng.poisson(1.5, n).astype(float)
        tripping_speed = self.rng.uniform(500, 2500, n)
        pump_pressure = self.rng.uniform(1000, 4000, n)
        temperature = self.rng.uniform(80, 350, n)

        return {
            "connection_time": connection_time,
            "reaming_frequency": reaming_freq,
            "tripping_speed": tripping_speed,
            "pump_pressure": pump_pressure,
            "temperature": temperature,
        }

    def _generate_derived_features(self, params: Dict[str, np.ndarray], n: int) -> Dict[str, np.ndarray]:
        torque_diff = np.diff(params["torque"], prepend=params["torque"][0])
        torque_fluctuation = np.abs(torque_diff) / (np.abs(params["torque"]) + 1e-6)

        pressure_diff = np.diff(params["standpipe_pressure"], prepend=params["standpipe_pressure"][0])
        pressure_spike_score = np.clip(np.abs(pressure_diff) / 100, 0, 1)

        drag_force = np.abs(params["hook_load"] - np.mean(params["hook_load"])) * 0.1
        drag_trend = pd.Series(drag_force).rolling(window=50, min_periods=1).mean().values

        cuttings_accumulation = pd.Series(params["cuttings_volume"]).rolling(window=100, min_periods=1).sum().values / 100

        wellbore_instability = (
            params["vibration_level"] / 15 * 0.3 +
            (1 - params["hole_cleaning_index"]) * 0.3 +
            torque_fluctuation * 0.2 +
            pressure_spike_score * 0.2
        )
        wellbore_instability = np.clip(wellbore_instability, 0, 1)

        diff_pressure = (params["mud_density"] - self.rng.uniform(8, 11, n)) * 0.052 * params["depth"]
        diff_pressure = np.clip(diff_pressure, 0, 8000)

        return {
            "torque_fluctuation": torque_fluctuation,
            "pressure_spike_score": pressure_spike_score,
            "drag_force": drag_force,
            "drag_trend": drag_trend,
            "cuttings_accumulation_risk": cuttings_accumulation,
            "wellbore_instability_score": wellbore_instability,
            "differential_pressure": diff_pressure,
        }

    def _inject_stuck_pipe_events(self, df: pd.DataFrame) -> pd.DataFrame:
        n = len(df)
        stuck_risk = np.zeros(n)
        stuck_probability = np.zeros(n)
        diff_sticking_risk = np.zeros(n)
        mech_sticking_risk = np.zeros(n)
        instability_score = np.zeros(n)

        num_events = max(1, int(n * 0.03))
        event_centers = self.rng.choice(range(200, n - 200), size=num_events, replace=False)

        for center in event_centers:
            event_type = self.rng.choice(["differential", "mechanical", "dynamic"])
            event_duration = self.rng.integers(30, 150)
            start = max(0, center - event_duration // 2)
            end = min(n, center + event_duration // 2)
            ramp = np.linspace(0, 1, end - start)

            if event_type == "differential":
                df.loc[start:end-1, "differential_pressure"] *= (1 + 2.0 * ramp)
                df.loc[start:end-1, "mud_density"] += 0.5 * ramp
                df.loc[start:end-1, "connection_time"] *= (1 + 1.5 * ramp)
                diff_sticking_risk[start:end] = 0.6 + 0.35 * ramp
                stuck_probability[start:end] = 0.5 + 0.4 * ramp
                stuck_risk[start:end] = 1

            elif event_type == "mechanical":
                df.loc[start:end-1, "cuttings_volume"] *= (1 + 3.0 * ramp)
                df.loc[start:end-1, "hole_cleaning_index"] *= (1 - 0.5 * ramp)
                df.loc[start:end-1, "drag_force"] *= (1 + 2.5 * ramp)
                df.loc[start:end-1, "torque"] *= (1 + 1.5 * ramp)
                mech_sticking_risk[start:end] = 0.5 + 0.4 * ramp
                stuck_probability[start:end] = 0.4 + 0.5 * ramp
                stuck_risk[start:end] = 1

            else:
                df.loc[start:end-1, "vibration_level"] *= (1 + 2.0 * ramp)
                df.loc[start:end-1, "stick_slip_index"] = np.clip(
                    df.loc[start:end-1, "stick_slip_index"].values + 0.4 * ramp, 0, 1
                )
                df.loc[start:end-1, "torque_fluctuation"] *= (1 + 3.0 * ramp)
                df.loc[start:end-1, "pressure_spike_score"] = np.clip(
                    df.loc[start:end-1, "pressure_spike_score"].values + 0.3 * ramp, 0, 1
                )
                instability_score[start:end] = 0.6 + 0.3 * ramp
                stuck_probability[start:end] = 0.3 + 0.5 * ramp
                stuck_risk[start:end] = 1

        background_risk = self.rng.uniform(0, 0.15, n)
        stuck_probability = np.clip(stuck_probability + background_risk, 0, 0.99)

        no_event_mask = stuck_risk == 0
        instability_score[no_event_mask] = df.loc[no_event_mask, "wellbore_instability_score"].values
        diff_sticking_risk[no_event_mask] = np.clip(
            df.loc[no_event_mask, "differential_pressure"].values / 8000, 0, 0.4
        )
        mech_sticking_risk[no_event_mask] = np.clip(
            (1 - df.loc[no_event_mask, "hole_cleaning_index"].values) * 0.5, 0, 0.4
        )

        df["stuck_pipe_risk"] = stuck_risk.astype(int)
        df["stuck_pipe_probability"] = stuck_probability
        df["differential_sticking_risk"] = diff_sticking_risk
        df["mechanical_sticking_risk"] = mech_sticking_risk
        df["drilling_instability_score"] = instability_score

        risk_level_bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        risk_labels = ["very_low", "low", "moderate", "high", "critical"]
        df["operational_risk_level"] = pd.cut(
            stuck_probability, bins=risk_level_bins, labels=risk_labels, include_lowest=True
        )

        return df

    def _add_noise_and_artifacts(self, df: pd.DataFrame) -> pd.DataFrame:
        n = len(df)
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        missing_mask = self.rng.random((n, len(numeric_cols))) < 0.005
        for i, col in enumerate(numeric_cols):
            df.loc[missing_mask[:, i], col] = np.nan

        num_outliers = int(n * 0.002)
        outlier_indices = self.rng.choice(n, size=num_outliers, replace=False)
        outlier_cols = self.rng.choice(["torque", "standpipe_pressure", "vibration_level", "hook_load"], size=num_outliers)
        for idx, col in zip(outlier_indices, outlier_cols):
            df.loc[idx, col] = df[col].mean() + self.rng.uniform(3, 5) * df[col].std()

        for col in numeric_cols:
            noise = self.rng.normal(0, df[col].std() * 0.01, n)
            df[col] = df[col] + noise

        return df

    def generate_well_data(self, well: WellConfig) -> pd.DataFrame:
        n = self.rows_per_well
        start_time = datetime(2023, 1, 1) + timedelta(days=self.rng.integers(0, 180))
        timestamps = [start_time + timedelta(seconds=30 * i) for i in range(n)]

        params = self._generate_base_parameters(well, n)
        mud_params = self._generate_mud_parameters(n, params["depth"], params["mud_density"])
        dynamics = self._generate_dynamics(n, params["wob"], params["rpm"])
        operational = self._generate_operational(n)

        all_params = {**params, **mud_params, **dynamics, **operational}
        derived = self._generate_derived_features(all_params, n)
        all_params.update(derived)

        df = pd.DataFrame(all_params)
        df.insert(0, "timestamp", timestamps)
        df.insert(1, "well_id", well.well_id)
        df["formation_type"] = [self._get_formation_at_depth(well, d) for d in params["depth"]]
        df["drilling_phase"] = [self._get_drilling_phase(d, well.total_depth) for d in params["depth"]]
        df["region"] = well.region
        df["rig_type"] = well.rig_type

        df = self._inject_stuck_pipe_events(df)
        df = self._add_noise_and_artifacts(df)

        return df

    def generate_full_dataset(self) -> pd.DataFrame:
        all_data = []
        for well in self.wells:
            well_df = self.generate_well_data(well)
            all_data.append(well_df)
            print(f"Generated {len(well_df)} rows for {well.well_id} ({well.region})")

        dataset = pd.concat(all_data, ignore_index=True)
        dataset = dataset.sort_values(["well_id", "timestamp"]).reset_index(drop=True)
        return dataset

    def save_dataset(self, output_dir: str = "data/raw") -> str:
        os.makedirs(output_dir, exist_ok=True)
        dataset = self.generate_full_dataset()

        output_path = os.path.join(output_dir, "drilling_telemetry.csv")
        dataset.to_csv(output_path, index=False)

        stats = {
            "total_rows": len(dataset),
            "total_wells": dataset["well_id"].nunique(),
            "stuck_pipe_events": int(dataset["stuck_pipe_risk"].sum()),
            "event_rate": float(dataset["stuck_pipe_risk"].mean()),
            "features": list(dataset.columns),
            "formations": list(dataset["formation_type"].unique()),
            "regions": list(dataset["region"].unique()),
            "date_range": {
                "start": str(dataset["timestamp"].min()),
                "end": str(dataset["timestamp"].max()),
            },
            "depth_range": {
                "min": float(dataset["depth"].min()),
                "max": float(dataset["depth"].max()),
            },
        }

        stats_path = os.path.join(output_dir, "dataset_stats.json")
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)

        print(f"\nDataset saved: {output_path}")
        print(f"Total rows: {len(dataset):,}")
        print(f"Total wells: {dataset['well_id'].nunique()}")
        print(f"Stuck pipe events: {dataset['stuck_pipe_risk'].sum():,} ({dataset['stuck_pipe_risk'].mean()*100:.2f}%)")

        return output_path


if __name__ == "__main__":
    generator = SyntheticDrillingDataGenerator(num_wells=15, rows_per_well=18000, seed=42)
    output_path = generator.save_dataset("data/raw")
