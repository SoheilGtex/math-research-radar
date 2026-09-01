import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Fallback to local host if DATABASE_URL is not provided (useful for local testing)
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://radar_user:secure_password@localhost:5432/math_radar"
)

try:
    # Create the SQLAlchemy engine
    engine = create_engine(DATABASE_URL, echo=False)
    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except SQLAlchemyError as e:
    logger.error(f"Failed to initialize database engine: {e}")
    raise

# Create a Base class for our models to inherit from
Base = declarative_base()

def get_db():
    """Dependency generator for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()