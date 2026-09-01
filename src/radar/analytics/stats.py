import json
import logging
from sqlalchemy import func, cast, Date

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def generate_statistics() -> None:
    """Generate analytics by querying the PostgreSQL database using SQL aggregations."""
    db = SessionLocal()
    try:
        # 1. Aggregate counts per category
        category_counts = db.query(Paper.category, func.count(Paper.id)).group_by(Paper.category).all()
        cat_stats = {cat: count for cat, count in category_counts}
        
        with open("data/stats/categories.json", "w", encoding="utf-8") as f:
            json.dump(cat_stats, f, ensure_ascii=False, indent=4)
        logger.info("Updated data/stats/categories.json with total counts from PostgreSQL.")

        # 2. Aggregate history counts (papers stored per day)
        history_counts = db.query(
            cast(Paper.created_at, Date).label("day"), 
            func.count(Paper.id)
        ).group_by("day").order_by("day").all()
        
        hist_stats = {str(day): count for day, count in history_counts if day}

        with open("data/stats/history.json", "w", encoding="utf-8") as f:
            json.dump(hist_stats, f, ensure_ascii=False, indent=4)
        logger.info("Updated data/stats/history.json with daily statistics from PostgreSQL.")

    except Exception as e:
        logger.error(f"Error generating statistics from DB: {e}")
    finally:
        db.close()