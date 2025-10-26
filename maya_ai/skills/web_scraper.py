import requests
from bs4 import BeautifulSoup

def get_top_reddit_posts(subreddit: str, limit: int = 5) -> list:
    """
    Fetches the titles of the top posts from a given subreddit.

    Args:
        subreddit: The name of the subreddit to scrape.
        limit: The maximum number of post titles to return.

    Returns:
        A list of the top post titles.
    """
    posts = []
    try:
        url = f"https://old.reddit.com/r/{subreddit}/top/?sort=top&t=day"
        # Using a more realistic browser User-Agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        post_elements = soup.select('a.title') # Using a more specific CSS selector

        for post in post_elements[:limit]:
            posts.append(post.get_text())

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Reddit posts: {e}")
        return ["I'm having trouble connecting to Reddit right now."]
    except Exception as e:
        print(f"An unexpected error occurred while scraping Reddit: {e}")
        return ["Something went wrong while I was checking Reddit."]

    if not posts:
        return [f"I couldn't find any hot posts on r/{subreddit} today."]

    return posts

# Example usage (for testing)
if __name__ == '__main__':
    print("--- Fetching top 5 posts from r/memes ---")
    memes = get_top_reddit_posts("memes", 5)
    for i, meme_title in enumerate(memes):
        print(f"{i+1}. {meme_title}")

    print("\n--- Fetching top 3 posts from r/worldnews ---")
    news = get_top_reddit_posts("worldnews", 3)
    for i, news_title in enumerate(news):
        print(f"{i+1}. {news_title}")
