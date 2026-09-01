from unittest.mock import MagicMock, patch
from radar.fetchers.arxiv import fetch_arxiv_papers, run_arxiv_pipeline


def test_fetch_arxiv_papers_parsing():
    """
    Test that fetch_arxiv_papers correctly parses an Atom feed response
    without making an actual network call.
    """
    # 1. Create a dummy XML feed structure mimicking arXiv
    mock_feed_content = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2609.12345v1</id>
        <title>Rigorous Numerical Analysis of Navier-Stokes</title>
        <summary>A detailed proof on global regularity.</summary>
        <published>2026-09-01T12:00:00Z</published>
        <link href="http://arxiv.org/abs/2609.12345v1" rel="alternate" type="text/html"/>
        <author><name>Terence Tao</name></author>
      </entry>
    </feed>
    """

    # 2. Patch requests.get to return our dummy XML
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_feed_content.encode("utf-8")
        mock_get.return_value = mock_response

        papers = fetch_arxiv_papers(category="math.NA", max_results=1)

        # 3. Assertions
        assert len(papers) == 1
        assert papers[0]["id"] == "http://arxiv.org/abs/2609.12345v1"
        assert papers[0]["title"] == "Rigorous Numerical Analysis of Navier-Stokes"
        assert papers[0]["category"] == "math.NA"
        assert papers[0]["source"] == "arXiv"
        mock_get.assert_called_once()


def test_run_arxiv_pipeline_db_isolation():
    """
    Test that run_arxiv_pipeline processes records and calls DB session
    without requiring a live PostgreSQL instance.
    """
    dummy_papers = [
        {
            "id": "2609.99999",
            "title": "Spectral Graph Theory Invariants",
            "published": "2026-09-01",
            "summary": "Eigenvalue bounds on Riemannian manifolds.",
            "link": "https://arxiv.org/abs/2609.99999",
            "category": "math.SP",
            "source": "arXiv",
        }
    ]

    with patch("radar.fetchers.arxiv.fetch_arxiv_papers", return_value=dummy_papers), \
         patch("radar.fetchers.arxiv.SessionLocal") as mock_session_cls, \
         patch("radar.fetchers.arxiv.save_papers_to_json"):  # Prevent local disk writes

        mock_db = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_db
        # Mocking query to simulate that the paper is NOT yet in the DB
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Execute
        run_arxiv_pipeline()

        # Verify DB interaction occurred
        assert mock_db.add.called
        assert mock_db.commit.called