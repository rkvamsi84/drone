from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas, auth
from ..services.drone_simulator import get_or_create_drone
import uuid
from geopy.distance import geodesic

router = APIRouter(prefix="/api/missions", tags=["missions"])

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in kilometers"""
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def estimate_duration(distance_km):
    """Estimate mission duration in minutes based on distance"""
    # Assume average speed of 40 km/h for drones
    time_hours = distance_km / 40
    return int(time_hours * 60) + 5  # Add 5 min buffer for takeoff/landing

@router.get("", response_model=List[schemas.MissionResponse])
async def get_missions(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all missions with optional status filter"""
    query = db.query(models.Mission)
    if status:
        query = query.filter(models.Mission.status == status)
    missions = query.order_by(models.Mission.created_at.desc()).offset(skip).limit(limit).all()
    return missions

@router.post("", response_model=schemas.MissionResponse, status_code=201)
async def create_mission(
    mission: schemas.MissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new mission"""
    # Verify drone exists and is available
    drone = db.query(models.Drone).filter(models.Drone.id == mission.drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    if drone.status not in ["idle", "available"]:
        raise HTTPException(status_code=400, detail="Drone is not available")
    
    # Calculate estimated duration
    distance = calculate_distance(
        mission.origin_lat, mission.origin_lon,
        mission.dest_lat, mission.dest_lon
    )
    estimated_duration = estimate_duration(distance)
    
    # Create mission
    mission_id = f"MISSION-{uuid.uuid4().hex[:8].upper()}"
    db_mission = models.Mission(
        mission_id=mission_id,
        operator_id=current_user.id,
        **mission.dict(),
        estimated_duration=estimated_duration
    )
    db.add(db_mission)
    
    # Update drone status
    drone.status = "flying"
    drone.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(db_mission)
    
    # Send mission to mock drone simulator
    mock_drone = get_or_create_drone(drone.drone_id, drone.name)
    mock_drone.set_mission({
        "origin_lat": mission.origin_lat,
        "origin_lon": mission.origin_lon,
        "dest_lat": mission.dest_lat,
        "dest_lon": mission.dest_lon,
        "mission_id": mission_id
    })
    mock_drone.is_armed = True
    mock_drone.is_airborne = True
    mock_drone.flight_mode = "AUTO"
    
    return db_mission

@router.get("/{mission_id}", response_model=schemas.MissionResponse)
async def get_mission(mission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get a specific mission"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.put("/{mission_id}", response_model=schemas.MissionResponse)
async def update_mission(
    mission_id: int,
    mission_update: schemas.MissionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update mission status"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    for key, value in mission_update.dict(exclude_unset=True).items():
        setattr(mission, key, value)
    
    # If mission completed, reset drone status
    if mission.status == "completed":
        drone = db.query(models.Drone).filter(models.Drone.id == mission.drone_id).first()
        if drone:
            drone.status = "idle"
        
        mission.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mission)
    return mission

@router.delete("/{mission_id}")
async def delete_mission(mission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Delete a mission"""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    db.delete(mission)
    db.commit()
    return {"message": "Mission deleted successfully"}
