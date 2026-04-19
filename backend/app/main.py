from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth, drones, missions, telemetry, dashboard, emergency, replay, video
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Drone Medical Delivery System",
    description="Autonomous drone-based medical supply delivery system",
    version="1.0.0"
)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3001,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(drones.router)
app.include_router(missions.router)
app.include_router(telemetry.router)
app.include_router(dashboard.router)
app.include_router(emergency.router)
app.include_router(replay.router)
app.include_router(video.router)

@app.get("/")
async def root():
    return {
        "message": "Drone Medical Delivery System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
