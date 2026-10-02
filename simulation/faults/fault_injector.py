"""
GridShield AI - Fault Injection Engine
WHY: Allows manual and programmatic injection of various fault types.
WHAT: Supports 15+ fault categories affecting grid, sensors, and comms.
HOW: Modifies pandapower network and sensor simulator states.
INPUT: Fault type, component, severity, duration.
OUTPUT: Modified grid state and sensor effects.
"""

import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger
from enum import Enum


class FaultType(str, Enum):
    TRANSMISSION_LINE_FAILURE = "TRANSMISSION_LINE_FAILURE"
    LINE_OVERLOAD = "LINE_OVERLOAD"
    TRANSFORMER_OVERLOAD = "TRANSFORMER_OVERLOAD"
    TRANSFORMER_FAILURE = "TRANSFORMER_FAILURE"
    VOLTAGE_DROP = "VOLTAGE_DROP"
    OVERVOLTAGE = "OVERVOLTAGE"
    FREQUENCY_DISTURBANCE = "FREQUENCY_DISTURBANCE"
    GENERATOR_FAILURE = "GENERATOR_FAILURE"
    BREAKER_FAILURE = "BREAKER_FAILURE"
    SWITCH_FAILURE = "SWITCH_FAILURE"
    SENSOR_FAILURE = "SENSOR_FAILURE"
    COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"
    SUDDEN_LOAD_INCREASE = "SUDDEN_LOAD_INCREASE"
    RENEWABLE_DROP = "RENEWABLE_DROP"
    MULTIPLE_FAULT = "MULTIPLE_FAULT"


@dataclass
class FaultRecord:
    fault_id: str
    component_id: str
    fault_type: str
    severity: float
    start_time: datetime
    expected_duration: float  # seconds
    actual_duration: Optional[float] = None
    status: str = "ACTIVE"
    sensor_effects: Dict = field(default_factory=dict)
    grid_effects: Dict = field(default_factory=dict)
    description: str = ""
    resolved_at: Optional[datetime] = None


