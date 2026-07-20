import json
import logging
import os
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class RadarConfig:
    """Structured configuration object for the Radar platform."""
    categories: List[str] = field(default_factory=lambda: ["math.NA", "math.LO"])
    max_results_per_category: int = 5
    timeout_seconds: int = 15
    
    papers_dir: str = "papers"
    stats_dir: str = "stats"
    docs_dir: str = "docs"
    cache_dir: str = "cache"  # <-- فیلد جدید اضافه شد

def load_config(config_path: str = "config.json") -> RadarConfig:
    """Load configuration settings from a JSON file and return a structured object."""
    if not os.path.exists(config_path):
        logger.warning(f"Config file {config_path} not found. Using defaults.")
        return RadarConfig()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return RadarConfig(
                categories=data.get("categories", ["math.NA", "math.LO"]),
                max_results_per_category=data.get("max_results_per_category", 5),
                timeout_seconds=data.get("timeout_seconds", 15)
            )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {config_path}: {e}. Using defaults.")
        return RadarConfig()

settings = load_config()