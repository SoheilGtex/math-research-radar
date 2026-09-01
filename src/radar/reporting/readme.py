import logging
import re
from sqlalchemy import desc

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def generate_readme() -> None:
    """Update the dynamic section of README.md with the latest papers directly from PostgreSQL."""
    db = SessionLocal()
    try:
        # Fetch the 5 most recently added papers from the database
        latest_papers = db.query(Paper).order_by(desc(Paper.created_at)).limit(5).all()
        
        latest_papers_text = "\n### 📄 Latest Discovered Papers\n\n"
        if not latest_papers:
            latest_papers_text += "*No papers found in the database yet.*\n"
        else:
            for p in latest_papers:
                # Format the date nicely
                pub_date = p.published[:10] if p.published else "Unknown Date"
                latest_papers_text += f"1. **[{p.title}]({p.link})**\n   - *Category: {p.category} | Source: {p.source} | Published: {pub_date}*\n"
        
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()
                
            # Bulletproof regex: finds the tags regardless of newlines or spaces between them
            pattern = re.compile(
                r"(<!-- LATEST_PAPERS_START -->)[\s\S]*?(<!-- LATEST_PAPERS_END -->)", 
                re.IGNORECASE
            )
            
            if pattern.search(content):
                # Inject the new content with guaranteed newlines
                new_content = pattern.sub(rf"\1{latest_papers_text}\n\2", content)
                with open("README.md", "w", encoding="utf-8") as f:
                    f.write(new_content)
                logger.info("Successfully updated the dynamic section of README.md from PostgreSQL.")
            else:
                logger.warning("Could not find dynamic tags in README.md. Ensure <!-- LATEST_PAPERS_START --> and <!-- LATEST_PAPERS_END --> exist.")
                
        except Exception as e:
            logger.error(f"Failed to read/write README.md: {e}")
            
    except Exception as e:
        logger.error(f"Database error while generating README: {e}")
    finally:
        db.close()