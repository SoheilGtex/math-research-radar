import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from scripts.update_arxiv_report import generate_report


def make_paper(identifier, category):
    return SimpleNamespace(
        id=f"https://arxiv.org/abs/{identifier}",
        title="Numerical Research",
        published="2026-10-16T09:00:00Z",
        summary="Research summary.",
        category=category,
        source="arxiv",
    )


def make_fetcher(responses):
    fetcher = Mock()
    fetcher.rate_limit_delay = 0
    fetcher.fetch_category.side_effect = responses
    return fetcher


def test_successful_report_generation(tmp_path):
    output = tmp_path / "latest.json"
    fetcher = make_fetcher([
        [make_paper("2610.12345v1", "math.NA")],
        [make_paper("2610.12346v1", "math.LO")],
    ])

    with patch("scripts.update_arxiv_report.time.sleep"):
        changed = generate_report(
            fetcher, ["math.NA", "math.LO"], output
        )

    assert changed is True

    data = json.loads(output.read_text(encoding="utf-8"))
    assert len(data["papers"]) == 2
    assert data["source"] == "arxiv"
    assert fetcher.fetch_category.call_count == 2


def test_network_failure_preserves_previous_report(tmp_path):
    output = tmp_path / "latest.json"
    original = '{"previous": true}\n'
    output.write_text(original, encoding="utf-8")

    fetcher = make_fetcher([
        [make_paper("2610.12345v1", "math.NA")],
        RuntimeError("Network unavailable"),
    ])

    with patch("scripts.update_arxiv_report.time.sleep"):
        with pytest.raises(RuntimeError, match="Network unavailable"):
            generate_report(fetcher, ["math.NA", "math.LO"], output)

    assert output.read_text(encoding="utf-8") == original


def test_empty_category_preserves_previous_report(tmp_path):
    output = tmp_path / "latest.json"
    output.write_text('{"previous": true}\n', encoding="utf-8")

    fetcher = make_fetcher([
        [make_paper("2610.12345v1", "math.NA")],
        [],
    ])

    with patch("scripts.update_arxiv_report.time.sleep"):
        with pytest.raises(RuntimeError, match="No papers returned"):
            generate_report(fetcher, ["math.NA", "math.LO"], output)

    assert json.loads(output.read_text()) == {"previous": True}


def test_repeated_data_does_not_rewrite_report(tmp_path):
    output = tmp_path / "latest.json"
    paper = make_paper("2610.12345v1", "math.NA")

    fetcher = make_fetcher([[paper], [paper]])

    assert generate_report(fetcher, ["math.NA"], output) is True
    first_content = output.read_bytes()

    assert generate_report(fetcher, ["math.NA"], output) is False
    assert output.read_bytes() == first_content


def test_missing_categories_fails_without_fetching(tmp_path):
    fetcher = make_fetcher([])
    output = tmp_path / "latest.json"

    with pytest.raises(ValueError, match="No research categories"):
        generate_report(fetcher, [], output)

    assert not output.exists()
    fetcher.fetch_category.assert_not_called()


def test_markdown_report_is_generated_and_stable(tmp_path):
    output = tmp_path / "latest.json"
    sample = make_paper("2610.12345v1", "math.NA")
    fetcher = make_fetcher([[sample], [sample]])

    assert generate_report(fetcher, ["math.NA"], output) is True

    markdown = output.with_suffix(".md")
    assert markdown.is_file()

    content = markdown.read_text(encoding="utf-8")
    assert "# arXiv Research Radar" in content
    assert "Unique papers: **1**" in content
    assert "Numerical Research" in content
    assert "https://arxiv.org/abs/2610.12345" in content

    assert generate_report(fetcher, ["math.NA"], output) is False
    assert markdown.read_text(encoding="utf-8") == content
