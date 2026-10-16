import logging

from sqlalchemy import desc

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def generate_readme() -> None:
    """Update the marked README section without changing unmarked files."""
    db = SessionLocal()
    try:
        # Fetch the 5 most recently added papers from the database
        latest_papers = db.query(Paper).order_by(desc(Paper.created_at)).limit(5).all()
        
        latest_papers_text = "\n### 📄 Latest Discovered Papers\n\n"
        if not latest_papers:
            latest_papers_text += "*No papers found in the database yet.*\n"
        else:
            for p in latest_papers:
                pub_date = p.published[:10] if p.published else "Unknown Date"
                latest_papers_text += f"1. **[{p.title}]({p.link})**\n   - *Category: {p.category} | Source: {p.source} | Published: {pub_date}*\n"
        
        start_tag = "<!-- LATEST_PAPERS_START -->"
        end_tag = "<!-- LATEST_PAPERS_END -->"
        
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()

            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag)

            # Never modify an unmarked README.
            if start_idx < 0 or end_idx < 0 or start_idx >= end_idx:
                logger.info(
                    "README.md has no valid dynamic markers; skipping update."
                )
                return

            before = content[:start_idx + len(start_tag)]
            after = content[end_idx:]
            new_content = before + latest_papers_text + "\n" + after

            if new_content == content:
                logger.info("Dynamic README section unchanged.")
                return

            with open("README.md", "w", encoding="utf-8") as file:
                file.write(new_content)

            logger.info("Updated marked README section.")

        except Exception as e:
            logger.error(f"Failed to read/write README.md: {e}")
            
    except Exception as e:
        logger.error(f"Database error while generating README: {e}")
    finally:
        db.close()