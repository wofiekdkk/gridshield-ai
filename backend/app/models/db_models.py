"""
Database Models using Record Base
"""
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from app.database.session import Record, ColumnDef

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"

class FaultStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    CLASSIFIED = "CLASSIFIED"
    LOCALIZED = "LOCALIZED"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"

class User(Record):
    __tablename__ = "users"
    id = ColumnDef(primary_key=True)
    username = ColumnDef()
    email = ColumnDef()
    hashed_password = ColumnDef()
    role = ColumnDef()
    is_active = ColumnDef()
    created_at = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "users"
        self.setdefault("is_active", True)
        self.setdefault("created_at", datetime.utcnow().isoformat())

class GridComponent(Record):
    __tablename__ = "grid_components"
    id = ColumnDef(primary_key=True)
    component_id = ColumnDef()
    component_type = ColumnDef()
    name = ColumnDef()
    is_critical = ColumnDef()
    status = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "grid_components"
        self.setdefault("status", "NORMAL")

class Sensor(Record):
    __tablename__ = "sensors"
    id = ColumnDef(primary_key=True)
    sensor_id = ColumnDef()
    component_id = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "sensors"
        self.setdefault("is_online", True)

class SensorReading(Record):
    __tablename__ = "sensor_readings"
    id = ColumnDef(primary_key=True)
    sensor_id = ColumnDef()
    component_id = ColumnDef()
    timestamp = ColumnDef()
    voltage = ColumnDef()
    current = ColumnDef()
    frequency = ColumnDef()
    active_power = ColumnDef()
    reactive_power = ColumnDef()
    temperature = ColumnDef()
    power_factor = ColumnDef()
    load_percentage = ColumnDef()
    breaker_status = ColumnDef()
    line_status = ColumnDef()
    status = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "sensor_readings"
        self.setdefault("timestamp", datetime.utcnow().isoformat())
        self.setdefault("status", "NORMAL")

class FaultEvent(Record):
    __tablename__ = "fault_events"
    id = ColumnDef(primary_key=True)
    fault_id = ColumnDef()
    component_id = ColumnDef()
    fault_type = ColumnDef()
    severity = ColumnDef()
    confidence = ColumnDef()
    cascade_risk = ColumnDef()
    status = ColumnDef()
    start_time = ColumnDef()
    end_time = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "fault_events"
        self.setdefault("status", FaultStatus.DETECTED)
        self.setdefault("start_time", datetime.utcnow().isoformat())

class AIPrediction(Record):
    __tablename__ = "ai_predictions"
    id = ColumnDef(primary_key=True)
    fault_id = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "ai_predictions"
        self.setdefault("timestamp", datetime.utcnow().isoformat())

class FaultLocalization(Record):
    __tablename__ = "fault_localizations"
    id = ColumnDef(primary_key=True)
    fault_id = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "fault_localizations"
        self.setdefault("timestamp", datetime.utcnow().isoformat())

class RecoveryPlan(Record):
    __tablename__ = "recovery_plans"
    id = ColumnDef(primary_key=True)
    plan_id = ColumnDef()
    fault_id = ColumnDef()
    actions = ColumnDef()
    restored_load = ColumnDef()
    cascade_risk = ColumnDef()
    max_line_loading = ColumnDef()
    constraint_violations = ColumnDef()
    feasible = ColumnDef()
    objective_score = ColumnDef()
    selected = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "recovery_plans"
        self.setdefault("feasible", True)
        self.setdefault("selected", False)
        self.setdefault("created_at", datetime.utcnow().isoformat())

class RecoveryAction(Record):
    __tablename__ = "recovery_actions"
    id = ColumnDef(primary_key=True)
    fault_id = ColumnDef()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "recovery_actions"
        self.setdefault("executed_at", datetime.utcnow().isoformat())

class GridState(Record):
    __tablename__ = "grid_states"
    id = ColumnDef(primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "grid_states"
        self.setdefault("timestamp", datetime.utcnow().isoformat())

class SystemEvent(Record):
    __tablename__ = "system_events"
    id = ColumnDef(primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["__tablename__"] = "system_events"
        self.setdefault("timestamp", datetime.utcnow().isoformat())

# Bind column names automatically
for cls in [User, GridComponent, Sensor, SensorReading, FaultEvent, AIPrediction, FaultLocalization, RecoveryPlan, RecoveryAction, GridState, SystemEvent]:
    for attr, val in list(cls.__dict__.items()):
        if isinstance(val, ColumnDef):
            val.name = attr
