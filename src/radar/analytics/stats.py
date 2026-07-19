import glob
import json
import logging
import os
from collections import Counter

from radar.config import settings

logger = logging.getLogger(__name__)

def generate_statistics() -> None:
    """Read all daily paper JSON files and generate aggregated statistics."""
    os.makedirs(settings.stats_dir, exist_ok=True)
    
    category_counts = Counter()
    daily_stats = {}
    
    # Use centralized configuration for paths
    paper_files = glob.glob(os.path.join(settings.papers_dir, "*.json"))
    
    if not paper_files:
        logger.warning("No paper files found to process.")
        return

    for filepath in sorted(paper_files):
        date_str = os.path.basename(filepath).replace(".json", "")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                papers = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to read {filepath} - Invalid JSON: {e}")
            continue
            
        day_category_counts = Counter()
        for paper in papers:
            cat = paper.get("category", "unknown")
            category_counts[cat] += 1
            day_category_counts[cat] += 1
            
        daily_stats[date_str] = {
            "total_fetched": len(papers),
            "categories": dict(day_category_counts)
        }
        
    categories_path = os.path.join(settings.stats_dir, "categories.json")
    with open(categories_path, 'w', encoding='utf-8') as f:
        json.dump(dict(category_counts), f, indent=4, ensure_ascii=False)
    logger.info(f"Updated {categories_path} with total counts.")

    history_path = os.path.join(settings.stats_dir, "history.json")
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(daily_stats, f, indent=4, ensure_ascii=False)
    logger.info(f"Updated {history_path} with daily statistics.")