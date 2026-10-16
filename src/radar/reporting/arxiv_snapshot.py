"""Deterministic, database-independent arXiv research snapshots."""

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Iterable, Protocol
from urllib.parse import urlparse


class PaperLike(Protocol):
    id: str
    title: str
    published: str
    summary: str
    category: str
    source: str


def build_snapshot(papers: Iterable[PaperLike]) -> dict:
    """Validate and deduplicate arXiv records without a database."""
    records = {}

    for paper in papers:
        parsed = urlparse(str(paper.id).strip())

        if (
            parsed.hostname not in
            {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}
            or not parsed.path.startswith("/abs/")
        ):
            raise ValueError(f"Invalid arXiv identifier: {paper.id!r}")

        if parsed.scheme not in {"http", "https"} or parsed.query or parsed.fragment:
            raise ValueError(f"Invalid arXiv URL: {paper.id!r}")

        raw_id = parsed.path[len("/abs/"):]
        pattern = (
            r"(?:\d{4}\.\d{4,5}|[a-z][a-z.-]*/\d{7})"
            r"(?:v[1-9]\d*)?"
        )
        if not re.fullmatch(pattern, raw_id):
            raise ValueError(f"Invalid arXiv identifier: {paper.id!r}")

        arxiv_id = re.sub(r"v[1-9]\d*$", "", raw_id)

        title = " ".join(str(paper.title).split())
        published = str(paper.published).strip()
        category = str(paper.category).strip()

        if not all((arxiv_id, title, published, category)):
            raise ValueError(f"Incomplete paper metadata: {paper.id!r}")

        if str(paper.source).lower() != "arxiv":
            raise ValueError(f"Unexpected paper source: {paper.source!r}")

        match = re.search(r"v([1-9][0-9]*)$", raw_id)
        version = int(match.group(1)) if match else None

        candidate = {
            "arxiv_id": arxiv_id,
            "version": version,
            "title": title,
            "published": published,
            "summary": " ".join(str(paper.summary or "").split()),
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "categories": [category],
        }

        previous = records.get(arxiv_id)

        if previous is None:
            records[arxiv_id] = candidate
        else:
            categories = sorted(set(previous["categories"] + [category]))

            def priority(record):
                return (
                    record["version"] or 0,
                    record["published"],
                    record["title"],
                    record["summary"],
                )

            selected = max((previous, candidate), key=priority)
            selected["categories"] = categories
            records[arxiv_id] = selected

    if not records:
        raise ValueError("No valid papers received; existing reports preserved.")

    for record in records.values():
        record["categories"].sort()

    ordered = sorted(
        records.values(),
        key=lambda item: (item["published"], item["arxiv_id"]),
        reverse=True,
    )

    return {
        "schema_version": 1,
        "source": "arxiv",
        "papers": ordered,
    }


def write_snapshot(path: Path, snapshot: dict) -> bool:
    """Atomically replace the report only when its content changes."""
    content = json.dumps(
        snapshot,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"

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
