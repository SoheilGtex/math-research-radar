import os
import json
import logging
import time
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import feedparser
from typing import List, Dict, Any

# Configure logging for production-grade tracking
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"
PAPERS_DIR = "papers"
CONFIG_FILE = "config.json"


def get_requests_session() -> requests.Session:
    """
    Create a robust HTTP session with a retry strategy for resilient network calls.
    """
    session = requests.Session()

    # Retry up to 3 times, with exponential backoff (1s, 2s, 4s)
    # Target typical transient server errors or rate limits
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def load_config() -> Dict[str, Any]:
    """Load configuration settings from config.json."""
    if not os.path.exists(CONFIG_FILE):
        logger.warning(f"Config file {CONFIG_FILE} not found. Using defaults.")
        return {
            "categories": ["math.NA", "math.LO"],
            "max_results_per_category": 3,
            "timeout_seconds": 10,
        }

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {CONFIG_FILE}: {e}")
        return {"categories": [], "max_results_per_category": 5, "timeout_seconds": 10}


def fetch_arxiv_papers(
    session: requests.Session, category: str, max_results: int, timeout: int
) -> List[Dict[str, Any]]:
    """Fetch recent papers from a specific arXiv category using a resilient session."""
    logger.info(f"Fetching up to {max_results} papers for category: {category}")

    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }

    try:
        response = session.get(ARXIV_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from arXiv API for {category}: {e}")
        return []

    feed = feedparser.parse(response.content)

    papers = []
    for entry in feed.entries:
        paper = {
            "id": entry.id,
            "title": entry.title.replace("\n", " ").strip(),
            "published": entry.published,
            "summary": entry.summary.replace("\n", " ").strip(),
            "link": entry.link,
            "category": category,
        }
        papers.append(paper)

    logger.info(f"Successfully parsed {len(papers)} papers from {category}.")
    return papers


def save_papers_to_json(papers: List[Dict[str, Any]], filename: str) -> None:
    """Save papers to a JSON file, ensuring no duplicates exist based on paper ID."""
    os.makedirs(PAPERS_DIR, exist_ok=True)
    filepath = os.path.join(PAPERS_DIR, filename)

    existing_papers = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing_papers = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"File {filepath} is corrupted. Starting fresh.")

    existing_ids = {paper["id"] for paper in existing_papers}
    new_papers = [p for p in papers if p["id"] not in existing_ids]

    if not new_papers:
        logger.info("No new papers to save.")
        return

    all_papers = existing_papers + new_papers
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_papers, f, indent=4, ensure_ascii=False)

    logger.info(f"Saved {len(new_papers)} new papers to {filepath}.")


if __name__ == "__main__":
    config = load_config()
    categories = config.get("categories", [])
    max_results = config.get("max_results_per_category", 5)
    timeout = config.get("timeout_seconds", 15)

    session = get_requests_session()
    all_fetched_papers = []

    for idx, cat in enumerate(categories):
        # Polite delay to avoid hitting rate limits (applied after the first request)
        if idx > 0:
            logger.info("Waiting 3 seconds to respect arXiv API rate limits...")
            time.sleep(3)

        recent_papers = fetch_arxiv_papers(
            session=session, category=cat, max_results=max_results, timeout=timeout
        )
        all_fetched_papers.extend(recent_papers)

    if all_fetched_papers:
        today_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today_str}.json"
        save_papers_to_json(all_fetched_papers, filename)
