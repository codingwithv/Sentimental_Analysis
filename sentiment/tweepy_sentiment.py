import os
from tweepy import OAuthHandler, API, Cursor
import tweepy
import pandas as pd

class Import_tweet_sentiment:
    def __init__(self):
        self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.auth_api = API(auth, wait_on_rate_limit=True)

    def tweet_to_data_frame(self, tweets):
        return pd.DataFrame([tweet.text for tweet in tweets], columns=["Tweets"])

    def get_tweets(self, handle):
        tweets = self.auth_api.user_timeline(screen_name=handle, count=20, tweet_mode="extended")
        df = self.tweet_to_data_frame(tweets)
        return df["Tweets"].tolist()

    def get_hashtag(self, hashtag):
        all_tweets = []
        for tweet in Cursor(self.auth_api.search_tweets, q=hashtag, lang="en").items(20):
            all_tweets.append(tweet.text)
        return all_tweets
