import logging
from sqlalchemy import desc

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def generate_readme() -> None:
    """Update the dynamic section of README.md with the latest papers using robust string manipulation."""
    db = SessionLocal()
    try:
        # Fetch the 5 most recently added papers from the database
        latest_papers = db.query(Paper).order_by(desc(Paper.created_at)).limit(5).all()
        
        latest_papers_text = "### 📄 Latest Discovered Papers\n\n"
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

            start_tag = "<!-- LATEST_PAPERS_START -->"
            end_tag = "<!-- LATEST_PAPERS_END -->"

            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag)

            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                # Construct the new content by slicing the string
                before_tags = content[:start_idx + len(start_tag)]
                after_tags = content[end_idx:]
                
                new_content = f"{before_tags}\n\n{latest_papers_text}\n{after_tags}"
                
                with open("README.md", "w", encoding="utf-8") as f:
                    f.write(new_content)
                logger.info("Successfully updated the dynamic section of README.md from PostgreSQL.")
            else:
                logger.warning("Could not find dynamic tags in README.md. Ensure both tags exist and are ordered correctly.")
                
        except Exception as e:
            logger.error(f"Failed to read/write README.md: {e}")
            
    except Exception as e:
        logger.error(f"Database error while generating README: {e}")
    finally:
        db.close()