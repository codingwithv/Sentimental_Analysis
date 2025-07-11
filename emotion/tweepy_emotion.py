import os
import tweepy
import pandas as pd
from tweepy import OAuthHandler, API, Cursor
from dotenv import load_dotenv

class Import_tweet_emotion:
    def __init__(self):
        load_dotenv()  # Load API keys securely

        self.consumer_key = os.getenv("CONSUMER_KEY")
        self.consumer_secret = os.getenv("CONSUMER_SECRET")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

        # Authentication
        try:
            self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            self.auth.set_access_token(self.access_token, self.access_token_secret)
            self.api = API(self.auth, wait_on_rate_limit=True)
        except Exception as e:
            raise Exception(f"Failed to authenticate with Twitter API: {str(e)}")

    def tweet_to_data_frame(self, tweets):
        if not tweets:
            return pd.DataFrame(columns=['Tweets'])
        return pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['Tweets'])

    def get_tweets(self, handle, count=20):
        try:
            tweets = self.api.user_timeline(
                screen_name=handle,
                count=count,
                tweet_mode="extended"
            )
            return [tweet.full_text for tweet in tweets]
        except tweepy.errors.TweepyException as e:
            print(f"Error fetching tweets for {handle}: {e}")
            return []

    def get_hashtag(self, hashtag, count=20):
        try:
            tweets = []
            for tweet in Cursor(
                self.api.search_tweets,
                q=f"#{hashtag}",
                lang='en',
                tweet_mode="extended"
            ).items(count):
                tweets.append(tweet.full_text)
            return tweets
        except tweepy.errors.TweepyException as e:
            print(f"Error fetching tweets for #{hashtag}: {e}")
            return []