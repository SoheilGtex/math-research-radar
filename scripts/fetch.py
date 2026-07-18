import logging
import requests
import feedparser
from typing import List, Dict, Any

# Configure logging for production-grade tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"

def fetch_arxiv_papers(category: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch recent papers from a specific arXiv category.
    """
    logger.info(f"Fetching up to {max_results} papers for category: {category}")
    
    # arXiv API parameters
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }

    try:
        # 10 seconds timeout is a good practice to prevent hanging connections
        response = requests.get(ARXIV_API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from arXiv API: {e}")
        return []

    # Parse the Atom feed returned by arXiv
    feed = feedparser.parse(response.content)
    
    papers = []
    for entry in feed.entries:
        # Extract and clean up the data
        paper = {
            "id": entry.id,
            "title": entry.title.replace('\n', ' ').strip(),
            "published": entry.published,
            "summary": entry.summary.replace('\n', ' ').strip(),
            "link": entry.link
        }
        papers.append(paper)
        
    logger.info(f"Successfully parsed {len(papers)} papers.")
    return papers

if __name__ == "__main__":
    # Testing the function with 'math.RA' (Rings and Algebras)
    test_category = "math.RA"
    recent_papers = fetch_arxiv_papers(category=test_category, max_results=3)
    
    # Print the results for manual verification
    for p in recent_papers:
        print(f"\nTitle: {p['title']}")
        print(f"Date: {p['published']}")
        print(f"Link: {p['link']}")