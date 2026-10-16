from types import SimpleNamespace

import pytest
from radar.reporting.arxiv_snapshot import build_snapshot, write_snapshot


def paper(identifier, category="math.NA"):
    return SimpleNamespace(
        id=identifier,
        title="  Numerical   Methods  ",
        published="2026-10-16T09:00:00Z",
        summary="A research paper.",
        category=category,
        source="arxiv",
    )


def test_valid_snapshot():
    snapshot = build_snapshot([
        paper("https://arxiv.org/abs/2610.12345v1")
    ])

    assert snapshot["schema_version"] == 1
    assert len(snapshot["papers"]) == 1

    result = snapshot["papers"][0]
    assert result["arxiv_id"] == "2610.12345"
    assert result["title"] == "Numerical Methods"
    assert result["url"] == "https://arxiv.org/abs/2610.12345"


def test_deduplication_and_categories():
    snapshot = build_snapshot([
        paper("https://arxiv.org/abs/2610.12345v1", "math.NA"),
        paper("https://arxiv.org/abs/2610.12345v2", "math.LO"),
    ])

    assert len(snapshot["papers"]) == 1
    assert snapshot["papers"][0]["categories"] == [
        "math.LO", "math.NA"
    ]


def test_snapshot_write_is_idempotent(tmp_path):
    destination = tmp_path / "snapshot.json"
    snapshot = build_snapshot([
        paper("https://arxiv.org/abs/2610.12345v1")
    ])

    assert write_snapshot(destination, snapshot) is True
    first_content = destination.read_bytes()

    assert write_snapshot(destination, snapshot) is False
    assert destination.read_bytes() == first_content


def test_invalid_and_empty_inputs():
    with pytest.raises(ValueError):
        build_snapshot([])

    with pytest.raises(ValueError):
        build_snapshot([
            paper("https://example.com/not-arxiv")
        ])


@pytest.mark.parametrize("identifier", [
    "https://arxiv.org/abs/invalid-paper",
    "https://arxiv.org/abs/2610.12345/extra",
    "https://arxiv.org/abs/2610.12345v0",
    "https://arxiv.org/abs/2610.12345?download=1",
    "ftp://arxiv.org/abs/2610.12345",
])
def test_malformed_arxiv_ids(identifier):
    with pytest.raises(ValueError):
        build_snapshot([paper(identifier)])


def test_legacy_arxiv_identifier():
    snapshot = build_snapshot([
        paper("http://arxiv.org/abs/math/0309136v2")
    ])

    assert snapshot["papers"][0]["arxiv_id"] == "math/0309136"
    assert snapshot["papers"][0]["url"] == (
        "https://arxiv.org/abs/math/0309136"
    )


def test_newest_version_is_order_independent():
    older = paper("https://arxiv.org/abs/2610.12345v1", "math.NA")
    older.title = "Original Research"

    newer = paper("https://arxiv.org/abs/2610.12345v3", "math.LO")
    newer.title = "Revised Research"

    first = build_snapshot([older, newer])
    second = build_snapshot([newer, older])

    assert first == second
    assert len(first["papers"]) == 1

    result = first["papers"][0]
    assert result["version"] == 3
    assert result["title"] == "Revised Research"
    assert result["categories"] == ["math.LO", "math.NA"]


def test_atomic_write_failure_preserves_previous_report(
    tmp_path, monkeypatch
):
    import os

    destination = tmp_path / "snapshot.json"
    destination.write_text('{"old": true}\n', encoding="utf-8")

    def failed_replace(source, target):
        raise OSError("Simulated replacement failure")

    monkeypatch.setattr(os, "replace", failed_replace)

    snapshot = build_snapshot([
        paper("https://arxiv.org/abs/2610.12345v1")
    ])

    with pytest.raises(OSError, match="Simulated"):
        write_snapshot(destination, snapshot)

    assert destination.read_text(encoding="utf-8") == (
        '{"old": true}\n'
    )

    assert list(tmp_path.glob("*.tmp")) == []
