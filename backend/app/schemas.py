from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class MissionStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class DroneStatus(str, Enum):
    idle = "idle"
    flying = "flying"
    landing = "landing"
    maintenance = "maintenance"
    error = "error"

class Priority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    emergency = "emergency"

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str = "operator"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Drone Schemas
class DroneBase(BaseModel):
    drone_id: str
    name: str
    model: str
    status: str = "idle"
    firmware_version: str

class DroneCreate(DroneBase):
    pass

class DroneUpdate(BaseModel):
    status: Optional[str] = None
    battery_level: Optional[float] = None
    hardware_status: Optional[str] = None

class DroneResponse(DroneBase):
    id: int
    battery_level: float
    hardware_status: str
    last_seen: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Mission Schemas
class MissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lon: float = Field(..., ge=-180, le=180)
    origin_name: str
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lon: float = Field(..., ge=-180, le=180)
    dest_name: str
    payload_weight: float = Field(..., gt=0, le=2)
    payload_description: str
    priority: str = "normal"

class MissionCreate(MissionBase):
    drone_id: int

class MissionUpdate(BaseModel):
    status: Optional[str] = None
    delivery_proof_image: Optional[str] = None
    delivery_confirmation_code: Optional[str] = None

class MissionResponse(MissionBase):
    id: int
    mission_id: str
    drone_id: int
    operator_id: int
    status: str
    estimated_duration: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivery_proof_image: Optional[str] = None
    delivery_confirmation_code: Optional[str] = None
    payload_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Telemetry Schemas
class TelemetryBase(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    heading: float
    speed: float
    battery_voltage: float
    battery_current: float
    battery_percent: float
    flight_mode: str
    is_armed: bool
    is_airborne: bool
    satellites: int
    gps_fix: int

class TelemetryCreate(TelemetryBase):
    drone_id: int
    mission_id: Optional[int] = None
    temperature: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None

class TelemetryResponse(TelemetryBase):
    id: int
    drone_id: int
    mission_id: Optional[int]
    timestamp: datetime
    temperature: Optional[float]
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    
    class Config:
        from_attributes = True

# Dashboard Statistics
class DashboardStats(BaseModel):
    total_missions: int
    active_missions: int
    completed_missions: int
    active_drones: int
    total_flight_hours: float
    avg_delivery_time: Optional[float] = None
