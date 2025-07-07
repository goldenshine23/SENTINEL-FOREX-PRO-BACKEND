# backend/news_sentiment.py

import requests
from backend.config import FINNHUB_API_KEY

def get_news_sentiment(symbol):
    try:
        response = requests.get(
            f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={FINNHUB_API_KEY}",
            timeout=10
        )
        data = response.json()
        return data
    except Exception as e:
        print(f"❌ News API error: {e}")
        return {}

def is_strong_news_event(symbol):
    sentiment = get_news_sentiment(symbol)
    try:
        # Example logic: classify as strong if negative/positive score > 0.6
        if sentiment:
            score = sentiment.get("sentiment", {})
            bullish = float(score.get("bullishPercent", 0))
            bearish = float(score.get("bearishPercent", 0))
            return bullish > 0.6 or bearish > 0.6
    except Exception as e:
        print(f"❌ Error checking strong news event: {e}")
    return False
