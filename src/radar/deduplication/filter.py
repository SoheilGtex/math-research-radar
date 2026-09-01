import logging
from typing import List

from sqlalchemy.exc import SQLAlchemyError

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def filter_new_papers(papers: List[Paper]) -> List[Paper]:
    """
    Filter out intra-batch duplicates and papers already stored in PostgreSQL.
    This replaces the legacy file-based 'seen_ids.json' cache.
    """
    if not papers:
        return []

    # 1. Intra-batch deduplication (keep the first occurrence of each ID)
    unique_incoming_dict = {}
    for p in papers:
        if p.id not in unique_incoming_dict:
            unique_incoming_dict[p.id] = p
            
    unique_papers = list(unique_incoming_dict.values())
    incoming_ids = list(unique_incoming_dict.keys())
    
    db = SessionLocal()
    try:
        # 2. Database deduplication (check against historical data)
        existing_records = db.query(Paper.id).filter(Paper.id.in_(incoming_ids)).all()
        existing_ids = {record[0] for record in existing_records}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during deduplication: {e}")
        existing_ids = set()
    finally:
        db.close()

    # 3. Final filtering
    new_papers = [paper for paper in unique_papers if paper.id not in existing_ids]

    logger.info(f"Deduplication complete: found {len(new_papers)} novel papers out of {len(papers)} originally fetched.")
    
    return new_papers