import praw
from maya_ai.config.config_manager import ConfigManager

def get_top_reddit_posts(subreddit_name: str, config_manager: ConfigManager, limit: int = 5) -> list:
    """
    Fetches the titles of the top posts from a given subreddit using the Reddit API.
    """
    try:
        reddit = praw.Reddit(
            client_id=config_manager.get_key("REDDIT_CLIENT_ID"),
            client_secret=config_manager.get_key("REDDIT_CLIENT_SECRET"),
            user_agent="MayaAI by u/originsbharat",
        )

        subreddit = reddit.subreddit(subreddit_name)
        top_posts = subreddit.top(time_filter="day", limit=limit)

        return [post.title for post in top_posts]

    except Exception as e:
        print(f"An error occurred while fetching from Reddit API: {e}")
        return [f"I'm having trouble connecting to the Reddit API. The error is: {e}"]

# Example usage will now be handled in the main UI file,
# as this module now depends on the ConfigManager.
