import logging

from sqlalchemy import desc

from radar.db import SessionLocal
from radar.models import Paper

logger = logging.getLogger(__name__)

def generate_readme() -> None:
    """Update the dynamic section of README.md. Self-heals if tags are missing."""
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

            # Self-healing logic: If tags exist and are ordered correctly
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                before_tags = content[:start_idx + len(start_tag)]
                after_tags = content[end_idx:]
                new_content = f"{before_tags}{latest_papers_text}\n{after_tags}"
            else:
                # SELF-HEAL: Tags are missing or corrupted. Append them to the end automatically.
                logger.warning("Tags missing or corrupted. Self-healing README.md by appending tags...")
                # Strip trailing whitespace/newlines before appending
                new_content = f"{content.rstrip()}\n\n{start_tag}{latest_papers_text}\n{end_tag}\n"
                
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info("Successfully updated the dynamic section of README.md from PostgreSQL.")
                
        except Exception as e:
            logger.error(f"Failed to read/write README.md: {e}")
            
    except Exception as e:
        logger.error(f"Database error while generating README: {e}")
    finally:
        db.close()