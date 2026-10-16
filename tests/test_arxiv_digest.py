import pytest
from radar.reporting.arxiv_digest import render_digest


def sample_papers():
    return [
        {
            "arxiv_id": "2610.12345",
            "title": "Numerical | Analysis",
            "published": "2026-10-16T09:00:00Z",
            "url": "https://arxiv.org/abs/2610.12345",
            "categories": ["math.NA", "math.LO"],
        },
        {
            "arxiv_id": "2610.12346",
            "title": "Computational Mathematics",
            "published": "2026-10-15T09:00:00Z",
            "url": "https://arxiv.org/abs/2610.12346",
            "categories": ["math.NA"],
        },
    ]


def test_digest_statistics_and_links():
    snapshot = {"papers": sample_papers()}
    digest = render_digest(snapshot)

    assert "Unique papers: **2**" in digest
    assert "Cross-category papers: **1**" in digest
    assert "Research categories: **2**" in digest

    assert "| math.NA | 2 |" in digest
    assert "| math.LO | 1 |" in digest

    assert "Numerical \\| Analysis" in digest
    assert "https://arxiv.org/abs/2610.12345" in digest


def test_digest_is_order_independent():
    papers = sample_papers()

    first = render_digest({"papers": papers})
    second = render_digest({"papers": list(reversed(papers))})

    assert first == second


def test_empty_digest_rejected():
    with pytest.raises(ValueError):
        render_digest({"papers": []})
