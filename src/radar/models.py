from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from radar.db import Base


class Paper(Base):
    """
    Unified Domain Model for research papers, mapped to the 'papers' table in PostgreSQL.
    """
    __tablename__ = "papers"

    # Primary key ensures we never have duplicate IDs at the database level
    id = Column(String, primary_key=True, index=True)
    
    title = Column(String, nullable=False)
    published = Column(String, nullable=False)  # Kept as string for broad compatibility across APIs
    summary = Column(Text, nullable=True)
    link = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    
    # Audit timestamps managed automatically by the database
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self) -> dict:
        """Convert the SQLAlchemy model instance to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "published": self.published,
            "summary": self.summary,
            "link": self.link,
            "category": self.category,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }