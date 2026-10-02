"""
Pydantic Schemas for API Validation - Permissive Serialization
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: Optional[str] = "VIEWER"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: Optional[int] = 1
    is_active: Optional[bool] = True
    created_at: Optional[Any] = None

    class Config:
        from_attributes = True
        extra = "ignore"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Sensor Schemas
class SensorReadingBase(BaseModel):
    sensor_id: str
    component_id: Optional[str] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    frequency: Optional[float] = None
    active_power: Optional[float] = None
    reactive_power: Optional[float] = None
    temperature: Optional[float] = None
    power_factor: Optional[float] = None
    load_percentage: Optional[float] = None
    breaker_status: Optional[str] = "ON"
    line_status: Optional[str] = "NORMAL"
    status: Optional[str] = "NORMAL"


class SensorReadingCreate(SensorReadingBase):
    timestamp: Optional[Any] = None


# Fault Schemas
class FaultInjectionRequest(BaseModel):
    component_id: str = "LINE_7"
    fault_type: str = "TRANSMISSION_LINE_FAILURE"
    severity: float = Field(0.85, ge=0.0, le=1.0)
    duration: Optional[float] = 60.0


class FaultEventResponse(BaseModel):
    id: Optional[int] = None
    fault_id: str
    component_id: str
    fault_type: str
    severity: Optional[float] = 0.0
    confidence: Optional[float] = 0.0
    cascade_risk: Optional[float] = 0.0
    status: Optional[str] = "DETECTED"
    start_time: Optional[Any] = None
    end_time: Optional[Any] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        extra = "ignore"


# Recovery Schemas
class RecoveryPlanResponse(BaseModel):
    id: Optional[int] = None
    plan_id: str
    fault_id: str
    actions: Optional[List[Any]] = []
    restored_load: Optional[float] = None
    cascade_risk: Optional[float] = None
    max_line_loading: Optional[float] = None
    constraint_violations: Optional[List[Any]] = []
    feasible: Optional[bool] = True
    objective_score: Optional[float] = None
    selected: Optional[bool] = False
    created_at: Optional[Any] = None

    class Config:
        from_attributes = True
        extra = "ignore"


class RecoveryExecuteRequest(BaseModel):
    plan_id: str
