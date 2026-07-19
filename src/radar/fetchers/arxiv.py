import logging
import time
from datetime import datetime
from typing import List

import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from radar.config import settings
from radar.models import Paper
from radar.storage.json import save_papers

logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"

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
    return session

def fetch_arxiv_papers(session: requests.Session, category: str) -> List[Paper]:
    """Fetch recent papers from arXiv and map them to the unified Paper model."""
    logger.info(f"Fetching up to {settings.max_results_per_category} papers for category: {category}")
    
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": settings.max_results_per_category
    }

    try:
        response = session.get(ARXIV_API_URL, params=params, timeout=settings.timeout_seconds)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from arXiv API for {category}: {e}")
        return []

    feed = feedparser.parse(response.content)
    
    papers: List[Paper] = []
    for entry in feed.entries:
        # Enforce schema instantly upon data extraction
        paper = Paper(
            id=entry.id,
            title=entry.title.replace('\n', ' ').strip(),
            published=entry.published,
            summary=entry.summary.replace('\n', ' ').strip(),
            link=entry.link,
            category=category,
            source="arxiv"
        )
        papers.append(paper)
        
    logger.info(f"Successfully parsed {len(papers)} papers from {category}.")
    return papers

def run_arxiv_pipeline() -> None:
    """Entry point for the arXiv fetcher module."""
    session = get_requests_session()
    all_fetched_papers: List[Paper] = []
    
    for idx, cat in enumerate(settings.categories):
        if idx > 0:
            logger.info("Waiting 3 seconds to respect arXiv API rate limits...")
            time.sleep(3)
            
        recent_papers = fetch_arxiv_papers(session=session, category=cat)
        all_fetched_papers.extend(recent_papers)
        
    if all_fetched_papers:
        today_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today_str}.json"
        save_papers(all_fetched_papers, filename)