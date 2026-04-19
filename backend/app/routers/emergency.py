from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/api/emergency", tags=["emergency"])

@router.post("/dispatch", response_model=schemas.MissionResponse, status_code=201)
async def emergency_dispatch(
    mission: schemas.MissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Emergency SOS dispatch - Rapid medical delivery"""
    # Force emergency priority
    mission_dict = mission.dict()
    mission_dict['priority'] = 'emergency'
    
    # Find available drone with highest battery
    available_drones = db.query(models.Drone).filter(
        models.Drone.status.in_(["idle", "available"]),
        models.Drone.battery_level > 50
    ).order_by(models.Drone.battery_level.desc()).all()
    
    if not available_drones:
        raise HTTPException(status_code=503, detail="No available drones for emergency dispatch")
    
    drone = available_drones[0]
    
    # Create mission with emergency override
    mission_obj = models.Mission(
        mission_id=f"EMERGENCY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        operator_id=current_user.id,
        drone_id=drone.id,
        **mission_dict
    )
    
    db.add(mission_obj)
    drone.status = "flying"
    
    db.commit()
    db.refresh(mission_obj)
    
    # Log emergency dispatch
    emergency_log = models.DeliveryLog(
        mission_id=mission_obj.id,
        action="emergency_dispatch",
        details="Emergency SOS dispatch activated"
    )
    db.add(emergency_log)
    db.commit()
    
    return mission_obj

@router.get("/active")
async def get_active_emergencies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all active emergency missions"""
    emergency_missions = db.query(models.Mission).filter(
        models.Mission.status.in_(["pending", "in_progress"]),
        models.Mission.priority == "emergency"
    ).all()
    return emergency_missions
