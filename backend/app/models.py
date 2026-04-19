from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="operator")  # operator, admin, viewer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    missions = relationship("Mission", back_populates="operator")

class Drone(Base):
    __tablename__ = "drones"
    
    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(String, unique=True, index=True)  # e.g., "DRONE-001"
    name = Column(String)
    model = Column(String)
    status = Column(String, default="idle")  # idle, flying, landing, maintenance, error
    battery_level = Column(Float, default=100.0)
    firmware_version = Column(String)
    hardware_status = Column(String, default="ok")
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    missions = relationship("Mission", back_populates="drone")
    telemetry = relationship("Telemetry", back_populates="drone")

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(Text)
    
    drone_id = Column(Integer, ForeignKey("drones.id"))
    operator_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(String, default="pending")  # pending, in_progress, completed, failed, cancelled
    
    # Origin coordinates
    origin_lat = Column(Float)
    origin_lon = Column(Float)
    origin_name = Column(String)
    
    # Destination coordinates
    dest_lat = Column(Float)
    dest_lon = Column(Float)
    dest_name = Column(String)
    
    # Mission details
    payload_weight = Column(Float)  # in kg
    payload_description = Column(Text)
    priority = Column(String, default="normal")  # low, normal, high, emergency
    
    # Timing
    estimated_duration = Column(Integer)  # in minutes
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Delivery proof
    delivery_proof_image = Column(String, nullable=True)
    delivery_confirmation_code = Column(String, nullable=True)
    
    # Temperature tracking for cold-chain compliance
    payload_temperature = Column(Float, nullable=True)  # Celsius
    min_temperature = Column(Float, nullable=True)  # Minimum safe temperature
    max_temperature = Column(Float, nullable=True)  # Maximum safe temperature
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    drone = relationship("Drone", back_populates="missions")
    operator = relationship("User", back_populates="missions")
    telemetry = relationship("Telemetry", back_populates="mission")

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(Integer, ForeignKey("drones.id"))
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    
    # Position
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)  # in meters AGL
    heading = Column(Float)  # 0-360 degrees
    
    # Flight status
    speed = Column(Float)  # m/s
    battery_voltage = Column(Float)
    battery_current = Column(Float)
    battery_percent = Column(Float)
    
    # System health
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    temperature = Column(Float)  # celsius
    
    # Flight mode
    flight_mode = Column(String)  # MANUAL, GUIDED, RTL, AUTO, etc.
    
    # Additional data
    gps_fix = Column(Integer)
    satellites = Column(Integer)
    is_armed = Column(Boolean, default=False)
    is_airborne = Column(Boolean, default=False)
    
    # Raw MAVLink data
    mavlink_data = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    drone = relationship("Drone", back_populates="telemetry")
    mission = relationship("Mission", back_populates="telemetry")

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    action = Column(String)  # dispatched, in_transit, delivered, failed
    location_lat = Column(Float)
    location_lon = Column(Float)
    altitude = Column(Float)
    notes = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    mission = relationship("Mission")
