"""Deterministic Markdown analytics for arXiv snapshots."""

import os
import tempfile
from collections import Counter
from pathlib import Path


def render_digest(snapshot: dict, limit: int = 10) -> str:
    """Produce a reproducible summary from validated snapshot data."""
    papers = snapshot["papers"]

    if not papers:
        raise ValueError("Cannot generate a digest from empty data.")

    counts = Counter(
        category
        for paper in papers
        for category in paper["categories"]
    )

    cross_listed = sum(
        len(paper["categories"]) > 1
        for paper in papers
    )

    lines = [
        "# arXiv Research Radar",
        "",
        "Automated research snapshot based on arXiv metadata.",
        "",
        "## Research Coverage",
        "",
        f"- Unique papers: **{len(papers)}**",
        f"- Cross-category papers: **{cross_listed}**",
        f"- Research categories: **{len(counts)}**",
        "",
        "## Category Distribution",
        "",
        "| Category | Papers |",
        "|---|---:|",
    ]

    for category, count in sorted(counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend([
        "",
        "## Most Recent Papers",
        "",
        "| Published | Paper | Categories |",
        "|---|---|---|",
    ])

    ordered = sorted(
        papers,
        key=lambda paper: (
            paper["published"],
            paper["arxiv_id"],
        ),
        reverse=True,
    )

    for paper in ordered[:limit]:
        title = (
            paper["title"]
            .replace("\\", "\\\\")
            .replace("|", "\\|")
            .replace("[", "\\[")
            .replace("]", "\\]")
        )

        lines.append(
            f'| {paper["published"][:10]} '
            f'| [{title}]({paper["url"]}) '
            f'| {", ".join(paper["categories"])} |'
        )

    lines.extend([
        "",
        "## Methodology",
        "",
        "- Source: arXiv API.",
        "- Records are deduplicated by canonical arXiv identifier.",
        "- Category counts can overlap for cross-listed papers.",
        "- This is a limited recent-paper snapshot, not an exhaustive literature review.",
        "- The report changes only when its underlying research data changes.",
        "",
    ])

    return "\n".join(lines)


def write_digest(path: Path, content: str) -> bool:
    """Atomically write Markdown only when content changes."""
    if not content.endswith("\n"):
        content += "\n"

    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())

        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return True
