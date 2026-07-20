import logging
import time
from typing import List

from radar.config import settings
from radar.fetchers.base import BaseFetcher
from radar.models import Paper

logger = logging.getLogger(__name__)

OPENALEX_API_URL = "https://api.openalex.org/works"

class OpenAlexFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="OpenAlex", rate_limit_delay=2)
        # OpenAlex uses a polite pool mechanism similar to Crossref
        self.session.headers.update({"User-Agent": "MathResearchRadar/0.1.0 (mailto:radar-bot@example.com)"})

    def fetch_category(self, category: str) -> List[Paper]:
        logger.info(f"Fetching up to {settings.max_results_per_category} papers from OpenAlex for: {category}")
        
        search_query = category.replace("math.", "") + " mathematics"
        
        params = {
            "search": search_query,
            "per-page": settings.max_results_per_category,
            "sort": "publication_date:desc"
        }

        response = self.session.get(OPENALEX_API_URL, params=params, timeout=settings.timeout_seconds)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        papers: List[Paper] = []
        
        for item in results:
            title = item.get("title")
            # Skip items without a proper title
            if not title:
                continue
                
            published = item.get("publication_date", "Unknown Date")
            
            paper = Paper(
                id=item.get("id", f"openalex-{time.time()}"),
                title=title.replace('\n', ' ').strip(),
                published=published,
                summary="Abstract available via OpenAlex API.",
                link=item.get("doi") or item.get("id", ""),
                category=category,
                source="openalex"
            )
            papers.append(paper)
            
        logger.info(f"Successfully parsed {len(papers)} papers from OpenAlex for {category}.")
        return papers

def run_openalex_pipeline() -> None:
    """Entry point for the OpenAlex fetcher module."""
    fetcher = OpenAlexFetcher()
    fetcher.run_pipeline()