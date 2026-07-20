import json
import logging
import os
from typing import List

from radar.config import settings
from radar.models import Paper

logger = logging.getLogger(__name__)

def filter_new_papers(papers: List[Paper]) -> List[Paper]:
    """Filter out globally seen papers using a persistent local cache."""
    os.makedirs(settings.cache_dir, exist_ok=True)
    cache_file = os.path.join(settings.cache_dir, "seen_ids.json")

    seen_ids = set()
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                seen_ids = set(json.load(f))
        except Exception as e:
            logger.warning(f"Cache file corrupted, starting fresh: {e}")

    new_papers: List[Paper] = []
    for paper in papers:
        if paper.id not in seen_ids:
            new_papers.append(paper)
            seen_ids.add(paper.id)

    if new_papers:
        # Update the global cache with newly discovered IDs
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(list(seen_ids), f, ensure_ascii=False)
            
        logger.info(f"Deduplication complete: found {len(new_papers)} novel papers out of {len(papers)}.")

    return new_papers