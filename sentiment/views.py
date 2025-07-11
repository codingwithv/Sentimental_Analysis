from django.shortcuts import render, redirect, HttpResponse
from .forms import Sentiment_Typed_Tweet_analyse_form, Sentiment_Imported_Tweet_analyse_form
from .sentiment_analysis_code import sentiment_analysis_code
from .tweepy_sentiment import Import_tweet_sentiment


def sentiment_analysis(request):
    return render(request, 'home/sentiment.html')


def sentiment_analysis_type(request):
    if request.method == 'POST':
        form = Sentiment_Typed_Tweet_analyse_form(request.POST)
        analyse = sentiment_analysis_code()
        if form.is_valid():
            tweet = form.cleaned_data['sentiment_typed_tweet']
            sentiment = analyse.get_tweet_sentiment(tweet)
            args = {'tweet': tweet, 'sentiment': sentiment, 'form': form}
            return render(request, 'home/sentiment_type_result.html', args)
    else:
        form = Sentiment_Typed_Tweet_analyse_form()

    return render(request, 'home/sentiment_type.html', {'form': form})


def sentiment_analysis_import(request):
    if request.method == 'POST':
        form = Sentiment_Imported_Tweet_analyse_form(request.POST)
        tweet_text = Import_tweet_sentiment()
        analyse = sentiment_analysis_code()

        if form.is_valid():
            handle = form.cleaned_data['sentiment_imported_tweet']

            # Check if it's a hashtag search
            if handle.startswith('#'):
                list_of_tweets = tweet_text.get_hashtag(handle)
            else:
                # Ensure it's a valid Twitter handle
                if not handle.startswith('@'):
                    handle = '@' + handle
                list_of_tweets = tweet_text.get_tweets(handle)

            # Process tweets and their sentiments
            list_of_tweets_and_sentiments = [(tweet, analyse.get_tweet_sentiment(tweet)) for tweet in list_of_tweets]

            args = {'list_of_tweets_and_sentiments': list_of_tweets_and_sentiments, 'handle': handle}

            if handle.startswith('#'):
                return render(request, 'home/sentiment_import_result_hashtag.html', args)
            else:
                return render(request, 'home/sentiment_import_result.html', args)
    else:
        form = Sentiment_Imported_Tweet_analyse_form()

    return render(request, 'home/sentiment_import.html', {'form': form})
