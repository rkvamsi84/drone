"""
Seed database with comprehensive mock data for all features
"""
from app.database import engine, SessionLocal
from app import models
from app import auth
from datetime import datetime, timedelta
import random

def seed_mock_data():
    """Seed database with mock data"""
    print("🌱 Seeding database with mock data...")
    
    db = SessionLocal()
    
    try:
        # Get admin user
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            print("❌ Admin user not found. Run setup_db.py first.")
            return
        
        print("✓ Found admin user")
        
        # Create additional users
        users_data = [
            {"username": "operator1", "email": "operator1@dronemed.com", "full_name": "Dr. Sarah Johnson", "role": "operator"},
            {"username": "operator2", "email": "operator2@dronemed.com", "full_name": "Rajesh Kumar", "role": "operator"},
            {"username": "viewer1", "email": "viewer1@dronemed.com", "full_name": "Dr. Emily Chen", "role": "viewer"},
        ]
        
        users = [admin]
        for user_data in users_data:
            existing = db.query(models.User).filter(models.User.username == user_data["username"]).first()
            if not existing:
                hashed_password = auth.get_password_hash("password123")
                user = models.User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                users.append(user)
                print(f"✓ Created user: {user_data['username']}")
            else:
                users.append(existing)
        
        # Create multiple drones
        drones_data = [
            {"drone_id": "DRONE-001", "name": "Himalayan Courier 1", "model": "VTOL Hybrid Long Range", "lat": 28.6139, "lon": 77.2090},
            {"drone_id": "DRONE-002", "name": "Himalayan Courier 2", "model": "VTOL Hybrid Long Range", "lat": 28.7041, "lon": 77.1025},
            {"drone_id": "DRONE-003", "name": "Himalayan Courier 3", "model": "VTOL Hybrid Long Range", "lat": 28.6139, "lon": 77.0090},
        ]
        
        drones = []
        for drone_data in drones_data:
            existing = db.query(models.Drone).filter(models.Drone.drone_id == drone_data["drone_id"]).first()
            if not existing:
                drone = models.Drone(
                    drone_id=drone_data["drone_id"],
                    name=drone_data["name"],
                    model=drone_data["model"],
                    status=random.choice(["idle", "idle", "idle", "flying"]),
                    battery_level=random.uniform(45, 100),
                    firmware_version="1.2.0",
                    hardware_status="ok",
                    last_seen=datetime.utcnow()
                )
                db.add(drone)
                db.commit()
                db.refresh(drone)
                drones.append(drone)
                print(f"✓ Created drone: {drone_data['drone_id']}")
            else:
                existing.lat = drone_data["lat"]
                existing.lon = drone_data["lon"]
                drones.append(existing)
        
        # Create missions with various statuses
        missions_data = [
            {
                "name": "Emergency Medicine Delivery - Village A",
                "description": "Critical insulin supply to remote mountain village",
                "origin_lat": 28.6139, "origin_lon": 77.2090, "origin_name": "Base Hospital Delhi",
                "dest_lat": 28.7041, "dest_lon": 77.1025, "dest_name": "Remote PHC Gangtok",
                "payload_weight": 1.2, "payload_description": "Insulin vials, syringes, glucose meters",
                "priority": "emergency", "status": "completed",
                "days_ago": 1
            },
            {
                "name": "Blood Sample Transport",
                "description": "Urgent blood samples for COVID testing",
                "origin_lat": 28.7041, "origin_lon": 77.1025, "origin_name": "PHC Gangtok",
                "dest_lat": 28.6139, "dest_lon": 77.2090, "dest_name": "Central Lab Delhi",
                "payload_weight": 0.8, "payload_description": "Blood samples in coolers",
                "priority": "high", "status": "in_progress",
                "days_ago": 0
            },
            {
                "name": "Vaccine Distribution - Week 2",
                "description": "Routine vaccine supply to rural centers",
                "origin_lat": 28.6139, "origin_lon": 77.0090, "origin_name": "Supply Depot",
                "dest_lat": 28.7041, "dest_lon": 77.1025, "dest_name": "Village Health Center",
                "payload_weight": 1.5, "payload_description": "COVID vaccines, cold chain boxes",
                "priority": "normal", "status": "pending",
                "days_ago": 0
            },
            {
                "name": "Medical Equipment Repair Parts",
                "description": "Urgent spare parts for X-ray machine",
                "origin_lat": 28.6139, "origin_lon": 77.2090, "origin_name": "Equipment Warehouse",
                "dest_lat": 28.9000, "dest_lon": 77.3000, "dest_name": "District Hospital",
                "payload_weight": 0.5, "payload_description": "Electronic components, connectors",
                "priority": "high", "status": "completed",
                "days_ago": 3
            },
            {
                "name": "Medicine Stock Replenishment",
                "description": "Monthly medicine supply to hill stations",
                "origin_lat": 28.6139, "origin_lon": 77.2090, "origin_name": "Central Pharmacy",
                "dest_lat": 28.7041, "dest_lon": 77.1025, "dest_name": "Hill Station Clinic",
                "payload_weight": 1.8, "payload_description": "Antibiotics, pain relievers, bandages",
                "priority": "normal", "status": "completed",
                "days_ago": 5
            },
            {
                "name": "Emergency Oxygen Supply",
                "description": "Critical oxygen cylinders for COVID ward",
                "origin_lat": 28.6139, "origin_lon": 77.2090, "origin_name": "Gas Supplier",
                "dest_lat": 28.7041, "dest_lon": 77.1025, "dest_name": "Emergency Hospital",
                "payload_weight": 1.5, "payload_description": "Oxygen cylinders (2 units)",
                "priority": "emergency", "status": "failed",
                "days_ago": 2
            },
        ]
        
        for i, mission_data in enumerate(missions_data):
            mission_id = f"MISSION-{1000 + i:04d}"
            created_at = datetime.utcnow() - timedelta(days=mission_data["days_ago"])
            
            # Calculate estimated duration
            from geopy.distance import geodesic
            distance = geodesic(
                (mission_data["origin_lat"], mission_data["origin_lon"]),
                (mission_data["dest_lat"], mission_data["dest_lon"])
            ).kilometers
            estimated_duration = int((distance / 40) * 60) + 5  # 40 km/h average
            
            mission = models.Mission(
                mission_id=mission_id,
                name=mission_data["name"],
                description=mission_data["description"],
                drone_id=drones[i % len(drones)].id,
                operator_id=admin.id,
                status=mission_data["status"],
                origin_lat=mission_data["origin_lat"],
                origin_lon=mission_data["origin_lon"],
                origin_name=mission_data["origin_name"],
                dest_lat=mission_data["dest_lat"],
                dest_lon=mission_data["dest_lon"],
                dest_name=mission_data["dest_name"],
                payload_weight=mission_data["payload_weight"],
                payload_description=mission_data["payload_description"],
                priority=mission_data["priority"],
                estimated_duration=estimated_duration,
                created_at=created_at
            )
            
            # Add start/completion times for completed/in_progress missions
            if mission_data["status"] in ["completed", "in_progress"]:
                mission.started_at = created_at + timedelta(minutes=5)
            
            if mission_data["status"] == "completed":
                mission.completed_at = mission.started_at + timedelta(minutes=estimated_duration)
                mission.delivery_confirmation_code = f"DC-{random.randint(1000, 9999)}"
            
            if mission_data["status"] == "failed":
                mission.started_at = created_at + timedelta(minutes=5)
                mission.completed_at = mission.started_at + timedelta(minutes=10)
            
            db.add(mission)
        
        db.commit()
        print(f"✓ Created {len(missions_data)} missions")
        
        # Create telemetry data for missions
        for mission in db.query(models.Mission).filter(models.Mission.status.in_(["completed", "in_progress", "failed"])).all():
            if not mission.started_at:
                continue
                
            drone = mission.drone
            total_points = 20
            
            # Generate path from origin to destination
            for i in range(total_points):
                progress = i / (total_points - 1)
                lat = mission.origin_lat + (mission.dest_lat - mission.origin_lat) * progress
                lon = mission.origin_lon + (mission.dest_lon - mission.origin_lon) * progress
                
                # Add some randomness to path
                lat += random.uniform(-0.002, 0.002)
                lon += random.uniform(-0.002, 0.002)
                
                timestamp = mission.started_at + timedelta(
                    seconds=(i * (mission.estimated_duration * 60 / total_points))
                )
                
                # Only create telemetry if within mission time
                if mission.completed_at and timestamp > mission.completed_at:
                    break
                
                telemetry = models.Telemetry(
                    drone_id=drone.id,
                    mission_id=mission.id,
                    latitude=lat,
                    longitude=lon,
                    altitude=50 if i > 5 else (i * 10),
                    heading=random.uniform(0, 360),
                    speed=12.0 if i > 2 else (i * 2),
                    battery_voltage=11.5 - (progress * 0.5),
                    battery_current=random.uniform(20, 30),
                    battery_percent=95 - (progress * 15),
                    cpu_usage=random.uniform(30, 50),
                    memory_usage=random.uniform(40, 60),
                    temperature=random.uniform(25, 35),
                    flight_mode="AUTO",
                    is_armed=True,
                    is_airborne=i > 3,
                    satellites=random.randint(8, 12),
                    gps_fix=3,
                    timestamp=timestamp
                )
                db.add(telemetry)
        
        db.commit()
        print("✓ Created telemetry data for missions")
        
        # Create delivery logs
        for mission in db.query(models.Mission).filter(models.Mission.status.in_(["completed", "in_progress"])).all():
            if not mission.started_at:
                continue
            
            # Dispatch log
            dispatch_log = models.DeliveryLog(
                mission_id=mission.id,
                action="dispatched",
                location_lat=mission.origin_lat,
                location_lon=mission.origin_lon,
                altitude=0,
                notes=f"Mission {mission.mission_id} dispatched from {mission.origin_name}",
                timestamp=mission.started_at
            )
            db.add(dispatch_log)
            
            # In-transit log
            mid_lat = (mission.origin_lat + mission.dest_lat) / 2
            mid_lon = (mission.origin_lon + mission.dest_lon) / 2
            transit_time = mission.started_at + timedelta(minutes=mission.estimated_duration / 2)
            
            transit_log = models.DeliveryLog(
                mission_id=mission.id,
                action="in_transit",
                location_lat=mid_lat,
                location_lon=mid_lon,
                altitude=50,
                notes=f"Drone en-route to {mission.dest_name}",
                timestamp=transit_time
            )
            db.add(transit_log)
            
            # Delivery log for completed missions
            if mission.status == "completed" and mission.completed_at:
                delivered_log = models.DeliveryLog(
                    mission_id=mission.id,
                    action="delivered",
                    location_lat=mission.dest_lat,
                    location_lon=mission.dest_lon,
                    altitude=0,
                    notes=f"Package successfully delivered to {mission.dest_name}. Confirmation: {mission.delivery_confirmation_code}",
                    timestamp=mission.completed_at
                )
                db.add(delivered_log)
        
        db.commit()
        print("✓ Created delivery logs")
        
        print("\n" + "="*60)
        print("🎉 Mock data seeding complete!")
        print("="*60)
        print("\nSummary:")
        print(f"  📋 Users: {len(users)}")
        print(f"  🚁 Drones: {len(drones)}")
        print(f"  📦 Missions: {len(missions_data)}")
        print(f"  📊 Telemetry points: {db.query(models.Telemetry).count()}")
        print(f"  📝 Delivery logs: {db.query(models.DeliveryLog).count()}")
        print("\n✅ All features are now populated with realistic data!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_mock_data()
