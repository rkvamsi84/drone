"""
Database setup script to initialize the database with initial data
"""
from app.database import engine, SessionLocal
from app import models
from app import auth
import sys

def init_db():
    """Initialize database with tables and initial data"""
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            print("Creating admin user...")
            admin_password = "password"
            hashed_password = auth.get_password_hash(admin_password)
            
            admin = models.User(
                username="admin",
                email="admin@dronemed.com",
                hashed_password=hashed_password,
                full_name="System Administrator",
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"✓ Admin user created (username: admin, password: {admin_password})")
        
        # Create sample drone
        drone = db.query(models.Drone).filter(models.Drone.drone_id == "DRONE-001").first()
        if not drone:
            print("Creating sample drone...")
            drone = models.Drone(
                drone_id="DRONE-001",
                name="Himalayan Medical Drone 1",
                model="VTOL Hybrid Long Range",
                status="idle",
                battery_level=100.0,
                firmware_version="1.0.0",
                hardware_status="ok"
            )
            db.add(drone)
            db.commit()
            print("✓ Sample drone created")
        
        print("\n✓ Database initialization complete!")
        print("\nDefault credentials:")
        print("  Username: admin")
        print("  Password: password")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
