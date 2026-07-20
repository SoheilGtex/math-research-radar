import logging
from typing import List

import feedparser

from radar.config import settings
from radar.fetchers.base import BaseFetcher
from radar.models import Paper

logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"

class ArxivFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(name="arXiv", rate_limit_delay=3)

    def fetch_category(self, category: str) -> List[Paper]:
        logger.info(f"Fetching up to {settings.max_results_per_category} papers from arXiv for: {category}")
        
        params = {
            "search_query": f"cat:{category}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": settings.max_results_per_category
        }

        response = self.session.get(ARXIV_API_URL, params=params, timeout=settings.timeout_seconds)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        papers: List[Paper] = []
        
        for entry in feed.entries:
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
            
        logger.info(f"Successfully parsed {len(papers)} papers from arXiv for {category}.")
        return papers

def run_arxiv_pipeline() -> None:
    """Entry point for the arXiv fetcher module."""
    fetcher = ArxivFetcher()
    fetcher.run_pipeline()