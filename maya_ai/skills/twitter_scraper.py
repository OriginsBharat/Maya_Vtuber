import tweepy
import os

def get_user_tweets(username: str, limit: int = 5) -> list:
    """
    Fetches the latest tweets from a user's timeline using the X API.

    Args:
        username: The X username of the user.
        limit: The maximum number of tweets to return.

    Returns:
        A list of tweet texts, or an error message if it fails.
    """
    try:
        # These credentials need to be set as environment variables by the user
        bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_BEARER_TOKEN")

        client = tweepy.Client(bearer_token)

        # Get the user's ID from their username
        user = client.get_user(username=username).data
        if not user:
            return [f"I couldn't find a Twitter user with the username: {username}"]

        # Fetch the user's latest tweets
        response = client.get_users_tweets(user.id, max_results=limit)
        tweets = response.data

        if not tweets:
            return [f"I couldn't find any recent tweets from {username}."]

        return [tweet.text for tweet in tweets]

    except Exception as e:
        print(f"An error occurred while fetching from Twitter API: {e}")
        return [f"I'm having trouble connecting to the Twitter API. The error is: {e}"]

# Example usage (for testing)
if __name__ == '__main__':
    # To run this test, you must set the TWITTER_BEARER_TOKEN environment variable.
    if os.environ.get("TWITTER_BEARER_TOKEN"):
        print(f"--- Fetching latest tweets from @elonmusk ---")
        user_tweets = get_user_tweets("elonmusk", 3)
        for i, tweet in enumerate(user_tweets):
            print(f"{i+1}. {tweet}\n")
    else:
        print("Skipping Twitter test because TWITTER_BEARER_TOKEN is not set.")
        print("Please set your Twitter API bearer token as an environment variable to test this.")
