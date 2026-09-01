import os
import logging
from celery import Celery
import redis

# We import the main pipeline logic
from radar.fetchers.arxiv import run_arxiv_pipeline
from radar.fetchers.crossref import run_crossref_pipeline
from radar.fetchers.openalex import run_openalex_pipeline
from radar.fetchers.semantic_scholar import run_semantic_scholar_pipeline
from radar.analytics.stats import generate_statistics
from radar.reporting.readme import generate_readme
from radar.dashboard.generator import build_dashboard

logger = logging.getLogger(__name__)

# Redis acts as both the message broker for Celery and our caching layer
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "radar_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Optional: Configure timezone for scheduled tasks (Celery Beat)
celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def run_full_extraction_pipeline():
    """Celery task to run the entire ETL pipeline."""
    logger.info("🚀 Celery Task Started: Running full extraction pipeline...")
    
    try:
        run_arxiv_pipeline()
        run_crossref_pipeline()
        run_openalex_pipeline()
        run_semantic_scholar_pipeline()
        
        generate_statistics()
        generate_readme()
        build_dashboard()
        
        logger.info("✅ Pipeline executed successfully via Celery.")
        
        # Cache Invalidation: Clear the Redis cache so API serves fresh data
        try:
            r = redis.Redis.from_url(REDIS_URL)
            # Find and delete all cache keys used by FastAPI
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