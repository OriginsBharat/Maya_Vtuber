import os
import praw
import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
# We will need to add REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT
load_dotenv()

class WebScraper:
    """
    Scrapes web content, currently focused on Reddit.
    """
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
        )
        logger.info("🌐 Web Scraper initialized for Reddit.")

    def find_top_image_post(self, search_term: str) -> dict:
        """
        Finds the top image post from a subreddit or by a keyword search.

        Args:
            search_term: The subreddit (e.g., "r/memes") or keyword (e.g., "cats").

        Returns:
            A dictionary containing the post title, image URL, and post URL,
            or None if no suitable post is found.
        """
        logger.info(f"Searching for top image post with term: '{search_term}'")

        # Determine if the search term is a subreddit or a keyword
        if search_term.lower().startswith('r/'):
            subreddit_name = search_term[2:]
            posts = self.reddit.subreddit(subreddit_name).hot(limit=10)
        else:
            # For keywords, we can search across a list of general-purpose SFW subreddits
            # This list can be expanded.
            popular_subreddits = ["pics", "memes", "aww", "mildlyinteresting"]
            search_query = f"title:({search_term})"
            posts = self.reddit.subreddit("all").search(search_query, sort="hot", limit=25)

        for post in posts:
            # We want image posts that are not videos and are SFW
            if not post.is_video and not post.over_18 and hasattr(post, 'url') and post.url.endswith(('jpg', 'jpeg', 'png')):
                logger.info(f"Found suitable post: {post.title}")
                return {
                    "title": post.title,
                    "image_url": post.url,
                    "post_url": post.shortlink
                }

        logger.warning("No suitable image post found.")
        return None

    def download_image(self, image_url: str, save_path: str) -> str:
        """Downloads an image from a URL to a local path."""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Image downloaded successfully to {save_path}")
            return save_path
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading image: {e}", exc_info=True)
            return None