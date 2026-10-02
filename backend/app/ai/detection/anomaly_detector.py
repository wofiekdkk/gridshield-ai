"""
GridShield AI - Multi-Layer Anomaly Detection
WHY: Detects abnormal grid behavior using rules + ML + temporal analysis.
WHAT: Three detection layers - rule-based, Isolation Forest/Autoencoder, temporal.
HOW: Processes sensor readings through all layers, combines scores.
INPUT: Sensor readings (voltage, current, frequency, power, temperature).
OUTPUT: Anomaly score, anomaly flag, detection method, affected sensors.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import joblib
import os


@dataclass
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    confidence: float
    detection_layer: str
    details: Dict
    affected_sensors: List[str]
    timestamp: datetime


class RuleBasedDetector:
    """
    LAYER 1: Rule-based electrical constraint detection.
    Checks hard physical limits that always indicate problems.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {
            "voltage_min_pu": 0.90,
            "voltage_max_pu": 1.10,
            "voltage_warning_low": 0.95,
            "voltage_warning_high": 1.05,
            "frequency_min": 49.5,
            "frequency_max": 50.5,
            "frequency_warning_low": 49.8,
            "frequency_warning_high": 50.2,
            "line_loading_warning": 80.0,
            "line_loading_critical": 95.0,
            "line_loading_max": 100.0,
            "temperature_warning": 65.0,
            "temperature_critical": 80.0,
            "temperature_max": 95.0
        }

    def detect(self, reading: Dict) -> Tuple[bool, float, Dict]:
        """Check a single reading against rules."""
        violations = []
        score = 0.0

        # Voltage checks
        v_pu = reading.get("voltage_pu")
        if v_pu is not None:
            if v_pu < self.config["voltage_min_pu"]:
                violations.append(f"UNDERVOLTAGE: {v_pu:.3f} pu")
                score = max(score, 0.9)
            elif v_pu < self.config["voltage_warning_low"]:
                violations.append(f"LOW_VOLTAGE_WARNING: {v_pu:.3f} pu")
                score = max(score, 0.5)
            if v_pu > self.config["voltage_max_pu"]:
                violations.append(f"OVERVOLTAGE: {v_pu:.3f} pu")
                score = max(score, 0.9)
            elif v_pu > self.config["voltage_warning_high"]:
                violations.append(f"HIGH_VOLTAGE_WARNING: {v_pu:.3f} pu")
                score = max(score, 0.5)

        # Frequency checks
        freq = reading.get("frequency")
        if freq is not None:
            if freq < self.config["frequency_min"] or freq > self.config["frequency_max"]:
                violations.append(f"FREQUENCY_VIOLATION: {freq:.2f} Hz")
                score = max(score, 0.85)
            elif freq < self.config["frequency_warning_low"] or freq > self.config["frequency_warning_high"]:
                violations.append(f"FREQUENCY_WARNING: {freq:.2f} Hz")
                score = max(score, 0.4)

        # Loading checks
        loading = reading.get("loading_percent")
        if loading is not None:
            if loading > self.config["line_loading_max"]:
                violations.append(f"OVERLOADED: {loading:.1f}%")
                score = max(score, 0.95)
            elif loading > self.config["line_loading_critical"]:
                violations.append(f"CRITICAL_LOADING: {loading:.1f}%")
                score = max(score, 0.8)
            elif loading > self.config["line_loading_warning"]:
                violations.append(f"HIGH_LOADING: {loading:.1f}%")
                score = max(score, 0.4)

        # Temperature checks
        temp = reading.get("temperature")
        if temp is not None:
            if temp > self.config["temperature_max"]:
                violations.append(f"EXTREME_TEMPERATURE: {temp:.1f}°C")
                score = max(score, 0.9)
            elif temp > self.config["temperature_critical"]:
                violations.append(f"CRITICAL_TEMPERATURE: {temp:.1f}°C")
                score = max(score, 0.7)
            elif temp > self.config["temperature_warning"]:
                violations.append(f"HIGH_TEMPERATURE: {temp:.1f}°C")
                score = max(score, 0.3)

        # Breaker/status checks
        if reading.get("breaker_status") == "TRIPPED":
            violations.append("BREAKER_TRIPPED")
            score = max(score, 0.95)

        if reading.get("line_status") == "FAULT":
            violations.append("LINE_FAULT_STATUS")
            score = max(score, 0.95)

        if reading.get("status") == "FAULT":
            violations.append("COMPONENT_FAULT_STATUS")
            score = max(score, 0.9)

        is_anomaly = score > 0.3
        return is_anomaly, score, {"violations": violations}


