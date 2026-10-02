"""
GridShield AI - Pydantic Schemas
WHY: Type-safe data validation for API requests/responses.
WHAT: Schemas for sensors, faults, recovery, grid state.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ---- Enums ----
class ComponentTypeEnum(str, Enum):
    BUS = "BUS"
    GENERATOR = "GENERATOR"
    EXTERNAL_GRID = "EXTERNAL_GRID"
    LINE = "LINE"
    TRANSFORMER = "TRANSFORMER"
    LOAD = "LOAD"
    SWITCH = "SWITCH"
    BREAKER = "BREAKER"
    RENEWABLE = "RENEWABLE"


class StatusEnum(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    OVERLOADED = "OVERLOADED"
    FAULT = "FAULT"
    DISCONNECTED = "DISCONNECTED"
    RECOVERY = "RECOVERY"


class FaultTypeEnum(str, Enum):
    NORMAL = "NORMAL"
    OVERLOAD = "OVERLOAD"
    VOLTAGE_DROP = "VOLTAGE_DROP"
    OVERVOLTAGE = "OVERVOLTAGE"
    TRANSFORMER_FAILURE = "TRANSFORMER_FAILURE"
    TRANSMISSION_LINE_FAILURE = "TRANSMISSION_LINE_FAILURE"
    FREQUENCY_DISTURBANCE = "FREQUENCY_DISTURBANCE"
    GENERATOR_FAILURE = "GENERATOR_FAILURE"
    BREAKER_FAILURE = "BREAKER_FAILURE"
    SENSOR_FAILURE = "SENSOR_FAILURE"
    COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"
    CASCADE_RISK = "CASCADE_RISK"


class SeverityEnum(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    RECOVERY = "RECOVERY"


class LoadPriorityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    NORMAL = "NORMAL"
    NON_CRITICAL = "NON_CRITICAL"


# ---- Sensor Schemas ----
class SensorReadingCreate(BaseModel):
    sensor_id: str
    component_id: Optional[str] = None
    timestamp: datetime
    voltage: Optional[float] = None
    current: Optional[float] = None
    frequency: Optional[float] = None
    active_power: Optional[float] = None
    reactive_power: Optional[float] = None
    power_factor: Optional[float] = None
    temperature: Optional[float] = None
    loading_percent: Optional[float] = None
    breaker_status: Optional[str] = "ON"
    line_status: Optional[str] = "NORMAL"


class SensorReadingResponse(SensorReadingCreate):
    id: int

    class Config:
        from_attributes = True


class SensorInfo(BaseModel):
    sensor_id: str
    component_id: str
    sensor_type: str
    location: Optional[str] = None
    is_active: bool = True
    status: str = "NORMAL"
    last_reading: Optional[SensorReadingCreate] = None


# ---- Component Schemas ----
class GridComponentResponse(BaseModel):
    component_id: str
    component_type: str
    name: str
    substation: Optional[str] = None
    status: str = "NORMAL"
    is_active: bool = True
    rated_capacity: Optional[float] = None
    voltage_level: Optional[float] = None
    load_priority: str = "NORMAL"
    metadata_json: Optional[Dict[str, Any]] = None


# ---- Fault Schemas ----
class FaultInjectRequest(BaseModel):
    component_id: str
    fault_type: str
    severity: float = Field(ge=0.0, le=1.0, default=0.5)
    duration_seconds: Optional[float] = 60.0
    description: Optional[str] = None


class FaultEventResponse(BaseModel):
    fault_id: str
    component_id: str
    fault_type: str
    severity: float
    confidence: float
    cascade_risk: float
    status: str
    description: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- AI Prediction Schemas ----
class AnomalyDetectionResult(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    confidence: float
    detection_method: str
    affected_sensors: List[str] = []
    timestamp: datetime


class FaultClassificationResult(BaseModel):
    fault_type: str
    confidence: float
    alternatives: Dict[str, float] = {}
    model_name: str = "ensemble"


class FaultLocalizationResult(BaseModel):
    component_id: str
    confidence: float
    affected_region: List[str] = []
    method: str = "topology_aware"
    top_candidates: List[Dict[str, Any]] = []


class CascadeRiskResult(BaseModel):
    risk_score: float
    risk_level: str
    affected_components: List[Dict[str, Any]] = []
    propagation_path: List[str] = []
    time_to_cascade: Optional[float] = None


# ---- Recovery Schemas ----
class RecoveryAction(BaseModel):
    action_type: str
    component_id: str
    previous_state: Optional[str] = None
    new_state: str
    description: str


class RecoveryPlanResponse(BaseModel):
    plan_id: str
    fault_id: str
    actions: List[RecoveryAction]
    restored_load: float
    cascade_risk: float
    max_line_loading: float
    switching_operations: int
    constraint_violations: List[str] = []
    feasible: bool
    objective_score: float
    status: str
    selected: bool = False


class RecoveryExecuteRequest(BaseModel):
    plan_id: str
    fault_id: str
    auto_verify: bool = True


class RecoveryResult(BaseModel):
    plan_id: str
    success: bool
    load_restored_pct: float
    grid_stable: bool
    remaining_violations: List[str] = []
    post_recovery_state: Dict[str, Any] = {}
    verification_passed: bool = False
    message: str = ""


# ---- Grid State Schemas ----
class GridStateResponse(BaseModel):
    overall_status: str
    total_generation: float
    total_load: float
    total_demand: float
    active_faults: int
    cascade_risk: float
    components_at_risk: int
    restored_load_pct: float
    frequency: float
    timestamp: datetime
    components: Optional[List[GridComponentResponse]] = None


# ---- System Event Schemas ----
class SystemEventResponse(BaseModel):
    event_id: str
    event_type: str
    severity: str
    title: str
    description: Optional[str] = None
    component_id: Optional[str] = None
    created_at: datetime


# ---- Auth Schemas ----
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "VIEWER"


class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ---- WebSocket Event ----
class WSEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---- Analytics ----
class AnalyticsResponse(BaseModel):
    total_faults: int
    faults_by_type: Dict[str, int]
    avg_detection_latency_ms: float
    avg_recovery_time_s: float
    avg_load_restored_pct: float
    false_positive_rate: float
    false_negative_rate: float
    cascade_prevention_rate: float
    most_vulnerable_components: List[Dict[str, Any]]
    recovery_success_rate: float
