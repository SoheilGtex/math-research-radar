import json
import logging
import os
from typing import List

from radar.config import settings
from radar.models import Paper

logger = logging.getLogger(__name__)

def save_papers(papers: List[Paper], filename: str) -> None:
    """Append validated Paper objects to the daily JSON storage file."""
    if not papers:
        return

    os.makedirs(settings.papers_dir, exist_ok=True)
    filepath = os.path.join(settings.papers_dir, filename)
    
    existing_papers = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_papers = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"File {filepath} is corrupted. Starting fresh.")
            
    # Protect against same-day overlaps from different fetchers
    existing_ids = {p["id"] for p in existing_papers}
    to_append = [p.to_dict() for p in papers if p.id not in existing_ids]
    
    if not to_append:
        return

    all_papers = existing_papers + to_append
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_papers, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Successfully wrote {len(to_append)} papers to {filepath}.")