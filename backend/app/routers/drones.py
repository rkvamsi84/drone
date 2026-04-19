from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, auth
from ..services.drone_simulator import get_or_create_drone

router = APIRouter(prefix="/api/drones", tags=["drones"])

@router.get("", response_model=List[schemas.DroneResponse])
async def get_drones(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get all drones"""
    drones = db.query(models.Drone).all()
    return drones

@router.post("", response_model=schemas.DroneResponse, status_code=201)
async def create_drone(drone: schemas.DroneCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Create a new drone"""
    # Check if drone_id already exists
    existing = db.query(models.Drone).filter(models.Drone.drone_id == drone.drone_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Drone ID already exists")
    
    db_drone = models.Drone(**drone.dict())
    db.add(db_drone)
    db.commit()
    db.refresh(db_drone)
    
    # Create mock drone simulator
    get_or_create_drone(drone.drone_id, drone.name)
    
    return db_drone

@router.get("/{drone_id}", response_model=schemas.DroneResponse)
async def get_drone(drone_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get a specific drone"""
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone

@router.put("/{drone_id}", response_model=schemas.DroneResponse)
async def update_drone(drone_id: int, drone_update: schemas.DroneUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Update drone information"""
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    for key, value in drone_update.dict(exclude_unset=True).items():
        setattr(drone, key, value)
    
    db.commit()
    db.refresh(drone)
    return drone

@router.delete("/{drone_id}")
async def delete_drone(drone_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Delete a drone"""
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    db.delete(drone)
    db.commit()
    return {"message": "Drone deleted successfully"}
