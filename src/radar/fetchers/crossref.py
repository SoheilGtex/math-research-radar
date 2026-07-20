import logging
import time
from datetime import datetime
from typing import List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from radar.config import settings
from radar.models import Paper
from radar.storage.json import save_papers

logger = logging.getLogger(__name__)

# Crossref REST API endpoint
CROSSREF_API_URL = "https://api.crossref.org/works"

def get_requests_session() -> requests.Session:
    """Create a robust HTTP session with exponential backoff retries."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Crossref requests the "Polite Pool" usage by providing an email
    session.headers.update({"User-Agent": "MathResearchRadar/0.1.0 (mailto:radar-bot@example.com)"})
    return session

def fetch_crossref_papers(session: requests.Session, category: str) -> List[Paper]:
    """Fetch recent papers from Crossref and map them to the unified Paper model."""
    logger.info(f"Fetching up to {settings.max_results_per_category} papers from Crossref for: {category}")
    
    # Clean up the category name for better Crossref text search (e.g., "math.NA" -> "NA mathematics")
    search_query = category.replace("math.", "") + " mathematics"
    
    params = {
        "query": search_query,
        "select": "DOI,title,created,abstract,URL,subject",
        "rows": settings.max_results_per_category,
        "sort": "created",
        "order": "desc"
    }

    try:
        response = session.get(CROSSREF_API_URL, params=params, timeout=settings.timeout_seconds)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from Crossref API for {category}: {e}")
        return []
    except ValueError as e:
        logger.error(f"Failed to parse JSON from Crossref API: {e}")
        return []

    items = data.get("message", {}).get("items", [])
    papers: List[Paper] = []
    
    for item in items:
        # Map Crossref fields to our unified Domain Model
        title_list = item.get("title", [])
        title = title_list[0] if title_list else "Unknown Title"
        
        # Safe extraction of nested dates
        created = item.get("created", {}).get("date-time", "Unknown Date")
        
        paper = Paper(
            id=item.get("DOI", f"crossref-{time.time()}"), # Use DOI as ID
            title=title.replace('\n', ' ').strip(),
            published=created,
            summary=item.get("abstract", "No abstract provided by Crossref.").replace('\n', ' ').strip(),
            link=item.get("URL", ""),
            category=category,
            source="crossref"
        )
        papers.append(paper)
        
    logger.info(f"Successfully parsed {len(papers)} papers from Crossref for {category}.")
    return papers

def run_crossref_pipeline() -> None:
    """Entry point for the Crossref fetcher module."""
    session = get_requests_session()
    all_fetched_papers: List[Paper] = []
    
    for idx, cat in enumerate(settings.categories):
        if idx > 0:
            logger.info("Waiting 2 seconds to respect Crossref API limits...")
            time.sleep(2)
            
        recent_papers = fetch_crossref_papers(session=session, category=cat)
        all_fetched_papers.extend(recent_papers)
        
    if all_fetched_papers:
        today_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today_str}.json" # It will merge perfectly with arXiv data
        save_papers(all_fetched_papers, filename)