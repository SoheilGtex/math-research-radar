import logging
import time
from typing import List

from radar.config import settings
from radar.fetchers.base import BaseFetcher
from radar.models import Paper

logger = logging.getLogger(__name__)

# Semantic Scholar Graph API endpoint
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

class SemanticScholarFetcher(BaseFetcher):
    def __init__(self):
        # Semantic Scholar can be strict with rate limits, so we use a 3-second delay
        super().__init__(name="SemanticScholar", rate_limit_delay=3)

    def fetch_category(self, category: str) -> List[Paper]:
        logger.info(f"Fetching up to {settings.max_results_per_category} papers from Semantic Scholar for: {category}")
        
        # Optimize search string
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