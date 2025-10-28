import os
from supabase import create_client, Client
from dotenv import load_dotenv

class ConfigManager:
    """
    Manages API keys and other configuration secrets.
    It first tries to load keys from environment variables.
    If not found, it falls back to a Supabase 'config' table.
    """
    def __init__(self):
        # Explicitly load the .env file from the project root
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        load_dotenv(dotenv_path=dotenv_path)

        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            print(f"Warning: Could not connect to Supabase. Falling back to environment variables only. Error: {e}")
            self.supabase = None
        self.cache = {}

    def get_key(self, key_name: str) -> str:
        """
        Retrieves a key. First checks the local cache, then environment variables,
        then falls back to Supabase.
        """
        if key_name in self.cache:
            return self.cache[key_name]

        value = os.environ.get(key_name)
        if value:
            self.cache[key_name] = value
            return value

        try:
            response = self.supabase.table('config').select('value').eq('key', key_name).execute()
            if response.data:
                value = response.data[0]['value']
                self.cache[key_name] = value
                return value
        except Exception as e:
            print(f"Could not fetch '{key_name}' from Supabase: {e}")
            return None

        print(f"Warning: Key '{key_name}' not found in any configuration source.")
        return None
