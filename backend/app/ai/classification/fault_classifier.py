"""
GridShield AI - Fault Classification Module
WHY: Determines the type of fault after anomaly detection.
WHAT: Classifies faults into categories using Random Forest / XGBoost.
HOW: Uses feature engineering on sensor readings + grid state.
INPUT: Anomalous sensor readings with features.
OUTPUT: Fault type, confidence, alternative probabilities.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import joblib
import os


FAULT_CLASSES = [
    "NORMAL", "OVERLOAD", "VOLTAGE_DROP", "OVERVOLTAGE",
    "TRANSFORMER_FAILURE", "TRANSMISSION_LINE_FAILURE",
    "FREQUENCY_DISTURBANCE", "GENERATOR_FAILURE",
    "BREAKER_FAILURE", "SENSOR_FAILURE",
    "COMMUNICATION_FAILURE", "CASCADE_RISK"
]

FEATURE_NAMES = [
    "voltage", "current", "frequency", "active_power",
    "reactive_power", "temperature", "loading_percent",
    "power_factor", "voltage_deviation", "frequency_deviation",
    "loading_ratio", "temp_ratio", "power_imbalance",
    "voltage_rate_of_change", "current_rate_of_change"
]


@dataclass
class ClassificationResult:
    fault_type: str
    confidence: float
    probabilities: Dict[str, float]
    model_name: str
    features_used: List[str]


class FaultClassifier:
    """
    Multi-model fault classifier using ensemble methods.
    """

    def __init__(self):
        self.rf_model = RandomForestClassifier(
            n_estimators=200, max_depth=15,
            min_samples_split=5, random_state=42, n_jobs=-1
        )
        self.gb_model = GradientBoostingClassifier(
            n_estimators=150, max_depth=8,
            learning_rate=0.1, random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(FAULT_CLASSES)
        self.is_trained = False
        self._history: Dict[str, List[float]] = {}
        logger.info("FaultClassifier initialized")

    def extract_features(self, reading: Dict,
                         history: List[Dict] = None) -> np.ndarray:
        """Extract classification features from a reading."""
        voltage = reading.get("voltage", 230.0)
        current = reading.get("current", 100.0)
        frequency = reading.get("frequency", 50.0)
        active_power = reading.get("active_power", 5.0)
        reactive_power = reading.get("reactive_power", 1.0)
        temperature = reading.get("temperature", 35.0)
        loading = reading.get("loading_percent", 50.0)
        pf = reading.get("power_factor", 0.85)

        # Derived features
        vn = reading.get("voltage_level", 20.0) or 20.0
        voltage_deviation = abs(voltage - vn) / vn if vn > 0 else 0
        frequency_deviation = abs(frequency - 50.0) / 50.0
        loading_ratio = loading / 100.0
        temp_ratio = temperature / 80.0  # Normalized to typical critical
        apparent_power = np.sqrt(active_power**2 + reactive_power**2)
        power_imbalance = abs(active_power - apparent_power * pf) if apparent_power > 0 else 0

        # Rate of change features
        v_roc = 0.0
        c_roc = 0.0
        sensor_id = reading.get("sensor_id", "")
        if sensor_id in self._history and len(self._history[sensor_id]) >= 2:
            prev = self._history[sensor_id]
            v_roc = voltage - prev[-1] if len(prev) > 0 else 0
            c_roc = current - (prev[-2] if len(prev) > 1 else current)

        # Update history
        if sensor_id:
            if sensor_id not in self._history:
                self._history[sensor_id] = []
            self._history[sensor_id].append(voltage)
            if len(self._history[sensor_id]) > 10:
                self._history[sensor_id] = self._history[sensor_id][-10:]

        features = np.array([
            voltage, current, frequency, active_power,
            reactive_power, temperature, loading,
            pf, voltage_deviation, frequency_deviation,
            loading_ratio, temp_ratio, power_imbalance,
            v_roc, c_roc
        ])

        return features

    def classify(self, reading: Dict) -> ClassificationResult:
        """Classify a fault from sensor reading."""
        if not self.is_trained:
            return self._rule_based_classify(reading)

        features = self.extract_features(reading).reshape(1, -1)
        scaled = self.scaler.transform(features)

        # Random Forest prediction
        rf_proba = self.rf_model.predict_proba(scaled)[0]
        rf_class_idx = np.argmax(rf_proba)

        # Gradient Boosting prediction
        gb_proba = self.gb_model.predict_proba(scaled)[0]

        # Ensemble (average)
        avg_proba = (rf_proba + gb_proba) / 2
        best_idx = np.argmax(avg_proba)
        confidence = float(avg_proba[best_idx])

        fault_type = self.label_encoder.inverse_transform([best_idx])[0]

        # Get probability dict
        proba_dict = {}
        for idx, prob in enumerate(avg_proba):
            class_name = self.label_encoder.inverse_transform([idx])[0]
            if prob > 0.01:
                proba_dict[class_name] = round(float(prob), 4)

        # Sort by probability
        proba_dict = dict(sorted(proba_dict.items(),
                                  key=lambda x: x[1], reverse=True))

        return ClassificationResult(
            fault_type=fault_type,
            confidence=round(confidence, 4),
            probabilities=proba_dict,
            model_name="ensemble_rf_gb",
            features_used=FEATURE_NAMES
        )

    def _rule_based_classify(self, reading: Dict) -> ClassificationResult:
        """Fallback rule-based classification when ML model is not trained."""
        voltage = reading.get("voltage", 230.0)
        current = reading.get("current", 100.0)
        frequency = reading.get("frequency", 50.0)
        loading = reading.get("loading_percent", 50.0)
        temperature = reading.get("temperature", 35.0)
        status = reading.get("status", "NORMAL")
        breaker = reading.get("breaker_status", "ON")
        line_status = reading.get("line_status", "NORMAL")

        probabilities = {c: 0.0 for c in FAULT_CLASSES}

        if status == "SENSOR_FAULT" or voltage == 0:
            probabilities["SENSOR_FAILURE"] = 0.8
            probabilities["TRANSMISSION_LINE_FAILURE"] = 0.1
        elif breaker == "TRIPPED" or line_status == "FAULT":
            probabilities["TRANSMISSION_LINE_FAILURE"] = 0.7
            probabilities["BREAKER_FAILURE"] = 0.15
        elif loading > 100:
            probabilities["OVERLOAD"] = 0.75
            probabilities["CASCADE_RISK"] = 0.15
        elif loading > 80:
            probabilities["OVERLOAD"] = 0.5
            probabilities["NORMAL"] = 0.3
        elif frequency < 49.5 or frequency > 50.5:
            probabilities["FREQUENCY_DISTURBANCE"] = 0.7
            probabilities["GENERATOR_FAILURE"] = 0.2
        elif temperature > 80:
            probabilities["OVERLOAD"] = 0.4
            probabilities["TRANSFORMER_FAILURE"] = 0.35
        else:
            probabilities["NORMAL"] = 0.6
            probabilities["OVERLOAD"] = 0.1

        # Normalize
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: round(v/total, 4) for k, v in probabilities.items()}

        best = max(probabilities, key=probabilities.get)
        probabilities = {k: v for k, v in probabilities.items() if v > 0.01}
        probabilities = dict(sorted(probabilities.items(),
                                    key=lambda x: x[1], reverse=True))

        return ClassificationResult(
            fault_type=best,
            confidence=round(probabilities.get(best, 0), 4),
            probabilities=probabilities,
            model_name="rule_based_fallback",
            features_used=FEATURE_NAMES
        )

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train classification models."""
        y_encoded = self.label_encoder.transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.rf_model.fit(X_train_scaled, y_train)
        self.gb_model.fit(X_train_scaled, y_train)

        rf_score = self.rf_model.score(X_test_scaled, y_test)
        gb_score = self.gb_model.score(X_test_scaled, y_test)

        self.is_trained = True
        logger.info(f"Classifier trained - RF: {rf_score:.3f}, GB: {gb_score:.3f}")

        return {"rf_accuracy": rf_score, "gb_accuracy": gb_score}

    def save(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        joblib.dump({
            "rf_model": self.rf_model,
            "gb_model": self.gb_model,
            "scaler": self.scaler,
            "label_encoder": self.label_encoder
        }, os.path.join(directory, "fault_classifier.joblib"))

    def load(self, directory: str):
        path = os.path.join(directory, "fault_classifier.joblib")
        if os.path.exists(path):
            data = joblib.load(path)
            self.rf_model = data["rf_model"]
            self.gb_model = data["gb_model"]
            self.scaler = data["scaler"]
            self.label_encoder = data["label_encoder"]
            self.is_trained = True
            logger.info("Classifier loaded")