class FaultInjector:
    """
    Manages fault injection into the virtual power grid.
    Records all faults for analysis and recovery tracking.
    """

    def __init__(self, grid_simulator, sensor_simulator):
        self.grid = grid_simulator
        self.sensors = sensor_simulator
        self.active_faults: Dict[str, FaultRecord] = {}
        self.fault_history: List[FaultRecord] = []
        logger.info("FaultInjector initialized")

    def inject_fault(self, component_id: str, fault_type: str,
                     severity: float = 0.5, duration: float = 60.0,
                     description: str = "") -> FaultRecord:
        """
        Inject a fault into the virtual grid.

        Steps:
        1. Create fault record
        2. Apply fault to grid simulation
        3. Apply sensor effects
        4. Log the fault event
        """
        fault_id = f"F-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        severity = np.clip(severity, 0.0, 1.0)

        fault = FaultRecord(
            fault_id=fault_id,
            component_id=component_id,
            fault_type=fault_type,
            severity=severity,
            start_time=datetime.utcnow(),
            expected_duration=duration,
            description=description or f"{fault_type} on {component_id}"
        )

        # Apply fault based on type
        success = False
        ft = FaultType(fault_type)

        if ft == FaultType.TRANSMISSION_LINE_FAILURE:
            success = self._inject_line_failure(fault)
        elif ft == FaultType.LINE_OVERLOAD:
            success = self._inject_line_overload(fault)
        elif ft == FaultType.TRANSFORMER_OVERLOAD:
            success = self._inject_trafo_overload(fault)
        elif ft == FaultType.TRANSFORMER_FAILURE:
            success = self._inject_trafo_failure(fault)
        elif ft == FaultType.VOLTAGE_DROP:
            success = self._inject_voltage_drop(fault)
        elif ft == FaultType.OVERVOLTAGE:
            success = self._inject_overvoltage(fault)
        elif ft == FaultType.FREQUENCY_DISTURBANCE:
            success = self._inject_frequency_disturbance(fault)
        elif ft == FaultType.GENERATOR_FAILURE:
            success = self._inject_generator_failure(fault)
        elif ft == FaultType.BREAKER_FAILURE:
            success = self._inject_breaker_failure(fault)
        elif ft == FaultType.SENSOR_FAILURE:
            success = self._inject_sensor_failure(fault)
        elif ft == FaultType.COMMUNICATION_FAILURE:
            success = self._inject_comm_failure(fault)
        elif ft == FaultType.SUDDEN_LOAD_INCREASE:
            success = self._inject_load_increase(fault)
        else:
            logger.error(f"Unknown fault type: {fault_type}")

        if success:
            self.active_faults[fault_id] = fault
            self.fault_history.append(fault)
            logger.warning(
                f"FAULT INJECTED: {fault_id} | Type: {fault_type} | "
                f"Component: {component_id} | Severity: {severity:.2f}"
            )
        else:
            fault.status = "FAILED"
            logger.error(f"Failed to inject fault: {fault_type} on {component_id}")

        return fault

    def _inject_line_failure(self, fault: FaultRecord) -> bool:
        line_name = fault.component_id.replace("LINE_", "")
        success = self.grid.inject_line_fault(line_name)
        if success:
            fault.sensor_effects = {
                "current": {"type": "set", "value": 0.0},
                "loading_percent": {"type": "set", "value": 0.0},
                "line_status": "FAULT",
                "breaker_status": "TRIPPED"
            }
            fault.grid_effects = {"action": "line_out_of_service", "line": line_name}
            self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return success

    def _inject_line_overload(self, fault: FaultRecord) -> bool:
        # Simulate overload by increasing loads on the connected buses
        line_name = fault.component_id.replace("LINE_", "")
        for idx in self.grid.net.line.index:
            if self.grid.net.line.at[idx, 'name'] == line_name:
                to_bus = int(self.grid.net.line.at[idx, 'to_bus'])
                # Find loads on this bus
                for lidx in self.grid.net.load.index:
                    if int(self.grid.net.load.at[lidx, 'bus']) == to_bus:
                        load_name = self.grid.net.load.at[lidx, 'name']
                        factor = 1.0 + fault.severity * 0.8
                        self.grid.inject_load_increase(load_name, factor)
                        fault.sensor_effects = {
                            "loading_percent": {"type": "multiply", "value": factor},
                            "current": {"type": "multiply", "value": factor},
                            "temperature": {"type": "add", "value": fault.severity * 20}
                        }
                        self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
                        return True
        return False

    def _inject_trafo_overload(self, fault: FaultRecord) -> bool:
        trafo_name = fault.component_id
        for idx in self.grid.net.trafo.index:
            if self.grid.net.trafo.at[idx, 'name'] == trafo_name:
                lv_bus = int(self.grid.net.trafo.at[idx, 'lv_bus'])
                for lidx in self.grid.net.load.index:
                    if int(self.grid.net.load.at[lidx, 'bus']) == lv_bus:
                        factor = 1.0 + fault.severity
                        self.grid.inject_load_increase(
                            self.grid.net.load.at[lidx, 'name'], factor)
                fault.sensor_effects = {
                    "loading_percent": {"type": "multiply", "value": 1.3},
                    "temperature": {"type": "add", "value": fault.severity * 30}
                }
                self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
                return True
        return False

    def _inject_trafo_failure(self, fault: FaultRecord) -> bool:
        trafo_name = fault.component_id
        success = self.grid.inject_trafo_fault(trafo_name)
        if success:
            fault.sensor_effects = {
                "loading_percent": {"type": "set", "value": 0.0},
                "status": "FAULT"
            }
            self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return success

    def _inject_voltage_drop(self, fault: FaultRecord) -> bool:
        # Reduce voltage at a bus by increasing reactive load
        bus_id = None
        comp = self.grid.components.get(fault.component_id)
        if comp:
            bus_id = comp.bus_id
        if bus_id is not None:
            for lidx in self.grid.net.load.index:
                if int(self.grid.net.load.at[lidx, 'bus']) == bus_id:
                    q_orig = float(self.grid.net.load.at[lidx, 'q_mvar'])
                    self.grid.net.load.at[lidx, 'q_mvar'] = q_orig * (1 + fault.severity * 3)
                    fault.sensor_effects = {
                        "voltage": {"type": "multiply", "value": 1.0 - fault.severity * 0.15}
                    }
                    self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
                    return True
        return False

    def _inject_overvoltage(self, fault: FaultRecord) -> bool:
        fault.sensor_effects = {
            "voltage": {"type": "multiply", "value": 1.0 + fault.severity * 0.15}
        }
        self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return True

    def _inject_frequency_disturbance(self, fault: FaultRecord) -> bool:
        fault.sensor_effects = {
            "frequency": {"type": "add", "value": -fault.severity * 1.5}
        }
        self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return True

    def _inject_generator_failure(self, fault: FaultRecord) -> bool:
        gen_name = fault.component_id
        success = self.grid.inject_generator_fault(gen_name)
        if success:
            fault.sensor_effects = {
                "active_power": {"type": "set", "value": 0.0},
                "status": "FAULT"
            }
            self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return success

    def _inject_breaker_failure(self, fault: FaultRecord) -> bool:
        fault.sensor_effects = {
            "breaker_status": "STUCK",
            "status": "FAULT"
        }
        self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return True

    def _inject_sensor_failure(self, fault: FaultRecord) -> bool:
        sensor_id = f"{fault.component_id}_SENSOR"
        fault_modes = ["stuck", "zero", "noise", "drift"]
        mode = fault_modes[int(fault.severity * 3) % len(fault_modes)]
        self.sensors.inject_sensor_fault(sensor_id, mode)
        fault.sensor_effects = {"sensor_fault_mode": mode}
        return True

    def _inject_comm_failure(self, fault: FaultRecord) -> bool:
        sensor_id = f"{fault.component_id}_SENSOR"
        self.sensors.inject_comm_failure(sensor_id)
        fault.sensor_effects = {"communication": "OFFLINE"}
        return True

    def _inject_load_increase(self, fault: FaultRecord) -> bool:
        load_name = fault.component_id
        factor = 1.0 + fault.severity * 1.5  # Up to 2.5x
        success = self.grid.inject_load_increase(load_name, factor)
        if success:
            fault.sensor_effects = {
                "active_power": {"type": "multiply", "value": factor},
                "current": {"type": "multiply", "value": factor}
            }
            self.sensors.set_fault_effect(fault.component_id, fault.sensor_effects)
        return success

    def resolve_fault(self, fault_id: str) -> bool:
        """Mark a fault as resolved."""
        if fault_id in self.active_faults:
            fault = self.active_faults[fault_id]
            fault.status = "RESOLVED"
            fault.resolved_at = datetime.utcnow()
            fault.actual_duration = (
                fault.resolved_at - fault.start_time).total_seconds()

            # Clear sensor effects
            self.sensors.clear_fault_effect(fault.component_id)

            del self.active_faults[fault_id]
            logger.info(f"Fault {fault_id} resolved")
            return True
        return False

    def get_active_faults(self) -> List[FaultRecord]:
        return list(self.active_faults.values())

    def get_fault_history(self) -> List[FaultRecord]:
        return self.fault_history

    def clear_all_faults(self):
        """Clear all active faults and reset grid."""
        for fault_id in list(self.active_faults.keys()):
            self.resolve_fault(fault_id)
        self.sensors.clear_all_faults()
        self.grid.reset_grid()
        logger.info("All faults cleared, grid reset")
