import os
import json
import glob
import logging
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PAPERS_DIR = "papers"
STATS_DIR = "stats"


def update_statistics() -> None:
    """
    Read all daily paper JSON files and generate aggregated statistics.
    """
    os.makedirs(STATS_DIR, exist_ok=True)

    category_counts = Counter()
    daily_stats = {}

    # Find all JSON files in the papers directory
    paper_files = glob.glob(os.path.join(PAPERS_DIR, "*.json"))

    if not paper_files:
        logger.warning("No paper files found to process.")
        return

    # Process files in chronological order
    for filepath in sorted(paper_files):
        # Extract date from filename (e.g., 2026-07-18.json -> 2026-07-18)
        date_str = os.path.basename(filepath).replace(".json", "")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                papers = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to read {filepath} - Invalid JSON: {e}")
            continue

        day_category_counts = Counter()
        for paper in papers:
            cat = paper.get("category", "unknown")
            category_counts[cat] += 1
            day_category_counts[cat] += 1

        # Store historical snapshot for this specific day
        daily_stats[date_str] = {
            "total_fetched": len(papers),
            "categories": dict(day_category_counts),
        }

    # Save overall category statistics
    categories_path = os.path.join(STATS_DIR, "categories.json")
    with open(categories_path, "w", encoding="utf-8") as f:
        json.dump(dict(category_counts), f, indent=4, ensure_ascii=False)
    logger.info(f"Updated {categories_path} with total counts.")

    # Save historical statistics
    history_path = os.path.join(STATS_DIR, "history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(daily_stats, f, indent=4, ensure_ascii=False)
    logger.info(f"Updated {history_path} with daily statistics.")


if __name__ == "__main__":
    update_statistics()
