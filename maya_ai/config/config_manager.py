import os
from supabase import create_client, Client

class ConfigManager:
    """
    Manages the secure retrieval of API keys and configuration from a cloud vault (Supabase).
    """
    def __init__(self):
        """
        Initializes the ConfigManager and connects to Supabase.
        """
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.config_cache = {}
        self._load_config()

    def _load_config(self):
        """
        Loads all key-value pairs from the 'config' table in Supabase into a local cache.
        """
        try:
            response = self.client.table('config').select('*').execute()
            if response.data:
                for item in response.data:
                    self.config_cache[item['key']] = item['value']
                print("Successfully loaded configuration from cloud vault.")
        except Exception as e:
            print(f"Error loading configuration from Supabase: {e}")
            raise

    def get_key(self, key_name: str) -> str:
        """
        Retrieves a secret key from the cached configuration.

        Args:
            key_name: The name of the key to retrieve (e.g., "REDDIT_CLIENT_ID").

        Returns:
            The value of the secret key, or None if not found.
        """
        return self.config_cache.get(key_name)

# Example Usage (for testing)
if __name__ == '__main__':
    # To run this test, you must have a Supabase project with a 'config' table
    # containing 'key' and 'value' columns. You must also set the
    # SUPABASE_URL and SUPABASE_KEY environment variables.

    if os.environ.get("SUPABASE_URL"):
        print("--- Testing ConfigManager ---")
        try:
            config_manager = ConfigManager()

            # Try to get a key that should exist
            reddit_id = config_manager.get_key("REDDIT_CLIENT_ID")
            if reddit_id:
                print(f"Successfully retrieved REDDIT_CLIENT_ID: {reddit_id[:4]}... (truncated)")
            else:
                print("Could not retrieve REDDIT_CLIENT_ID. Make sure it exists in your Supabase table.")

        except ValueError as e:
            print(f"Configuration error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("Skipping ConfigManager test because SUPABASE_URL is not set.")
