import pytest
from radar.reporting import readme as readme_module


class FakeSession:
    def query(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def limit(self, *_args):
        return self

    def all(self):
        return []

    def close(self):
        pass


@pytest.fixture
def isolated_readme(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        readme_module,
        "SessionLocal",
        FakeSession,
    )
    return tmp_path / "README.md"


def test_unmarked_readme_is_preserved(isolated_readme):
    original = "# Mathematical Research Intelligence\n\nDocumentation.\n"
    isolated_readme.write_text(original, encoding="utf-8")

    readme_module.generate_readme()

    assert isolated_readme.read_text(encoding="utf-8") == original


def test_reversed_markers_are_preserved(isolated_readme):
    original = (
        "# Project\n"
        "<!-- LATEST_PAPERS_END -->\n"
        "Documentation\n"
        "<!-- LATEST_PAPERS_START -->\n"
    )
    isolated_readme.write_text(original, encoding="utf-8")

    readme_module.generate_readme()

    assert isolated_readme.read_text(encoding="utf-8") == original


def test_marked_section_updates_only_expected_content(isolated_readme):
    start = "<!-- LATEST_PAPERS_START -->"
    end = "<!-- LATEST_PAPERS_END -->"

    original = f"HEADER\n{start}\nOld papers\n{end}\nFOOTER\n"
    isolated_readme.write_text(original, encoding="utf-8")

    readme_module.generate_readme()

    expected = (
        f"HEADER\n{start}\n"
        "### 📄 Latest Discovered Papers\n\n"
        "*No papers found in the database yet.*\n\n"
        f"{end}\nFOOTER\n"
    )

    assert isolated_readme.read_text(encoding="utf-8") == expected

    readme_module.generate_readme()
    assert isolated_readme.read_text(encoding="utf-8") == expected
