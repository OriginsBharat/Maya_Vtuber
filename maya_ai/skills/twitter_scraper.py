import tweepy
from maya_ai.config.config_manager import ConfigManager

def get_user_tweets(username: str, config_manager: ConfigManager, limit: int = 5) -> list:
    """
    Fetches the latest tweets from a user's timeline using the X API.
    """
    try:
        bearer_token = config_manager.get_key("TWITTER_BEARER_TOKEN")

        client = tweepy.Client(bearer_token)

        user = client.get_user(username=username).data
        if not user:
            return [f"I couldn't find a Twitter user with the username: {username}"]

        response = client.get_users_tweets(user.id, max_results=limit)
        tweets = response.data

        if not tweets:
            return [f"I couldn't find any recent tweets from {username}."]

        return [tweet.text for tweet in tweets]

    except Exception as e:
        print(f"An error occurred while fetching from Twitter API: {e}")
        return [f"I'm having trouble connecting to the Twitter API. The error is: {e}"]

# Example usage will now be handled in the main UI file.
