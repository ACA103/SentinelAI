import os
from src.utils.config import ConfigManager

def test_actual_config():
    """Verify that the ConfigManager correctly loads the YAML file."""
    os.environ["SENTINEL_ENV"] = "development"
    
    # Reset singleton instance to ensure clean state for testing
    ConfigManager._instance = None 
    cm = ConfigManager()
    
    assert cm.get("app.name") == "SentinelAI"
    assert cm.get("app.environment") == "development"
    assert cm.get("paths.raw_data") == "data/raw"
    assert cm.get("duckdb.threads") == 4
    
    # Test non-existent key fallback
    assert cm.get("invalid.key.path", "fallback") == "fallback"
