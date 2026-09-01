import logging
import os

import redis
from celery import Celery
from celery.schedules import crontab

from radar.analytics.stats import generate_statistics

# We import the main pipeline logic
from radar.fetchers.arxiv import run_arxiv_pipeline
from radar.fetchers.crossref import run_crossref_pipeline
from radar.fetchers.openalex import run_openalex_pipeline
from radar.fetchers.semantic_scholar import run_semantic_scholar_pipeline
from radar.reporting.readme import generate_readme

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "radar_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    'run-daily-extraction-midnight': {
        'task': 'radar.tasks.run_full_extraction_pipeline',
        'schedule': crontab(minute=0, hour=0), 
    },
}

@celery_app.task
def run_full_extraction_pipeline():
    logger.info("🚀 Celery Task Started: Running full extraction pipeline...")
    
    try:
        run_arxiv_pipeline()
        run_crossref_pipeline()
        run_openalex_pipeline()
        run_semantic_scholar_pipeline()
        
        generate_statistics()
        generate_readme()
        
        logger.info("✅ Pipeline executed successfully via Celery.")
        
        try:
            r = redis.Redis.from_url(REDIS_URL)
            keys = r.keys("papers:*")
            if keys:
                r.delete(*keys)
                logger.info("🧹 Redis cache invalidated successfully.")
        except Exception as cache_err:
            logger.error(f"Failed to invalidate Redis cache: {cache_err}")
            
        return "Success"
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed during Celery execution: {e}")
        return f"Failed: {e}"