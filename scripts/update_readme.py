import os
import json
import glob
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

README_PATH = "README.md"
STATS_FILE = "stats/categories.json"
PAPERS_DIR = "papers"

def generate_readme() -> None:
    """
    Generate the README.md file dynamically based on stats and recent papers.
    """
    logger.info("Starting README generation...")

    # 1. Load statistics
    total_papers = 0
    stats_text = ""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                # Sort categories alphabetically
                for cat in sorted(stats.keys()):
                    count = stats[cat]
                    stats_text += f"- **{cat}**: {count} papers\n"
                    total_papers += count
        except Exception as e:
            logger.error(f"Failed to read stats file: {e}")

    # 2. Load latest papers
    latest_papers_text = ""
    # glob gets all json files, sorted reverse means newest first (e.g., 2026-07-18 before 2026-07-17)
    paper_files = sorted(glob.glob(os.path.join(PAPERS_DIR, "*.json")), reverse=True)
    
    if paper_files:
        latest_file = paper_files[0]
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
                # Display up to 5 most recent papers
                for p in papers[:5]:
                    # Extract only the date part from ISO format
                    pub_date = p.get('published', 'Unknown Date')[:10]
                    latest_papers_text += f"1. **[{p['title']}]({p['link']})**\n   - *Category: {p['category']} | Published: {pub_date}*\n"
        except Exception as e:
            logger.error(f"Failed to read latest papers from {latest_file}: {e}")

    # 3. Construct Markdown content
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    readme_content = f"""# 📡 Math Research Radar

An automated pipeline to track, store, and analyze new Mathematics papers from arXiv.
Built with Python and GitHub Actions.

## 📊 Repository Statistics
**Total Papers Tracked:** {total_papers}

{stats_text if stats_text else "_No statistics available yet._"}

## 🆕 Latest Discoveries
{latest_papers_text if latest_papers_text else "_No papers fetched yet._"}

---
*Last updated automatically on: **{now_utc}***
"""

    # 4. Write to README.md
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(readme_content)
        
    logger.info("Successfully updated README.md")

if __name__ == "__main__":
    generate_readme()