class MLAnomalyDetector:
    """
    LAYER 2: Machine Learning anomaly detection.
    Uses Isolation Forest for unsupervised anomaly detection.
    """

    FEATURES = [
        "voltage", "current", "frequency", "active_power",
        "reactive_power", "temperature", "loading_percent", "power_factor"
    ]

    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            max_features=1.0,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []

    def extract_features(self, reading: Dict) -> Optional[np.ndarray]:
        """Extract feature vector from a sensor reading."""
        features = []
        for f in self.FEATURES:
            val = reading.get(f)
            if val is None or not isinstance(val, (int, float)):
                features.append(0.0)
            else:
                features.append(float(val))
        return np.array(features)

    def add_training_sample(self, reading: Dict):
        """Accumulate training data from normal operation."""
        features = self.extract_features(reading)
        if features is not None:
            self.training_data.append(features)

    def train(self, data: np.ndarray = None):
        """Train the Isolation Forest model."""
        if data is None:
            if len(self.training_data) < 50:
                logger.warning("Not enough training data for ML detector")
                return False
            data = np.array(self.training_data)

        self.scaler.fit(data)
        scaled = self.scaler.transform(data)
        self.model.fit(scaled)
        self.is_trained = True
        logger.info(f"ML Anomaly Detector trained on {len(data)} samples")
        return True

    def detect(self, reading: Dict) -> Tuple[bool, float]:
        """Detect anomaly in a single reading."""
        if not self.is_trained:
            return False, 0.0

        features = self.extract_features(reading)
        if features is None:
            return False, 0.0

        scaled = self.scaler.transform(features.reshape(1, -1))
        score = self.model.decision_function(scaled)[0]
        prediction = self.model.predict(scaled)[0]

        # Convert score to 0-1 range (lower decision function = more anomalous)
        anomaly_score = max(0, min(1, 0.5 - score))
        is_anomaly = prediction == -1

        return is_anomaly, anomaly_score

    def save(self, path: str):
        joblib.dump({"model": self.model, "scaler": self.scaler}, path)
        logger.info(f"ML detector saved to {path}")

    def load(self, path: str):
        if os.path.exists(path):
            data = joblib.load(path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.is_trained = True
            logger.info(f"ML detector loaded from {path}")


class TemporalAnalyzer:
    """
    LAYER 3: Temporal analysis for detecting trends and patterns.
    Detects sudden changes, gradual degradation, oscillations.
    """

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.history: Dict[str, deque] = {}

    def update(self, sensor_id: str, reading: Dict):
        """Add reading to history."""
        if sensor_id not in self.history:
            self.history[sensor_id] = deque(maxlen=self.window_size)
        self.history[sensor_id].append(reading)

    def analyze(self, sensor_id: str) -> Tuple[bool, float, Dict]:
        """Analyze temporal patterns for a sensor."""
        if sensor_id not in self.history or len(self.history[sensor_id]) < 5:
            return False, 0.0, {}

        history = list(self.history[sensor_id])
        details = {}
        score = 0.0

        # Check for sudden changes in voltage
        voltages = [h.get("voltage", 0) for h in history if h.get("voltage") is not None]
        if len(voltages) >= 3:
            recent = voltages[-3:]
            older = voltages[:-3] if len(voltages) > 3 else voltages[:1]
            if older:
                mean_old = np.mean(older)
                mean_recent = np.mean(recent)
                if mean_old > 0:
                    change_pct = abs(mean_recent - mean_old) / mean_old
                    if change_pct > 0.1:
                        details["sudden_voltage_change"] = round(change_pct * 100, 1)
                        score = max(score, min(1.0, change_pct * 5))

        # Check for gradual loading increase
        loadings = [h.get("loading_percent", 0) for h in history
                    if h.get("loading_percent") is not None]
        if len(loadings) >= 5:
            trend = np.polyfit(range(len(loadings)), loadings, 1)[0]
            if trend > 2.0:  # Increasing trend
                details["loading_trend"] = round(trend, 2)
                score = max(score, min(1.0, trend / 10))

        # Check for oscillations in frequency
        freqs = [h.get("frequency", 50) for h in history
                if h.get("frequency") is not None]
        if len(freqs) >= 5:
            std = np.std(freqs)
            if std > 0.2:
                details["frequency_oscillation"] = round(std, 3)
                score = max(score, min(1.0, std / 0.5))

        # Check for persistent abnormality
        statuses = [h.get("status", "NORMAL") for h in history]
        fault_count = sum(1 for s in statuses[-5:] if s in ["FAULT", "WARNING", "OVERLOADED"])
        if fault_count >= 3:
            details["persistent_abnormality"] = fault_count
            score = max(score, 0.7)

        is_anomaly = score > 0.3
        return is_anomaly, score, details


class MultiLayerAnomalyDetector:
    """
    Combined multi-layer anomaly detection system.
    Merges results from all three layers with weighted scoring.
    """

    def __init__(self):
        self.rule_detector = RuleBasedDetector()
        self.ml_detector = MLAnomalyDetector()
        self.temporal_analyzer = TemporalAnalyzer()
        self.weights = {"rule": 0.4, "ml": 0.35, "temporal": 0.25}
        self._training_mode = True
        self._training_count = 0
        self._min_training_samples = 100
        logger.info("MultiLayerAnomalyDetector initialized")

    def process_reading(self, reading: Dict) -> AnomalyResult:
        """Process a single sensor reading through all detection layers."""
        sensor_id = reading.get("sensor_id", "unknown")
        affected = []

        # Layer 1: Rule-based
        rule_anomaly, rule_score, rule_details = self.rule_detector.detect(reading)

        # Layer 2: ML-based
        if self._training_mode:
            if rule_score < 0.2:  # Only train on likely-normal data
                self.ml_detector.add_training_sample(reading)
                self._training_count += 1

            if self._training_count >= self._min_training_samples:
                self.ml_detector.train()
                self._training_mode = False
                logger.info("ML detector auto-trained after sufficient normal samples")

        ml_anomaly, ml_score = self.ml_detector.detect(reading)

        # Layer 3: Temporal
        self.temporal_analyzer.update(sensor_id, reading)
        temp_anomaly, temp_score, temp_details = self.temporal_analyzer.analyze(sensor_id)

        # Combined score
        combined_score = (
            self.weights["rule"] * rule_score +
            self.weights["ml"] * ml_score +
            self.weights["temporal"] * temp_score
        )

        is_anomaly = combined_score > 0.35 or rule_score > 0.7
        confidence = min(1.0, combined_score * 1.5)

        if is_anomaly:
            affected.append(sensor_id)

        details = {
            "rule_based": {"score": round(rule_score, 3), "details": rule_details},
            "ml_based": {"score": round(ml_score, 3), "is_anomaly": ml_anomaly},
            "temporal": {"score": round(temp_score, 3), "details": temp_details}
        }

        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=round(combined_score, 4),
            confidence=round(confidence, 4),
            detection_layer="rule" if rule_score > max(ml_score, temp_score) else
                           "ml" if ml_score > temp_score else "temporal",
            details=details,
            affected_sensors=affected,
            timestamp=datetime.utcnow()
        )

    def batch_process(self, readings: List[Dict]) -> List[AnomalyResult]:
        return [self.process_reading(r) for r in readings]

    def get_anomalous_readings(self, readings: List[Dict]) -> List[Tuple[Dict, AnomalyResult]]:
        results = []
        for reading in readings:
            result = self.process_reading(reading)
            if result.is_anomaly:
                results.append((reading, result))
        return results

    def save_models(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        self.ml_detector.save(os.path.join(directory, "anomaly_detector.joblib"))

    def load_models(self, directory: str):
        model_path = os.path.join(directory, "anomaly_detector.joblib")
        if os.path.exists(model_path):
            self.ml_detector.load(model_path)
            self._training_mode = False
