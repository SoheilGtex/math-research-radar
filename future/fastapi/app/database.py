import os
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

# Points to radar_db in Docker network, or localhost for local testing
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://radar_user:secure_password@localhost:5432/math_radar"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Paper(Base):
    """SQLAlchemy model for the API bounded context."""
    __tablename__ = "papers"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    published = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    link = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def get_db():
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()