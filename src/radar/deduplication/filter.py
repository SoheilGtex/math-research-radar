import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError

from radar.models import Paper
from radar.db import SessionLocal

logger = logging.getLogger(__name__)

def filter_new_papers(papers: List[Paper]) -> List[Paper]:
    """
    Filter out papers that have already been stored in the PostgreSQL database.
    This replaces the legacy file-based 'seen_ids.json' cache.
    """
    if not papers:
        return []

    # Extract all incoming paper IDs
    incoming_ids = [paper.id for paper in papers]
    
    db = SessionLocal()
    try:
        # Query the database for IDs that already exist among the incoming IDs
        # Using with_entities to only fetch the primary key for performance
        existing_records = db.query(Paper.id).filter(Paper.id.in_(incoming_ids)).all()
        # Flatten the result list of tuples into a simple set
        existing_ids = {record[0] for record in existing_records}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during deduplication: {e}")
        # Fail safe: if DB fails, assume none exist to avoid losing data 
        # (the db.merge in storage layer will handle conflicts anyway)
        existing_ids = set()
    finally:
        db.close()

    # Filter out papers whose ID is already in the database
    new_papers = [paper for paper in papers if paper.id not in existing_ids]

    logger.info(f"Deduplication complete: found {len(new_papers)} novel papers out of {len(papers)}.")
    
    return new_papers