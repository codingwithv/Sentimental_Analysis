import pandas as pd
import numpy as np
import nltk
import re
import pickle
import itertools
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from django.conf import settings
import os
import joblib  # Better alternative to pickle
from sklearn.exceptions import InconsistentVersionWarning
import warnings

# Download NLTK data if not already present
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)


class emotion_analysis_code:
    def __init__(self):
        self.lem = WordNetLemmatizer()
        # Load models once during initialization
        self.vectorizer = self._load_model('vectorizer.pickle')
        self.model = self._load_model('finalized_model.sav')

    def _load_model(self, filename):
        """Safely load a saved model with version checking"""
        path = os.path.join(settings.MODELS, filename)

        try:
            # First try loading with joblib (more reliable for sklearn models)
            try:
                return joblib.load(path)
            except:
                # Fall back to pickle if joblib fails
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=InconsistentVersionWarning)
                    with open(path, 'rb') as f:
                        # Handle sklearn namespace changes
                        import sklearn.svm
                        import sys
                        if 'sklearn.svm.classes' not in sys.modules:
                            sys.modules['sklearn.svm.classes'] = sklearn.svm._classes
                        return pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found: {path}")
        except Exception as e:
            raise RuntimeError(f"Error loading model {filename}: {str(e)}")

    def clean_text(self, text):
        """Clean and preprocess text with robust error handling"""
        if not isinstance(text, str) or not text.strip():
            return 'no text'

        try:
            # Remove URLs
            text = re.sub(r"http\S+", "", text)
            if not text.strip():
                return 'no text'

            # Tokenize and remove mentions
            tokens = text.split()
            tokens = [t for t in tokens if not t.startswith('@')]
            if not tokens:
                return 'no text'

            # Reconstruct text
            text = ' '.join(tokens)

            # Remove special chars (keeping letters and numbers)
            text = re.sub(r"[^\w\s]", ' ', text)
            if not text.strip():
                return 'no text'

            # Remove character repetition (keeping max 2 repeats)
            text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text))
            text = text.replace("'", "")

            # Tokenize and lemmatize
            tokens = word_tokenize(text)
            tokens = [self.lem.lemmatize(t, "v") for t in tokens]

            return tokens if tokens else 'no text'

        except Exception as e:
            print(f"Error cleaning text: {e}")
            return 'no text'

    def predict_emotion(self, tweet):
        """Predict emotion from tweet text with error handling"""
        if not isinstance(tweet, str) or not tweet.strip():
            return "Neutral"  # Default for empty input

        try:
            cleaned = self.clean_text(tweet)
            if cleaned == 'no text':
                return "Neutral"

            # Convert to pandas Series for vectorizer
            tweet_series = pd.Series(' '.join(cleaned) if isinstance(cleaned, list) else cleaned)

            # Vectorize and predict
            test_vec = self.vectorizer.transform(tweet_series)
            prediction = self.model.predict(test_vec)

            # Map prediction to readable format
            emotion_map = {
                'worry': 'Worry',
                'sadness': 'Sadness',
                'happiness': 'Happiness',
                'love': 'Love',
                'hate': 'Hate',
                'neutral': 'Neutral',
                'anger': 'Anger',
                'surprise': 'Surprise'
            }

            return emotion_map.get(prediction[0].lower(), 'Neutral')

        except Exception as e:
            print(f"Error predicting emotion: {e}")
            return "Neutral"  # Fallback emotion