from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/api/replay", tags=["replay"])

@router.get("/mission/{mission_id}", response_model=List[schemas.TelemetryResponse])
async def replay_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all telemetry data for flight replay"""
    # Verify mission exists
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Get all telemetry points ordered by time
    telemetry = db.query(models.Telemetry).filter(
        models.Telemetry.mission_id == mission_id
    ).order_by(models.Telemetry.timestamp.asc()).all()
    
    return telemetry

@router.get("/incidents")
async def get_incidents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all failed missions or error incidents for review"""
    incidents = db.query(models.Mission).filter(
        models.Mission.status.in_(["failed", "cancelled"])
    ).order_by(models.Mission.created_at.desc()).offset(skip).limit(limit).all()
    
    return incidents
