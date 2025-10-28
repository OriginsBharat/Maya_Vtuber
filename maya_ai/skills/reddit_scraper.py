import praw
from maya_ai.config.config_manager import ConfigManager
from maya_ai.skills.skill import Skill

class RedditScraperSkill(Skill):
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
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
            limit = kwargs.get("limit", 5)
            if not subreddit_name:
                return ["Error: subreddit_name is required."]
            return self._get_top_posts(subreddit_name, limit)
        return [f"Unknown action: {action_name}"]

    def _initialize_client(self):
        try:
            self.reddit = praw.Reddit(
                client_id=self.config_manager.get_key("REDDIT_CLIENT_ID"),
                client_secret=self.config_manager.get_key("REDDIT_CLIENT_SECRET"),
                user_agent="MayaAI by u/originsbharat",
            )
        except Exception as e:
            print(f"Failed to initialize Reddit client: {e}")

    def _get_top_posts(self, subreddit_name: str, limit: int = 5) -> list:
        if not self.reddit:
            return ["Reddit client is not initialized."]
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            top_posts = subreddit.top(time_filter="day", limit=limit)
            return [post.title for post in top_posts]
        except Exception as e:
            return [f"Error fetching from Reddit API: {e}"]

def create_skill(config_manager: ConfigManager):
    return RedditScraperSkill(config_manager)
