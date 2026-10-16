"""Deterministic data-quality analysis for arXiv research snapshots."""

from collections import Counter
from datetime import datetime


def analyze_quality(snapshot: dict) -> dict:
    """Analyze metadata quality without external services."""

    if snapshot.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot schema")

    if snapshot.get("source") != "arxiv":
        raise ValueError("Expected an arXiv snapshot")

    papers = snapshot.get("papers")

    if not isinstance(papers, list) or not papers:
        raise ValueError("Cannot analyze an empty snapshot")

    categories = Counter()
    seen_ids = set()
    duplicate_ids = []
    missing_abstract_ids = []
    invalid_date_ids = []
    invalid_url_ids = []
    publication_dates = []
    cross_listed = 0

    for paper in papers:
        identifier = paper["arxiv_id"]

        if identifier in seen_ids:
            duplicate_ids.append(identifier)
        seen_ids.add(identifier)

        paper_categories = paper["categories"]
        categories.update(paper_categories)

        if len(paper_categories) > 1:
            cross_listed += 1

        if not str(paper.get("summary") or "").strip():
            missing_abstract_ids.append(identifier)

        expected_url = f"https://arxiv.org/abs/{identifier}"
        if paper.get("url") != expected_url:
            invalid_url_ids.append(identifier)

        try:
            published = datetime.fromisoformat(
                paper["published"].replace("Z", "+00:00")
            )
            if published.tzinfo is None:
                raise ValueError("Timezone missing")
            publication_dates.append(published)
        except (ValueError, TypeError, AttributeError):
            invalid_date_ids.append(identifier)

    issues = {
        "duplicate_ids": sorted(duplicate_ids),
        "missing_abstract_ids": sorted(missing_abstract_ids),
        "invalid_date_ids": sorted(invalid_date_ids),
        "invalid_url_ids": sorted(invalid_url_ids),
    }

    return {
        "schema_version": 1,
        "source": "arxiv",
        "total_papers": len(papers),
        "category_counts": dict(sorted(categories.items())),
        "cross_listed_papers": cross_listed,
        "publication_window": {
            "earliest": min(publication_dates).date().isoformat()
            if publication_dates else None,
            "latest": max(publication_dates).date().isoformat()
            if publication_dates else None,
        },
        "issues": issues,
        "checks": {
            "unique_ids": not duplicate_ids,
            "valid_publication_dates": not invalid_date_ids,
            "canonical_urls": not invalid_url_ids,
        },
    }
