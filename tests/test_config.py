import json
import pytest
from scripts.fetch import load_config

def test_load_config_default_fallback(tmp_path, monkeypatch):
    """
    Test that default configurations are returned when config.json is missing.
    """
    # Change current working directory to an empty temporary directory
    monkeypatch.chdir(tmp_path)
    
    config = load_config()
    
    assert "categories" in config
    assert config["categories"] == ["math.NA", "math.LO"]
    assert config["max_results_per_category"] == 3
    assert config["timeout_seconds"] == 10

def test_load_config_valid_file(tmp_path, monkeypatch):
    """
    Test that configurations are correctly loaded from an existing config.json.
    """
    monkeypatch.chdir(tmp_path)
    
    # Create a mock config.json in the temporary directory
    mock_config = {
        "categories": ["math.PR", "math.ST"],
        "max_results_per_category": 10,
        "timeout_seconds": 20
    }
    
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(mock_config, f)
        
    config = load_config()
    
    assert config["categories"] == ["math.PR", "math.ST"]
    assert config["max_results_per_category"] == 10
    assert config["timeout_seconds"] == 20