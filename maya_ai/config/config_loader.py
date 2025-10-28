import yaml
from pathlib import Path
import sys
from loguru import logger
import os
from dotenv import load_dotenv

_config_instance = None

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"FATAL: Configuration file not found at '{config_path}'. Please create it.")
            sys.exit(1)

        # Load environment variables from .env file
        load_dotenv()

        self._create_directories()

    def get(self, section: str, key: str, default=None):
        """
        Retrieves a value from the config.
        Example: config.get('brain', 'model')
        """
        return self._config.get(section, {}).get(key, default)

    def get_api_key(self, key_name: str):
        """
        Retrieves an API key from environment variables.
        Example: config.get_api_key('PINECONE_API_KEY')
        """
        return os.getenv(key_name)

    def _create_directories(self):
        """
        Creates all directories specified in the 'paths' section of the config.
        """
        paths = self._config.get('paths', {})
        for path_name, path_value in paths.items():
            try:
                Path(path_value).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create directory '{path_value}' for '{path_name}'. Error: {e}")


    @property
    def brain_model(self):
        return self.get('brain', 'model')

    @property
    def log_level(self):
        return self.get('logging', 'level', 'INFO')

    @property
    def log_file(self):
        return self.get('logging', 'file', 'logs/maya.log')

def get_config(config_path: str = "config.yaml") -> 'Config':
    """
    Returns a singleton instance of the Config class.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
