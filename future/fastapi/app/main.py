from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.database import get_db, Paper
from app.schemas import PaperResponse

app = FastAPI(
    title="Math Research Radar API",
    description="RESTful API for querying mathematical research papers",
    version="1.0.0"
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "fastapi-backend"}

@app.get("/api/papers", response_model=List[PaperResponse])
def get_papers(
    category: Optional[str] = Query(None, description="Filter by math category (e.g., math.NA)"),
    limit: int = Query(50, ge=1, le=100, description="Number of papers to return"),
    db: Session = Depends(get_db)
):
    """Retrieve the latest papers, optionally filtered by category."""
    query = db.query(Paper)
    
    if category:
        query = query.filter(Paper.category == category)
        
    papers = query.order_by(desc(Paper.created_at)).limit(limit).all()
    return papers