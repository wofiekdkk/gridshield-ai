"""
GridShield AI - Grid Component Database Models
WHY: Persistent storage for grid topology, components, states.
WHAT: SQLAlchemy models for all grid components.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.connection import Base
import enum


class ComponentType(str, enum.Enum):
    BUS = "BUS"
    GENERATOR = "GENERATOR"
    EXTERNAL_GRID = "EXTERNAL_GRID"
    LINE = "LINE"
    TRANSFORMER = "TRANSFORMER"
    LOAD = "LOAD"
    SWITCH = "SWITCH"
    BREAKER = "BREAKER"
    RENEWABLE = "RENEWABLE"


class ComponentStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    OVERLOADED = "OVERLOADED"
    FAULT = "FAULT"
    DISCONNECTED = "DISCONNECTED"
    RECOVERY = "RECOVERY"
    MAINTENANCE = "MAINTENANCE"


class LoadPriority(str, enum.Enum):
    CRITICAL = "CRITICAL"
    NORMAL = "NORMAL"
    NON_CRITICAL = "NON_CRITICAL"


class GridComponent(Base):
    __tablename__ = "grid_components"

    id = Column(Integer, primary_key=True, autoincrement=True)
    component_id = Column(String(100), unique=True, nullable=False, index=True)
    component_type = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    substation = Column(String(100), nullable=True)
    bus_id = Column(Integer, nullable=True)
    from_bus = Column(Integer, nullable=True)
    to_bus = Column(Integer, nullable=True)
    status = Column(String(50), default="NORMAL")
    is_active = Column(Boolean, default=True)
    rated_capacity = Column(Float, nullable=True)
    voltage_level = Column(Float, nullable=True)
    load_priority = Column(String(20), default="NORMAL")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    sensors = relationship("Sensor", back_populates="component")
    fault_events = relationship("FaultEvent", back_populates="component")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(100), unique=True, nullable=False, index=True)
    component_id = Column(String(100), ForeignKey("grid_components.component_id"))
    sensor_type = Column(String(50), nullable=False)
    location = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    last_reading_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="NORMAL")
    created_at = Column(DateTime, server_default=func.now())

    component = relationship("GridComponent", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(100), ForeignKey("sensors.sensor_id"), index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    frequency = Column(Float, nullable=True)
    active_power = Column(Float, nullable=True)
    reactive_power = Column(Float, nullable=True)
    power_factor = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    loading_percent = Column(Float, nullable=True)
    breaker_status = Column(String(10), nullable=True)
    line_status = Column(String(20), nullable=True)
    is_simulated = Column(Boolean, default=True)

    sensor = relationship("Sensor", back_populates="readings")


class FaultEvent(Base):
    __tablename__ = "fault_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fault_id = Column(String(100), unique=True, nullable=False, index=True)
    component_id = Column(String(100), ForeignKey("grid_components.component_id"))
    fault_type = Column(String(100), nullable=False)
    severity = Column(Float, default=0.5)
    confidence = Column(Float, default=0.0)
    cascade_risk = Column(Float, default=0.0)
    status = Column(String(50), default="DETECTED")
    description = Column(Text, nullable=True)
    detected_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    injected = Column(Boolean, default=False)
    sensor_effects = Column(JSON, nullable=True)

    component = relationship("GridComponent", back_populates="fault_events")
    ai_predictions = relationship("AIPrediction", back_populates="fault_event")
    recovery_plans = relationship("RecoveryPlan", back_populates="fault_event")


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(String(100), unique=True, nullable=False)
    fault_id = Column(String(100), ForeignKey("fault_events.fault_id"), nullable=True)
    prediction_type = Column(String(50), nullable=False)
    predicted_class = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    probabilities = Column(JSON, nullable=True)
    localization = Column(JSON, nullable=True)
    cascade_risk = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    input_features = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    fault_event = relationship("FaultEvent", back_populates="ai_predictions")


class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String(100), unique=True, nullable=False)
    fault_id = Column(String(100), ForeignKey("fault_events.fault_id"))
    actions = Column(JSON, nullable=False)
    restored_load = Column(Float, nullable=True)
    cascade_risk = Column(Float, nullable=True)
    max_line_loading = Column(Float, nullable=True)
    switching_operations = Column(Integer, default=0)
    constraint_violations = Column(JSON, nullable=True)
    feasible = Column(Boolean, default=False)
    objective_score = Column(Float, nullable=True)
    status = Column(String(50), default="GENERATED")
    selected = Column(Boolean, default=False)
    executed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    fault_event = relationship("FaultEvent", back_populates="recovery_plans")


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_id = Column(String(100), unique=True, nullable=False)
    plan_id = Column(String(100), nullable=False)
    fault_id = Column(String(100), nullable=False)
    action_type = Column(String(100), nullable=False)
    component_id = Column(String(100), nullable=False)
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)
    objective_score = Column(Float, nullable=True)
    constraint_status = Column(String(50), nullable=True)
    result = Column(String(50), nullable=True)
    executed_at = Column(DateTime, nullable=True)


class GridState(Base):
    __tablename__ = "grid_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(String(100), unique=True, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    overall_status = Column(String(50), default="NORMAL")
    total_generation = Column(Float, nullable=True)
    total_load = Column(Float, nullable=True)
    total_demand = Column(Float, nullable=True)
    active_faults = Column(Integer, default=0)
    cascade_risk = Column(Float, default=0.0)
    components_at_risk = Column(Integer, default=0)
    restored_load_pct = Column(Float, default=100.0)
    frequency = Column(Float, default=50.0)
    state_data = Column(JSON, nullable=True)


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(100), unique=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="INFO")
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    component_id = Column(String(100), nullable=True)
    user_id = Column(String(100), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    role = Column(String(20), default="VIEWER")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(100), nullable=True)
    action = Column(String(200), nullable=False)
    component_id = Column(String(100), nullable=True)
    old_state = Column(String(100), nullable=True)
    new_state = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
