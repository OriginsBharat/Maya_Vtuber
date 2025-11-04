import praw
from maya_ai.config.config_loader import get_config
from maya_ai.skills.skill import Skill
from loguru import logger

class RedditScraperSkill(Skill):
    def __init__(self):
        self.config = get_config()
        self.reddit = None
        self._initialize_client()

    def get_name(self) -> str:
        return "Reddit Scraper Skill"

    def get_possible_actions(self) -> list:
        return [
            {
                "name": "get_top_posts",
                "description": "Fetches top posts from a subreddit.",
                "args": {"subreddit_name": "string", "limit": "int"}
            }
        ]

    def perform_action(self, action_name: str, **kwargs) -> list:
        if action_name == "get_top_posts":
            subreddit_name = kwargs.get("subreddit_name")
            limit = kwargs.get("limit", self.config.get('skills', 'reddit', {}).get('default_limit', 5))
            if not subreddit_name:
                logger.error("subreddit_name is required for get_top_posts action.")
                return ["Error: subreddit_name is required."]
            return self._get_top_posts(subreddit_name, limit)
        logger.warning(f"Unknown action for Reddit Scraper Skill: {action_name}")
        return [f"Unknown action: {action_name}"]

    def _initialize_client(self):
        client_id = self.config.get_api_key('REDDIT_CLIENT_ID')
        client_secret = self.config.get_api_key('REDDIT_CLIENT_SECRET')

        if not client_id or not client_secret:
            logger.warning("REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variables not set. RedditScraperSkill will be disabled.")
            return

        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="MayaAI by u/originsbharat",
            )
            logger.info("Reddit client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}", exc_info=True)

    def _get_top_posts(self, subreddit_name: str, limit: int = 5) -> list:
        if not self.reddit:
            logger.error("Reddit client is not initialized.")
            return ["Reddit client is not initialized."]
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            top_posts = subreddit.top(time_filter="day", limit=limit)
            logger.info(f"Fetched top {limit} posts from r/{subreddit_name}")
            return [post.title for post in top_posts]
        except Exception as e:
            logger.error(f"Error fetching from Reddit API: {e}", exc_info=True)
            return [f"Error fetching from Reddit API: {e}"]

def create_skill(brain):
    return RedditScraperSkill()
