import praw
import os

def get_top_reddit_posts(subreddit_name: str, limit: int = 5) -> list:
    """
    Fetches the titles of the top posts from a given subreddit using the Reddit API.

    Args:
        subreddit_name: The name of the subreddit.
        limit: The number of posts to return.

    Returns:
        A list of post titles, or an error message if it fails.
    """
    try:
        # These credentials need to be set as environment variables by the user
        reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET"),
            user_agent="MayaAI by u/originsbharat",
        )

        subreddit = reddit.subreddit(subreddit_name)

        # Fetch top posts from the last 24 hours
        top_posts = subreddit.top(time_filter="day", limit=limit)

        return [post.title for post in top_posts]

    except Exception as e:
        print(f"An error occurred while fetching from Reddit API: {e}")
        return [f"I'm having trouble connecting to the Reddit API. The error is: {e}"]

# Example usage (for testing)
if __name__ == '__main__':
    # To run this test, you must set the REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET
    # environment variables.
    if os.environ.get("REDDIT_CLIENT_ID"):
        print(f"--- Fetching top 5 posts from r/memes ---")
        memes = get_top_reddit_posts("memes", 5)
        for i, meme_title in enumerate(memes):
            print(f"{i+1}. {meme_title}")
    else:
        print("Skipping Reddit test because REDDIT_CLIENT_ID is not set.")
        print("Please set your Reddit API credentials as environment variables to test this.")
