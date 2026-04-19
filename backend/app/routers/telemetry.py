from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from .. import models, schemas, auth
from ..services.drone_simulator import drone_simulators
from ..services.mqtt_service import mqtt_service
import json

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])

@router.get("/drones/{drone_id}", response_model=List[schemas.TelemetryResponse])
async def get_drone_telemetry(
    drone_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get telemetry history for a specific drone"""
    telemetry = db.query(models.Telemetry).filter(
        models.Telemetry.drone_id == drone_id
    ).order_by(models.Telemetry.timestamp.desc()).limit(limit).all()
    return telemetry

@router.get("/drones/{drone_id}/latest", response_model=schemas.TelemetryResponse)
async def get_latest_telemetry(
    drone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get latest telemetry for a drone"""
    telemetry = db.query(models.Telemetry).filter(
        models.Telemetry.drone_id == drone_id
    ).order_by(models.Telemetry.timestamp.desc()).first()
    
    if not telemetry:
        raise HTTPException(status_code=404, detail="No telemetry data found")
    
    return telemetry

@router.get("/missions/{mission_id}", response_model=List[schemas.TelemetryResponse])
async def get_mission_telemetry(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get telemetry for a specific mission"""
    telemetry = db.query(models.Telemetry).filter(
        models.Telemetry.mission_id == mission_id
    ).order_by(models.Telemetry.timestamp.asc()).all()
    return telemetry

@router.post("/drones/{drone_id}/simulate")
async def simulate_telemetry(
    drone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Generate simulated telemetry for testing"""
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    # Get or create mock drone
    mock_drone = drone_simulators.get(drone.drone_id)
    if not mock_drone:
        raise HTTPException(status_code=404, detail="Drone simulator not found")
    
    # Get telemetry from simulator
    telemetry_data = mock_drone.calculate_telemetry()
    
    # Create database entry
    db_telemetry = models.Telemetry(
        drone_id=drone.id,
        latitude=telemetry_data["latitude"],
        longitude=telemetry_data["longitude"],
        altitude=telemetry_data["altitude"],
        heading=telemetry_data["heading"],
        speed=telemetry_data["speed"],
        battery_voltage=telemetry_data["battery_voltage"],
        battery_current=telemetry_data["battery_current"],
        battery_percent=telemetry_data["battery_percent"],
        flight_mode=telemetry_data["flight_mode"],
        is_armed=telemetry_data["is_armed"],
        is_airborne=telemetry_data["is_airborne"],
        satellites=telemetry_data["satellites"],
        gps_fix=telemetry_data["gps_fix"],
        cpu_usage=telemetry_data.get("cpu_usage", 0),
        memory_usage=telemetry_data.get("memory_usage", 0),
        temperature=telemetry_data.get("temperature", 25),
        mavlink_data=telemetry_data
    )
    
    db.add(db_telemetry)
    
    # Update drone status
    drone.battery_level = telemetry_data["battery_percent"]
    drone.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(db_telemetry)
    
    return db_telemetry
