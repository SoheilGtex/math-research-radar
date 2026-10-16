import pytest
from radar.analytics.quality import analyze_quality


def make_paper(identifier, category="math.NA"):
    return {
        "arxiv_id": identifier,
        "title": "Numerical Research",
        "published": "2026-10-16T09:00:00Z",
        "summary": "A mathematical research paper.",
        "url": f"https://arxiv.org/abs/{identifier}",
        "categories": [category],
    }


def make_snapshot(papers):
    return {
        "schema_version": 1,
        "source": "arxiv",
        "papers": papers,
    }


def test_clean_research_snapshot():
    first = make_paper("2610.12345")
    first["categories"] = ["math.NA", "math.LO"]

    second = make_paper("2610.12346", "math.NA")
    second["published"] = "2026-10-15T09:00:00Z"

    result = analyze_quality(make_snapshot([first, second]))

    assert result["total_papers"] == 2
    assert result["cross_listed_papers"] == 1
    assert result["category_counts"] == {
        "math.LO": 1,
        "math.NA": 2,
    }

    assert result["publication_window"] == {
        "earliest": "2026-10-15",
        "latest": "2026-10-16",
    }

    assert all(result["checks"].values())
    assert all(not issues for issues in result["issues"].values())


def test_quality_issues_are_detected():
    first = make_paper("2610.12345")

    second = make_paper("2610.12345")
    second["summary"] = ""
    second["published"] = "invalid-date"
    second["url"] = "https://example.com/incorrect"

    result = analyze_quality(make_snapshot([first, second]))

    assert result["issues"]["duplicate_ids"] == ["2610.12345"]
    assert result["issues"]["missing_abstract_ids"] == ["2610.12345"]
    assert result["issues"]["invalid_date_ids"] == ["2610.12345"]
    assert result["issues"]["invalid_url_ids"] == ["2610.12345"]

    assert result["checks"]["unique_ids"] is False
    assert result["checks"]["valid_publication_dates"] is False
    assert result["checks"]["canonical_urls"] is False


def test_quality_analysis_is_order_independent():
    first = make_paper("2610.12345")
    second = make_paper("2610.12346", "math.LO")

    forward = analyze_quality(make_snapshot([first, second]))
    reverse = analyze_quality(make_snapshot([second, first]))

    assert forward == reverse


@pytest.mark.parametrize(
    "snapshot",
    [
        {"schema_version": 2, "source": "arxiv", "papers": []},
        {"schema_version": 1, "source": "other", "papers": []},
        {"schema_version": 1, "source": "arxiv", "papers": []},
    ],
)
def test_invalid_snapshots_are_rejected(snapshot):
    with pytest.raises(ValueError):
        analyze_quality(snapshot)
