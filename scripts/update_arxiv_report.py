"""Generate a version-controlled arXiv research report."""

import argparse
import time
from pathlib import Path
from typing import Sequence

from radar.analytics.quality import analyze_quality
from radar.config import settings
from radar.fetchers.arxiv import ArxivFetcher
from radar.reporting.arxiv_digest import render_digest, write_digest
from radar.reporting.arxiv_snapshot import build_snapshot, write_snapshot


def generate_report(
    fetcher: ArxivFetcher,
    categories: Sequence[str],
    output: Path,
) -> bool:
    """Fetch, validate and save a deterministic research snapshot."""

    if not categories:
        raise ValueError("No research categories configured.")

    papers = []

    for index, category in enumerate(categories):
        if index > 0:
            time.sleep(fetcher.rate_limit_delay)

        batch = fetcher.fetch_category(category)

        if not batch:
            raise RuntimeError(
                f"No papers returned for {category}; report preserved."
            )

        papers.extend(batch)

    snapshot = build_snapshot(papers)
    quality = analyze_quality(snapshot)

    if not all(quality["checks"].values()):
        raise ValueError("Research snapshot failed integrity checks")

    digest = render_digest(snapshot)

    json_changed = write_snapshot(output, snapshot)
    markdown_changed = write_digest(output.with_suffix(".md"), digest)
    quality_changed = write_snapshot(
        output.with_name("quality.json"), quality
    )

    return json_changed or markdown_changed or quality_changed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an arXiv research snapshot."
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/arxiv/latest.json"),
    )

    args = parser.parse_args()

    changed = generate_report(
        fetcher=ArxivFetcher(),
        categories=settings.categories,
        output=args.output,
    )

    print("REPORT_UPDATED" if changed else "REPORT_UNCHANGED")


if __name__ == "__main__":
    main()
