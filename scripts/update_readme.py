import os
import json
import glob
import logging
import re
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

README_PATH = "README.md"
STATS_FILE = "stats/categories.json"
PAPERS_DIR = "papers"


def generate_readme() -> None:
    """
    Generate the dynamic parts of the README and inject them between specific markers.
    """
    logger.info("Starting dynamic README generation...")

    # 1. Load statistics
    total_papers = 0
    stats_text = ""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                stats = json.load(f)
                for cat in sorted(stats.keys()):
                    count = stats[cat]
                    stats_text += f"- **{cat}**: {count} papers\n"
                    total_papers += count
        except Exception as e:
            logger.error(f"Failed to read stats file: {e}")

    # 2. Load latest papers
    latest_papers_text = ""
    paper_files = sorted(glob.glob(os.path.join(PAPERS_DIR, "*.json")), reverse=True)

    if paper_files:
        latest_file = paper_files[0]
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                papers = json.load(f)
                # Display up to 5 most recent papers
                for p in papers[:5]:
                    pub_date = p.get("published", "Unknown Date")[:10]
                    latest_papers_text += f"1. **[{p['title']}]({p['link']})**\n   - *Category: {p['category']} | Published: {pub_date}*\n"
        except Exception as e:
            logger.error(f"Failed to read latest papers from {latest_file}: {e}")

    # 3. Construct Dynamic Markdown content
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    dynamic_content = f"""
## 📊 Repository Statistics
**Total Papers Tracked:** {total_papers}

{stats_text if stats_text else "_No statistics available yet._"}

## 🆕 Latest Discoveries
{latest_papers_text if latest_papers_text else "_No papers fetched yet._"}

---
*Last updated automatically by GitHub Actions on: **{now_utc}***
"""

    # 4. Inject into README.md using Regex
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme_content = f.read()

        # Regex pattern to match everything between the markers
        pattern = r"(<!-- RADAR_START -->)(.*?)(<!-- RADAR_END -->)"

        # Replace the content inside the markers with our new dynamic content
        new_readme = re.sub(
            pattern, rf"\1\n{dynamic_content}\n\3", readme_content, flags=re.DOTALL
        )

        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_readme)

        logger.info("Successfully updated the dynamic section of README.md")
    except Exception as e:
        logger.error(f"Failed to update README.md: {e}")


if __name__ == "__main__":
    generate_readme()
