from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> Dict:
        """
        Analyze text sentiment using both TextBlob and VADER.
        Returns combined sentiment scores and classification.
        """
        # TextBlob analysis
        blob = TextBlob(text)
        blob_polarity = blob.sentiment.polarity
        blob_subjectivity = blob.sentiment.subjectivity

        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)

        # Combine and classify
        compound_score = vader_scores['compound']
        
        # Determine sentiment category
        if compound_score >= 0.05:
            sentiment = 'positive'
        elif compound_score <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        # Determine urgency based on negative sentiment strength
        urgency = 'high' if compound_score < -0.5 else 'medium' if compound_score < -0.2 else 'low'

        return {
            'sentiment': sentiment,
            'urgency': urgency,
            'scores': {
                'compound': compound_score,
                'textblob_polarity': blob_polarity,
                'textblob_subjectivity': blob_subjectivity,
                'vader_neg': vader_scores['neg'],
                'vader_neu': vader_scores['neu'],
                'vader_pos': vader_scores['pos']
            }
        }