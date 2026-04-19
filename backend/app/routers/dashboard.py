from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get dashboard statistics"""
    # Total missions
    total_missions = db.query(models.Mission).count()
    
    # Active missions
    active_missions = db.query(models.Mission).filter(
        models.Mission.status.in_(["pending", "in_progress"])
    ).count()
    
    # Completed missions
    completed_missions = db.query(models.Mission).filter(
        models.Mission.status == "completed"
    ).count()
    
    # Active drones
    active_drones = db.query(models.Drone).filter(
        models.Drone.status.in_(["flying", "landing"])
    ).count()
    
    # Calculate total flight hours
    flight_times = db.query(models.Mission).filter(
        models.Mission.status == "completed",
        models.Mission.started_at.isnot(None),
        models.Mission.completed_at.isnot(None)
    ).all()
    
    total_minutes = 0
    for mission in flight_times:
        if mission.started_at and mission.completed_at:
            duration = mission.completed_at - mission.started_at
            total_minutes += duration.total_seconds() / 60
    
    total_flight_hours = round(total_minutes / 60, 2)
    
    # Average delivery time
    completed = db.query(models.Mission).filter(
        models.Mission.status == "completed",
        models.Mission.estimated_duration.isnot(None)
    ).all()
    
    avg_delivery_time = None
    if completed:
        avg_minutes = sum(m.estimated_duration for m in completed) / len(completed)
        avg_delivery_time = round(avg_minutes, 1)
    
    return schemas.DashboardStats(
        total_missions=total_missions,
        active_missions=active_missions,
        completed_missions=completed_missions,
        active_drones=active_drones,
        total_flight_hours=total_flight_hours,
        avg_delivery_time=avg_delivery_time
    )

@router.get("/recent-missions")
async def get_recent_missions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get recent missions"""
    missions = db.query(models.Mission).order_by(
        models.Mission.created_at.desc()
    ).limit(limit).all()
    return missions
