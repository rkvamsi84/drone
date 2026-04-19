import asyncio
import random
import math
from datetime import datetime
from typing import Optional, Tuple

class MockDrone:
    def __init__(self, drone_id: str, name: str):
        self.drone_id = drone_id
        self.name = name
        self.running = False
        self.current_mission = None
        
        # Position
        self.lat = 28.6139  # Default to Delhi coordinates
        self.lon = 77.2090
        self.altitude = 0
        self.heading = 0
        
        # Flight status
        self.is_armed = False
        self.is_airborne = False
        self.flight_mode = "MANUAL"
        self.speed = 0
        
        # Battery
        self.battery_percent = 100.0
        self.battery_voltage = 11.1
        self.battery_current = 0
        
        # System
        self.cpu_usage = random.uniform(20, 50)
        self.memory_usage = random.uniform(30, 60)
        self.temperature = random.uniform(25, 35)
        
        # GPS
        self.satellites = random.randint(8, 12)
        self.gps_fix = 3
        
        # Mission tracking
        self.waypoint_index = 0
        self.mission_start_time = None
    
    def start(self):
        """Start the drone simulator"""
        self.running = True
        asyncio.create_task(self._simulation_loop())
    
    def stop(self):
        """Stop the simulator"""
        self.running = False
    
    def set_mission(self, mission):
        """Set a mission for the drone"""
        self.current_mission = mission
        self.waypoint_index = 0
        self.mission_start_time = datetime.utcnow()
    
    def get_current_position(self) -> Tuple[float, float, float]:
        """Get current position (lat, lon, altitude)"""
        return self.lat, self.lon, self.altitude
    
    def calculate_telemetry(self) -> dict:
        """Calculate and return current telemetry data"""
        # Simulate movement if flying
        if self.is_airborne and self.current_mission:
            self._update_position()
        
        # Simulate battery drain
        if self.is_airborne:
            self.battery_percent = max(0, self.battery_percent - random.uniform(0.01, 0.03))
            self.battery_voltage = 10.5 + (self.battery_percent / 100) * 2
            self.battery_current = random.uniform(15, 30)
        else:
            self.battery_current = random.uniform(0, 5)
        
        # Simulate system parameters
        self.cpu_usage = max(10, min(90, self.cpu_usage + random.uniform(-5, 5)))
        self.memory_usage = max(20, min(80, self.memory_usage + random.uniform(-2, 2)))
        self.temperature = max(20, min(50, self.temperature + random.uniform(-1, 1)))
        
        return {
            "latitude": self.lat,
            "longitude": self.lon,
            "altitude": self.altitude,
            "heading": self.heading,
            "speed": self.speed,
            "battery_voltage": round(self.battery_voltage, 2),
            "battery_current": round(self.battery_current, 2),
            "battery_percent": round(self.battery_percent, 1),
            "cpu_usage": round(self.cpu_usage, 1),
            "memory_usage": round(self.memory_usage, 1),
            "temperature": round(self.temperature, 1),
            "flight_mode": self.flight_mode,
            "is_armed": self.is_armed,
            "is_airborne": self.is_airborne,
            "satellites": self.satellites,
            "gps_fix": self.gps_fix,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _update_position(self):
        """Update drone position based on mission"""
        if not self.current_mission:
            return
        
        origin_lat = self.current_mission.get("origin_lat", self.lat)
        origin_lon = self.current_mission.get("origin_lon", self.lon)
        dest_lat = self.current_mission.get("dest_lat", self.lat)
        dest_lon = self.current_mission.get("dest_lon", self.lon)
        
        # Calculate distance and bearing
        lat_diff = dest_lat - self.lat
        lon_diff = dest_lon - self.lon
        
        # Simple linear interpolation
        distance = math.sqrt(lat_diff**2 + lon_diff**2)
        
        # Move towards destination
        if distance > 0.0001:  # ~11 meters
            # Calculate bearing
            self.heading = math.degrees(math.atan2(lon_diff, lat_diff))
            if self.heading < 0:
                self.heading += 360
            
            # Move at ~12 m/s (simulating ~43 km/h speed)
            step_size = 0.0001  # Roughly 11 meters per step
            self.lat += (lat_diff / distance) * step_size
            self.lon += (lon_diff / distance) * step_size
            
            # Maintain altitude
            if self.altitude < 50:
                self.altitude = min(50, self.altitude + 0.5)
            
            self.speed = 12.0
        else:
            # Reached destination
            self.speed = 0
            self.altitude = 0
            self.is_airborne = False
    
    async def _simulation_loop(self):
        """Main simulation loop"""
        while self.running:
            await asyncio.sleep(1)  # Update every second

# Global drone simulators
drone_simulators = {}

def get_or_create_drone(drone_id: str, name: str = None) -> MockDrone:
    """Get or create a mock drone"""
    if drone_id not in drone_simulators:
        drone_simulators[drone_id] = MockDrone(drone_id, name or f"Drone {drone_id}")
        drone_simulators[drone_id].start()
    return drone_simulators[drone_id]

def stop_drone(drone_id: str):
    """Stop a drone simulator"""
    if drone_id in drone_simulators:
        drone_simulators[drone_id].stop()
        del drone_simulators[drone_id]
