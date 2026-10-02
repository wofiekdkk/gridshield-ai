"""
GridShield AI - Virtual IoT Sensor Simulator
WHY: Creates realistic virtual sensor data streams without physical hardware.
WHAT: Generates voltage, current, frequency, power, temperature readings.
HOW: Uses grid state from pandapower + noise models + fault-induced deviations.
INPUT: Grid state from power flow calculation.
OUTPUT: Sensor readings published to MQTT topics.
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger
import json
import time


@dataclass
class VirtualSensor:
    sensor_id: str
    component_id: str
    component_type: str
    substation: str
    bus_id: Optional[int] = None
    from_bus: Optional[int] = None
    to_bus: Optional[int] = None
    is_active: bool = True
    is_healthy: bool = True
    noise_std: float = 0.01
    drift: float = 0.0
    last_reading: Optional[Dict] = None


class SensorSimulator:
    """
    Virtual IoT Sensor Engine.

    Generates realistic sensor readings based on:
    1. Actual power flow results from pandapower
    2. Gaussian noise for measurement uncertainty
    3. Gradual load variation patterns
    4. Temperature correlation with loading
    5. Fault-induced signal deviations
    6. Sensor failure simulation
    """

    def __init__(self):
        self.sensors: Dict[str, VirtualSensor] = {}
        self._time_step = 0
        self._daily_pattern = self._create_daily_pattern()
        self._fault_effects: Dict[str, Dict] = {}
        self._sensor_faults: Dict[str, str] = {}
        self._comm_failures: Dict[str, bool] = {}
        logger.info("SensorSimulator initialized")

    def _create_daily_pattern(self) -> np.ndarray:
        """Create a realistic daily load pattern (24 hours, hourly)."""
        hours = np.arange(24)
        # Typical load curve: low at night, peaks at morning and evening
        pattern = (
            0.6 + 0.15 * np.sin(2 * np.pi * (hours - 6) / 24) +
            0.1 * np.sin(4 * np.pi * (hours - 9) / 24) +
            0.05 * np.cos(2 * np.pi * (hours - 18) / 12)
        )
        return np.clip(pattern, 0.4, 1.0)

    def create_sensors_from_grid(self, grid_components: Dict) -> List[VirtualSensor]:
        """Create virtual sensors for all grid components."""
        self.sensors.clear()

        for comp_id, comp_info in grid_components.items():
            sensor = VirtualSensor(
                sensor_id=f"{comp_id}_SENSOR",
                component_id=comp_id,
                component_type=comp_info.component_type,
                substation=comp_info.substation,
                bus_id=comp_info.bus_id,
                from_bus=comp_info.from_bus,
                to_bus=comp_info.to_bus,
                noise_std=0.005 + np.random.uniform(0, 0.01)
            )
            self.sensors[sensor.sensor_id] = sensor

        logger.info(f"Created {len(self.sensors)} virtual sensors")
        return list(self.sensors.values())

    def generate_readings(self, grid_state: Dict) -> List[Dict]:
        """
        Generate sensor readings from current grid state.

        For each active sensor:
        1. Get base electrical values from power flow results
        2. Apply measurement noise
        3. Apply daily load variation
        4. Apply fault effects if any
        5. Apply sensor faults if any
        6. Calculate derived quantities (temperature, power factor)
        """
        self._time_step += 1
        readings = []
        current_hour = datetime.now().hour
        load_factor = float(self._daily_pattern[current_hour % 24])

        for sensor_id, sensor in self.sensors.items():
            # Skip if communication failure
            if self._comm_failures.get(sensor_id, False):
                continue

            if not sensor.is_active:
                continue

            reading = self._generate_single_reading(
                sensor, grid_state, load_factor
            )

            if reading:
                sensor.last_reading = reading
                readings.append(reading)

        return readings

    def _generate_single_reading(self, sensor: VirtualSensor,
                                  grid_state: Dict, load_factor: float) -> Optional[Dict]:
        """Generate a single sensor reading."""
        timestamp = datetime.utcnow().isoformat()
        noise = lambda std=sensor.noise_std: np.random.normal(0, std)

        reading = {
            "sensor_id": sensor.sensor_id,
            "component_id": sensor.component_id,
            "component_type": sensor.component_type,
            "timestamp": timestamp,
            "is_simulated": True
        }

        if sensor.component_type == "BUS":
            reading.update(self._bus_reading(sensor, grid_state, noise))
        elif sensor.component_type == "LINE":
            reading.update(self._line_reading(sensor, grid_state, noise))
        elif sensor.component_type == "TRANSFORMER":
            reading.update(self._trafo_reading(sensor, grid_state, noise))
        elif sensor.component_type == "LOAD":
            reading.update(self._load_reading(sensor, grid_state, noise, load_factor))
        elif sensor.component_type == "GENERATOR":
            reading.update(self._gen_reading(sensor, grid_state, noise))
        elif sensor.component_type == "BREAKER":
            reading.update(self._breaker_reading(sensor, grid_state))
        elif sensor.component_type == "EXTERNAL_GRID":
            reading.update(self._ext_grid_reading(sensor, grid_state, noise))
        else:
            reading.update({
                "voltage": 230.0 + noise(1.0),
                "current": 0.0,
                "frequency": 50.0 + noise(0.02),
                "status": "NORMAL"
            })

        # Apply sensor fault effects
        if sensor_id := sensor.sensor_id:
            if sensor_id in self._sensor_faults:
                reading = self._apply_sensor_fault(reading, self._sensor_faults[sensor_id])

        # Apply fault effects
        if sensor.component_id in self._fault_effects:
            reading = self._apply_fault_effects(
                reading, self._fault_effects[sensor.component_id])

        return reading

    def _bus_reading(self, sensor: VirtualSensor, state: Dict, noise) -> Dict:
        bus_key = sensor.component_id
        bus_data = state.get("buses", {}).get(bus_key, {})
        vm_pu = bus_data.get("vm_pu", 1.0)
        vn_kv = bus_data.get("vn_kv", 20.0)
        voltage_kv = vm_pu * vn_kv

        return {
            "voltage": round(float(voltage_kv * (1 + noise())), 3),
            "voltage_pu": round(float(vm_pu + noise(0.002)), 4),
            "frequency": round(float(state.get("frequency", 50.0) + noise(0.02)), 3),
            "active_power": round(float(bus_data.get("p_mw", 0) + noise(0.1)), 3),
            "reactive_power": round(float(bus_data.get("q_mvar", 0) + noise(0.05)), 3),
            "temperature": round(float(25 + abs(bus_data.get("p_mw", 0)) * 2 + noise(0.5) * 5), 1),
            "status": bus_data.get("status", "NORMAL"),
            "line_status": "NORMAL" if bus_data.get("in_service", True) else "DISCONNECTED"
        }

    def _line_reading(self, sensor: VirtualSensor, state: Dict, noise) -> Dict:
        line_name = sensor.component_id.replace("LINE_", "")
        line_data = state.get("lines", {}).get(line_name, {})
        loading = line_data.get("loading_percent", 0.0)

        base_current = loading * 0.01 * 200  # Approximate base current
        temperature = 25 + loading * 0.5 + np.random.normal(0, 1)

        return {
            "voltage": round(float(20.0 * (1 + noise())), 3),
            "current": round(float(max(0, base_current + noise(2))), 2),
            "frequency": round(float(state.get("frequency", 50.0) + noise(0.02)), 3),
            "active_power": round(float(line_data.get("p_from_mw", 0) + noise(0.05)), 3),
            "reactive_power": round(float(noise(0.1)), 3),
            "loading_percent": round(float(max(0, loading + noise(0.5) * 3)), 2),
            "temperature": round(float(max(15, temperature)), 1),
            "power_factor": round(float(np.clip(0.85 + noise(0.02), 0.7, 1.0)), 3),
            "line_status": line_data.get("status", "NORMAL"),
            "breaker_status": "ON" if line_data.get("in_service", True) else "OFF",
            "status": line_data.get("status", "NORMAL")
        }

    def _trafo_reading(self, sensor: VirtualSensor, state: Dict, noise) -> Dict:
        trafo_name = sensor.component_id.replace("TRAFO_", "").replace("LINE_", "")
        # Try to find the trafo in state
        trafo_data = state.get("transformers", {}).get(sensor.component_id, {})
        if not trafo_data:
            trafo_data = state.get("transformers", {}).get(
                sensor.component_id.replace("TRAFO_", ""), {})

        loading = trafo_data.get("loading_percent", 50.0)
        temperature = 35 + loading * 0.4 + np.random.normal(0, 1.5)

        return {
            "voltage": round(float(20.0 * (1 + noise())), 3),
            "current": round(float(loading * 2 + noise(1)), 2),
            "frequency": round(float(state.get("frequency", 50.0) + noise(0.02)), 3),
            "loading_percent": round(float(max(0, loading + noise(0.5) * 2)), 2),
            "temperature": round(float(max(20, temperature)), 1),
            "oil_temperature": round(float(max(20, temperature - 5 + noise(1))), 1),
            "status": trafo_data.get("status", "NORMAL"),
            "breaker_status": "ON" if trafo_data.get("in_service", True) else "OFF"
        }

    def _load_reading(self, sensor: VirtualSensor, state: Dict,
                       noise, load_factor: float) -> Dict:
        load_data = state.get("loads", {}).get(sensor.component_id, {})
        p_mw = load_data.get("p_mw", 1.0)
        q_mvar = load_data.get("q_mvar", 0.3)

        apparent = np.sqrt(p_mw**2 + q_mvar**2)
        pf = p_mw / apparent if apparent > 0 else 0.85

        return {
            "voltage": round(float(20.0 * (1 + noise())), 3),
            "current": round(float(apparent * 50 / 20 + noise(1)), 2),
            "frequency": round(float(state.get("frequency", 50.0) + noise(0.02)), 3),
            "active_power": round(float(p_mw + noise(0.05)), 3),
            "reactive_power": round(float(q_mvar + noise(0.02)), 3),
            "power_factor": round(float(np.clip(pf + noise(0.01), 0.7, 1.0)), 3),
            "loading_percent": round(float(p_mw / max(load_data.get("p_mw", 1), 0.01) * 100), 1),
            "temperature": round(float(30 + p_mw * 3 + noise(0.5) * 3), 1),
            "status": "NORMAL" if load_data.get("in_service", True) else "DISCONNECTED"
        }

    def _gen_reading(self, sensor: VirtualSensor, state: Dict, noise) -> Dict:
        gen_data = state.get("generators", {}).get(sensor.component_id, {})
        p_mw = gen_data.get("p_mw", 50.0)
        q_mvar = gen_data.get("q_mvar", 10.0)

        return {
            "voltage": round(float(110.0 * gen_data.get("vm_pu", 1.02) + noise(0.5)), 3),
            "current": round(float(p_mw * 10 + noise(2)), 2),
            "frequency": round(float(state.get("frequency", 50.0) + noise(0.01)), 3),
            "active_power": round(float(p_mw + noise(0.1)), 3),
            "reactive_power": round(float(q_mvar + noise(0.05)), 3),
            "temperature": round(float(45 + p_mw * 0.3 + noise(1)), 1),
            "status": "NORMAL" if gen_data.get("in_service", True) else "FAULT"
        }

    def _ext_grid_reading(self, sensor: VirtualSensor, state: Dict, noise) -> Dict:
        return {
            "voltage": round(float(110.0 * 1.02 + noise(0.3)), 3),
            "frequency": round(float(state.get("frequency", 50.0) + noise(0.01)), 3),
            "active_power": round(float(state.get("total_generation", 20) + noise(0.1)), 3),
            "status": "NORMAL"
        }

    def _breaker_reading(self, sensor: VirtualSensor, state: Dict) -> Dict:
        return {
            "breaker_status": "ON",
            "current": 0.0,
            "temperature": round(float(25 + np.random.normal(0, 2)), 1),
            "status": "NORMAL"
        }

    def _apply_fault_effects(self, reading: Dict, effects: Dict) -> Dict:
        """Apply fault effects to sensor readings."""
        for key, modifier in effects.items():
            if key in reading and isinstance(reading[key], (int, float)):
                if isinstance(modifier, dict):
                    if modifier.get("type") == "multiply":
                        reading[key] = round(reading[key] * modifier["value"], 3)
                    elif modifier.get("type") == "add":
                        reading[key] = round(reading[key] + modifier["value"], 3)
                    elif modifier.get("type") == "set":
                        reading[key] = modifier["value"]
                else:
                    reading[key] = round(reading[key] * modifier, 3)
        return reading

    def _apply_sensor_fault(self, reading: Dict, fault_type: str) -> Dict:
        """Simulate sensor malfunction."""
        if fault_type == "stuck":
            # Sensor reports same value
            reading["voltage"] = 230.0
            reading["current"] = 100.0
            reading["status"] = "SENSOR_FAULT"
        elif fault_type == "zero":
            reading["voltage"] = 0.0
            reading["current"] = 0.0
            reading["status"] = "SENSOR_FAULT"
        elif fault_type == "noise":
            for key in ["voltage", "current", "active_power"]:
                if key in reading:
                    reading[key] = round(reading[key] + np.random.normal(0, 50), 2)
            reading["status"] = "SENSOR_FAULT"
        elif fault_type == "drift":
            for key in ["voltage", "current"]:
                if key in reading:
                    reading[key] = round(reading[key] * 1.15, 2)
        return reading

    def inject_sensor_fault(self, sensor_id: str, fault_type: str):
        """Inject a fault into a specific sensor."""
        self._sensor_faults[sensor_id] = fault_type
        logger.warning(f"Sensor fault injected: {sensor_id} -> {fault_type}")

    def clear_sensor_fault(self, sensor_id: str):
        self._sensor_faults.pop(sensor_id, None)

    def inject_comm_failure(self, sensor_id: str):
        """Simulate communication failure for a sensor."""
        self._comm_failures[sensor_id] = True
        logger.warning(f"Communication failure: {sensor_id}")

    def clear_comm_failure(self, sensor_id: str):
        self._comm_failures.pop(sensor_id, None)

    def set_fault_effect(self, component_id: str, effects: Dict):
        """Set fault effects for a component's sensors."""
        self._fault_effects[component_id] = effects

    def clear_fault_effect(self, component_id: str):
        self._fault_effects.pop(component_id, None)

    def clear_all_faults(self):
        self._fault_effects.clear()
        self._sensor_faults.clear()
        self._comm_failures.clear()

    def get_mqtt_topic(self, sensor: VirtualSensor) -> str:
        """Get MQTT topic for a sensor."""
        sub = sensor.substation.lower().replace(" ", "_")
        comp = sensor.component_id.lower()
        return f"grid/{sub}/{comp}/sensors"

    def get_all_topics(self) -> List[str]:
        return list(set(
            self.get_mqtt_topic(s) for s in self.sensors.values()
        ))
