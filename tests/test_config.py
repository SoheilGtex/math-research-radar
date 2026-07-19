import json

from radar.config import load_config


def test_load_config_default_fallback(tmp_path, monkeypatch):
    """
    Test that default structured configurations are returned when config.json is missing.
    """
    monkeypatch.chdir(tmp_path)
    
    config = load_config("config.json")
    
    # Asserting attributes instead of dictionary keys
    assert config.categories == ["math.NA", "math.LO"]
    assert config.max_results_per_category == 5
    assert config.timeout_seconds == 15
    assert config.papers_dir == "papers"

def test_load_config_valid_file(tmp_path, monkeypatch):
    """
    Test that configurations are correctly loaded and mapped to the RadarConfig object.
    """
    monkeypatch.chdir(tmp_path)
    
    mock_config = {
        "categories": ["math.PR", "math.ST"],
        "max_results_per_category": 10,
        "timeout_seconds": 20
    }
    
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(mock_config, f)
        
    config = load_config("config.json")
    
    assert config.categories == ["math.PR", "math.ST"]
    assert config.max_results_per_category == 10
    assert config.timeout_seconds == 20