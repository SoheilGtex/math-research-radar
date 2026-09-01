import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def save_papers(papers: List[Paper]) -> None:
    """Save or update novel papers to the PostgreSQL database using an upsert strategy."""
    if not papers:
        return

    db = SessionLocal()
    try:
        for paper in papers:
            # db.merge performs an upsert: it inserts if the ID is new, or updates if it exists.
            db.merge(paper)
        
        db.commit()
        logger.info(f"Successfully committed {len(papers)} papers to PostgreSQL.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to commit papers to database: {e}")
    finally:
        db.close()