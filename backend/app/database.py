from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# If no PostgreSQL DATABASE_URL is set, use SQLite as fallback
if not DATABASE_URL:
    # Use absolute path to backend directory
    import os
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(backend_dir, "..", "drone_medical.db")
    DATABASE_URL = f"sqlite:///{os.path.abspath(db_path)}"
    print(f"⚠️  Using SQLite database: {os.path.abspath(db_path)}")
else:
    print("✅ Using PostgreSQL database")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
