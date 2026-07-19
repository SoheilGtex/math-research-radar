import json
import logging
import os
from typing import List

from radar.config import settings
from radar.models import Paper

logger = logging.getLogger(__name__)

def save_papers(papers: List[Paper], filename: str) -> None:
    """Save deduplicated Paper objects to the configured JSON storage directory."""
    os.makedirs(settings.papers_dir, exist_ok=True)
    filepath = os.path.join(settings.papers_dir, filename)
    
    existing_papers = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_papers = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"File {filepath} is corrupted. Starting fresh.")
            
    existing_ids = {paper["id"] for paper in existing_papers}
    
    # Filter new papers and convert them back to dicts for JSON serialization
    new_papers = [p.to_dict() for p in papers if p.id not in existing_ids]
    
    if not new_papers:
        logger.info("No new papers to save.")
        return

    all_papers = existing_papers + new_papers
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_papers, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Saved {len(new_papers)} new papers to {filepath}.")