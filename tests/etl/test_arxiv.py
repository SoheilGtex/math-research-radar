from unittest.mock import MagicMock, patch
from radar.fetchers.arxiv import ArxivFetcher, run_arxiv_pipeline

def test_arxiv_fetch_category_parsing():
    """
    Test that ArxivFetcher correctly fetches and parses an Atom feed
    without making real HTTP requests.
    """
    # 1. Create a dummy XML feed mimicking the arXiv API response
    mock_feed_content = b"""<?xml version="1.0" encoding="UTF-8"?>
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

    # 2. Instantiate the fetcher
    fetcher = ArxivFetcher()
    
    # 3. Mock the 'session' object inherited from BaseFetcher
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.content = mock_feed_content
    # Ensure raise_for_status doesn't throw an error
    mock_response.raise_for_status.return_value = None 
    mock_session.get.return_value = mock_response
    
    fetcher.session = mock_session

    # 4. Execute the method
    papers = fetcher.fetch_category("math.NA")

    # 5. Assertions: Verify parsing logic and Pydantic/Model generation
    assert len(papers) == 1
    assert papers[0].id == "http://arxiv.org/abs/2609.12345v1"
    assert papers[0].title == "Rigorous Numerical Analysis of Navier-Stokes"
    assert papers[0].category == "math.NA"
    assert papers[0].source == "arxiv"
    
    # Verify that the mocked session was actually called
    mock_session.get.assert_called_once()


@patch("radar.fetchers.arxiv.ArxivFetcher")
def test_run_arxiv_pipeline_execution(mock_fetcher_class):
    """
    Test that the entrypoint function properly instantiates the fetcher
    and triggers the pipeline execution without hitting the DB.
    """
    # Create a mock instance that will be returned when ArxivFetcher() is called
    mock_instance = MagicMock()
    mock_fetcher_class.return_value = mock_instance
    
    # Execute the entry point
    run_arxiv_pipeline()
    
    # Verify initialization and method call
    mock_fetcher_class.assert_called_once()
    mock_instance.run_pipeline.assert_called_once()