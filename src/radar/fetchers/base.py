import abc
import logging
import time
from datetime import datetime
from typing import List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from radar.config import settings
from radar.deduplication.filter import filter_new_papers
from radar.models import Paper
from radar.storage.json import save_papers

logger = logging.getLogger(__name__)

class BaseFetcher(abc.ABC):
    """Abstract Base Class defining the template for all research paper fetchers."""
    
    def __init__(self, name: str, rate_limit_delay: int = 2):
        self.name = name
        self.rate_limit_delay = rate_limit_delay
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
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

    @abc.abstractmethod
    def fetch_category(self, category: str) -> List[Paper]:
        """Fetch papers for a specific category. Must be implemented by subclasses."""
        pass

    def run_pipeline(self) -> None:
        """Template method: Execute the fetch pipeline for all categories and save results."""
        logger.info(f"Starting pipeline for {self.name} fetcher...")
        all_fetched_papers: List[Paper] = []
        
        for idx, cat in enumerate(settings.categories):
            if idx > 0:
                logger.info(f"Waiting {self.rate_limit_delay}s to respect {self.name} API rate limits...")
                time.sleep(self.rate_limit_delay)
                
            try:
                recent_papers = self.fetch_category(cat)
                all_fetched_papers.extend(recent_papers)
            except Exception as e:
                logger.error(f"Error fetching {cat} from {self.name}: {e}")
            
        if all_fetched_papers:
            # Enforce global deduplication before storage
            novel_papers = filter_new_papers(all_fetched_papers)
            if novel_papers:
                today_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{today_str}.json"
                save_papers(novel_papers, filename)
            else:
                logger.info(f"No novel papers found for {self.name} across all categories.")