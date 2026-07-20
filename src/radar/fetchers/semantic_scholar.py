import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List

from radar.config import settings
from radar.models import Paper
from radar.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

class SemanticScholarFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="SemanticScholar", rate_limit_delay=5)

    def _create_session(self) -> requests.Session:
        """Override session creation to provide a much higher backoff factor for Semantic Scholar."""
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=3,  # Delays will be: 0s, 6s, 12s, 24s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_category(self, category: str) -> List[Paper]:
        logger.info(f"Fetching up to {settings.max_results_per_category} papers from Semantic Scholar for: {category}")
        
        search_query = category.replace("math.", "") + " mathematics"
        
        params = {
            "query": search_query,
            "fields": "paperId,title,url,publicationDate,abstract",
            "limit": settings.max_results_per_category
        }

        try:
            response = self.session.get(SEMANTIC_SCHOLAR_API_URL, params=params, timeout=settings.timeout_seconds)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch data from Semantic Scholar API for {category}: {e}")
            return []

        items = data.get("data", [])
        papers: List[Paper] = []
        
        for item in items:
            title = item.get("title")
            if not title:
                continue
                
            paper = Paper(
                id=item.get("paperId", f"s2-{time.time()}"),
                title=title.replace('\n', ' ').strip(),
                published=item.get("publicationDate", "Unknown Date") or "Unknown Date",
                summary=(item.get("abstract") or "No abstract provided.").replace('\n', ' ').strip(),
                link=item.get("url", ""),
                category=category,
                source="semantic_scholar"
            )
            papers.append(paper)
            
        logger.info(f"Successfully parsed {len(papers)} papers from Semantic Scholar for {category}.")
        return papers

def run_semantic_scholar_pipeline() -> None:
    """Entry point for the Semantic Scholar fetcher module."""
    fetcher = SemanticScholarFetcher()
    fetcher.run_pipeline()