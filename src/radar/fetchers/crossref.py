import logging
import time
from typing import List

from radar.config import settings
from radar.fetchers.base import BaseFetcher
from radar.models import Paper

logger = logging.getLogger(__name__)

CROSSREF_API_URL = "https://api.crossref.org/works"

class CrossrefFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="Crossref", rate_limit_delay=2)
        # Crossref requests the "Polite Pool" usage by providing an email
        self.session.headers.update({"User-Agent": "MathResearchRadar/0.1.0 (mailto:radar-bot@example.com)"})

    def fetch_category(self, category: str) -> List[Paper]:
        logger.info(f"Fetching up to {settings.max_results_per_category} papers from Crossref for: {category}")
        
        search_query = category.replace("math.", "") + " mathematics"
        
        params = {
            "query": search_query,
            "select": "DOI,title,created,abstract,URL,subject",
            "rows": settings.max_results_per_category,
            "sort": "created",
            "order": "desc"
        }

        response = self.session.get(CROSSREF_API_URL, params=params, timeout=settings.timeout_seconds)
        response.raise_for_status()
        data = response.json()

        items = data.get("message", {}).get("items", [])
        papers: List[Paper] = []
        
        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else "Unknown Title"
            created = item.get("created", {}).get("date-time", "Unknown Date")
            
            paper = Paper(
                id=item.get("DOI", f"crossref-{time.time()}"),
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
    fetcher = CrossrefFetcher()
    fetcher.run_pipeline()