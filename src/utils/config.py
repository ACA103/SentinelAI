import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigManager:
    """
    Singleton Configuration Manager that loads YAML configurations
    based on the SENTINEL_ENV environment variable.
    """
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        env = os.getenv("SENTINEL_ENV", "development")
        
        # Determine the project root assuming this file is in src/utils/
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / env / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def get(self, key_path: str, default=None):
        """
        Retrieve a configuration value using dot-notation.
        Example: config.get("paths.raw_data")
        """
        keys = key_path.split('.')
        val = self._config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
