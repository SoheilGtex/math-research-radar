import json
import os
import logging
import redis
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.database import get_db, Paper
from app.schemas import PaperResponse

logger = logging.getLogger(__name__)

# Initialize Redis client using Docker's internal DNS
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(
    title="Math Research Radar API",
    description="RESTful API for querying mathematical research papers with Redis caching",
    version="1.1.0"
)

@app.get("/api/health")
def health_check():
    """Verify backend and caching layer connectivity."""
    try:
        cache_status = cache.ping()
    except redis.ConnectionError:
        cache_status = False
    return {"status": "healthy", "service": "fastapi-backend", "redis_connected": cache_status}

@app.get("/api/papers", response_model=List[PaperResponse])
def get_papers(
    category: Optional[str] = Query(None, description="Filter by math category (e.g., math.NA)"),
    limit: int = Query(50, ge=1, le=100, description="Number of papers to return"),
    db: Session = Depends(get_db)
):
    """Retrieve the latest papers, utilizing Redis for sub-millisecond latency."""
    cache_key = f"papers:{category if category else 'all'}:{limit}"
    
    # 1. Check Redis Cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # 2. Cache Miss: Query PostgreSQL
    query = db.query(Paper)
    if category:
        query = query.filter(Paper.category == category)
        
    papers = query.order_by(desc(Paper.created_at)).limit(limit).all()
    
    # 3. Serialize and save to Redis (Cache for 1 hour)
    # Convert SQLAlchemy ORM models to Pydantic models, then dump to dicts
    papers_dict = [PaperResponse.model_validate(p).model_dump(mode='json') for p in papers]
    
    try:
        cache.setex(cache_key, 3600, json.dumps(papers_dict))
    except redis.ConnectionError as e:
        logger.error(f"Redis cache failed: {e}")
        
    return papers