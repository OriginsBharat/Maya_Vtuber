import tweepy
from maya_ai.config.config_manager import ConfigManager
from maya_ai.skills.skill import Skill

class TwitterScraperSkill(Skill):
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.client = None
        self._initialize_client()

    def get_name(self) -> str:
        return "Twitter Scraper Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "get_user_tweets",
                "description": "Fetches tweets from a user's timeline.",
                "args": {"username": "string", "limit": "int"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> list:
        if action_name == "get_user_tweets":
            username = kwargs.get("username")
            limit = kwargs.get("limit", 5)
            if not username:
                return ["Error: username is required."]
            return self._get_user_tweets(username, limit)
        return [f"Unknown action: {action_name}"]

    def _initialize_client(self):
        try:
            bearer_token = self.config_manager.get_key("TWITTER_BEARER_TOKEN")
            self.client = tweepy.Client(bearer_token)
        except Exception as e:
            print(f"Failed to initialize Twitter client: {e}")

    def _get_user_tweets(self, username: str, limit: int = 5) -> list:
        if not self.client:
            return ["Twitter client is not initialized."]
        try:
            user = self.client.get_user(username=username).data
            if not user:
                return [f"Could not find Twitter user: {username}"]
            response = self.client.get_users_tweets(user.id, max_results=limit)
            tweets = response.data
            if not tweets:
                return [f"No recent tweets from {username}."]
            return [tweet.text for tweet in tweets]
        except Exception as e:
            return [f"Error fetching from Twitter API: {e}"]

def create_skill(config_manager: ConfigManager):
    return TwitterScraperSkill(config_manager)
