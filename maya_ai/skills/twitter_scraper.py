import tweepy
from maya_ai.config.config_loader import get_config
from maya_ai.skills.skill import Skill
from loguru import logger

class TwitterScraperSkill(Skill):
    def __init__(self):
        self.config = get_config()
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
            limit = kwargs.get("limit", self.config.get('skills', 'twitter', {}).get('default_limit', 5))
            if not username:
                logger.error("username is required for get_user_tweets action.")
                return ["Error: username is required."]
            return self._get_user_tweets(username, limit)
        logger.warning(f"Unknown action for Twitter Scraper Skill: {action_name}")
        return [f"Unknown action: {action_name}"]

    def _initialize_client(self):
        bearer_token = self.config.get_api_key('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            logger.warning("TWITTER_BEARER_TOKEN environment variable not set. TwitterScraperSkill will be disabled.")
            return

        try:
            self.client = tweepy.Client(bearer_token)
            logger.info("Twitter client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}", exc_info=True)

    def _get_user_tweets(self, username: str, limit: int = 5) -> list:
        if not self.client:
            logger.error("Twitter client is not initialized.")
            return ["Twitter client is not initialized."]
        try:
            user = self.client.get_user(username=username).data
            if not user:
                logger.warning(f"Could not find Twitter user: {username}")
                return [f"Could not find Twitter user: {username}"]
            response = self.client.get_users_tweets(user.id, max_results=limit)
            tweets = response.data
            if not tweets:
                logger.info(f"No recent tweets from {username}.")
                return [f"No recent tweets from {username}."]
            logger.info(f"Fetched {len(tweets)} tweets from @{username}")
            return [tweet.text for tweet in tweets]
        except Exception as e:
            logger.error(f"Error fetching from Twitter API: {e}", exc_info=True)
            return [f"Error fetching from Twitter API: {e}"]

def create_skill():
    return TwitterScraperSkill()
