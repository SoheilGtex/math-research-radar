from unittest.mock import MagicMock, patch

from radar.fetchers.crossref import CrossrefFetcher, run_crossref_pipeline


def test_crossref_fetch_category_parsing():
    """
    Test that CrossrefFetcher correctly fetches and parses JSON responses
    without making real HTTP requests.
    """
    # 1. Create a dummy JSON dictionary mimicking the Crossref API response structure.
    # Note: Adjust the keys here if your actual Crossref parsing logic expects different nested fields.
    mock_json_data = {
        "message": {
            "items": [
                {
                    "DOI": "10.1000/math.2026.09.01",
                    "title": ["A Rigorous Proof on Stochastic Differential Equations"],
                    "created": {"date-time": "2026-09-01T14:30:00Z"},
                    "abstract": "We present a novel approach to solving SDEs...",
                    "URL": "http://dx.doi.org/10.1000/math.2026.09.01"
                }
            ]
        }
    }

    # 2. Instantiate the fetcher
    fetcher = CrossrefFetcher()
    
    # 3. Mock the 'session' object inherited from BaseFetcher
    mock_session = MagicMock()
    mock_response = MagicMock()
    
    # For JSON APIs, we mock the return value of the .json() method
    mock_response.json.return_value = mock_json_data
    mock_response.raise_for_status.return_value = None 
    mock_session.get.return_value = mock_response
    
    fetcher.session = mock_session

    # 4. Execute the method
    papers = fetcher.fetch_category("math.PR") # Probability

    # 5. Assertions: Verify parsing logic and Pydantic/Model generation
    assert len(papers) == 1
    # Check if the parsed ID matches the DOI logic in your fetcher
    assert papers[0].id == "10.1000/math.2026.09.01" 
    assert "Stochastic Differential Equations" in papers[0].title
    assert papers[0].category == "math.PR"
    # Ensure your fetcher tags Crossref papers correctly
    assert papers[0].source.lower() == "crossref" 
    
    # Verify the network call was simulated exactly once
    mock_session.get.assert_called_once()


@patch("radar.fetchers.crossref.CrossrefFetcher")
def test_run_crossref_pipeline_execution(mock_fetcher_class):
    """
    Test that the entrypoint function properly instantiates the Crossref fetcher
    and triggers the pipeline execution without hitting the DB.
    """
    mock_instance = MagicMock()
    mock_fetcher_class.return_value = mock_instance
    
    # Execute the entry point
    run_crossref_pipeline()
    
    # Verify initialization and method call
    mock_fetcher_class.assert_called_once()
    mock_instance.run_pipeline.assert_called_once()