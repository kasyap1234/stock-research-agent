"""
Sentiment Analysis Module
Scrapes stock news and performs sentiment analysis
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes sentiment for stocks based on news and other sources
    """

    def __init__(self, delay: float = 1.0):
        """
        Initialize sentiment analyzer

        Args:
            delay: Delay between requests in seconds
        """
        self.delay = delay
        self.vader = SentimentIntensityAnalyzer()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def analyze_stock_sentiment(self, symbol: str, days: int = 7) -> Dict:
        """
        Analyze overall sentiment for a stock

        Args:
            symbol: Stock symbol
            days: Number of days to look back

        Returns:
            Dictionary with sentiment analysis
        """
        result = {
            'symbol': symbol,
            'analysis_date': datetime.now().isoformat(),
            'news_count': 0,
            'sentiment_score': 0,
            'sentiment_label': 'neutral',
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'news_articles': []
        }

        try:
            # Get news from yfinance
            news = self._fetch_news_yfinance(symbol)

            if not news:
                logger.warning(f"No news found for {symbol}")
                return result

            result['news_count'] = len(news)
            result['news_articles'] = news

            # Analyze sentiment for each news item
            sentiments = []
            for article in news:
                title = article.get('title', '')
                if title:
                    sentiment = self.analyze_text(title)
                    sentiments.append(sentiment['compound'])
                    article['sentiment'] = sentiment

                    # Count sentiment categories
                    if sentiment['compound'] >= 0.05:
                        result['positive_count'] += 1
                    elif sentiment['compound'] <= -0.05:
                        result['negative_count'] += 1
                    else:
                        result['neutral_count'] += 1

            # Calculate overall sentiment
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                result['sentiment_score'] = avg_sentiment

                # Determine sentiment label
                if avg_sentiment >= 0.05:
                    result['sentiment_label'] = 'positive'
                elif avg_sentiment <= -0.05:
                    result['sentiment_label'] = 'negative'
                else:
                    result['sentiment_label'] = 'neutral'

            logger.info(f"Sentiment for {symbol}: {result['sentiment_label']} ({result['sentiment_score']:.3f})")

        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {str(e)}")

        return result

    def _fetch_news_yfinance(self, symbol: str) -> List[Dict]:
        """
        Fetch news using yfinance

        Args:
            symbol: Stock symbol

        Returns:
            List of news articles
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            articles = []
            for item in news[:10]:  # Limit to 10 most recent
                article = {
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat() if item.get('providerPublishTime') else None,
                }
                articles.append(article)

            time.sleep(self.delay)
            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return []

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a text using VADER

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        scores = self.vader.polarity_scores(text)
        return scores

    def get_sentiment_score_normalized(self, sentiment_score: float) -> float:
        """
        Normalize sentiment score to 0-100 scale

        Args:
            sentiment_score: Raw sentiment score (-1 to 1)

        Returns:
            Normalized score (0-100)
        """
        # Convert -1 to 1 range to 0 to 100
        return (sentiment_score + 1) * 50

    def analyze_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Analyze sentiment for multiple stocks

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbols to sentiment data
        """
        results = {}

        for symbol in symbols:
            try:
                sentiment = self.analyze_stock_sentiment(symbol)
                results[symbol] = sentiment
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                results[symbol] = {
                    'symbol': symbol,
                    'error': str(e),
                    'sentiment_score': 0,
                    'sentiment_label': 'unknown'
                }

        return results

    def add_sentiment_to_dataframe(self, df, sentiment_weight: float = 0.1):
        """
        Add sentiment scores to stock dataframe and adjust overall scores

        Args:
            df: DataFrame with stock data
            sentiment_weight: Weight of sentiment in overall score

        Returns:
            DataFrame with sentiment data added
        """
        if df.empty:
            return df

        logger.info("Adding sentiment analysis to stocks...")

        sentiment_scores = []
        sentiment_labels = []

        for _, row in df.iterrows():
            symbol = row['symbol']
            try:
                sentiment = self.analyze_stock_sentiment(symbol)
                sentiment_scores.append(sentiment['sentiment_score'])
                sentiment_labels.append(sentiment['sentiment_label'])
            except Exception as e:
                logger.error(f"Error getting sentiment for {symbol}: {str(e)}")
                sentiment_scores.append(0)
                sentiment_labels.append('unknown')

        df['sentiment_score'] = sentiment_scores
        df['sentiment_label'] = sentiment_labels

        # Adjust overall score with sentiment
        if 'overall_score' in df.columns and sentiment_weight > 0:
            sentiment_normalized = [(s + 1) * 50 for s in sentiment_scores]  # Convert -1..1 to 0..100

            # Adjust overall score: reduce weight of original score, add sentiment
            original_weight = 1 - sentiment_weight
            df['overall_score_with_sentiment'] = (
                df['overall_score'] * original_weight +
                [s * sentiment_weight for s in sentiment_normalized]
            )

        logger.info("Sentiment analysis complete!")
        return df

    def get_sector_sentiment(self, df) -> Dict[str, Dict]:
        """
        Get aggregated sentiment by sector

        Args:
            df: DataFrame with stock data including sentiment

        Returns:
            Dictionary with sector-wise sentiment
        """
        if 'sector' not in df.columns or 'sentiment_score' not in df.columns:
            return {}

        sector_sentiment = {}

        for sector in df['sector'].unique():
            sector_df = df[df['sector'] == sector]

            avg_sentiment = sector_df['sentiment_score'].mean()

            sentiment_label = 'neutral'
            if avg_sentiment >= 0.05:
                sentiment_label = 'positive'
            elif avg_sentiment <= -0.05:
                sentiment_label = 'negative'

            sector_sentiment[sector] = {
                'average_sentiment': avg_sentiment,
                'sentiment_label': sentiment_label,
                'stock_count': len(sector_df),
                'positive_stocks': len(sector_df[sector_df['sentiment_score'] >= 0.05]),
                'negative_stocks': len(sector_df[sector_df['sentiment_score'] <= -0.05]),
            }

        return sector_sentiment

    def generate_sentiment_report(self, sentiment_data: Dict) -> str:
        """
        Generate a text report from sentiment data

        Args:
            sentiment_data: Sentiment analysis results

        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += f"SENTIMENT ANALYSIS: {sentiment_data['symbol']}\n"
        report += "="*60 + "\n\n"

        report += f"Overall Sentiment: {sentiment_data['sentiment_label'].upper()}\n"
        report += f"Sentiment Score: {sentiment_data['sentiment_score']:.3f}\n"
        report += f"News Articles Analyzed: {sentiment_data['news_count']}\n\n"

        if sentiment_data['news_count'] > 0:
            report += f"Positive: {sentiment_data['positive_count']} | "
            report += f"Neutral: {sentiment_data['neutral_count']} | "
            report += f"Negative: {sentiment_data['negative_count']}\n\n"

            report += "Recent News:\n"
            report += "-" * 60 + "\n"

            for i, article in enumerate(sentiment_data['news_articles'][:5], 1):
                report += f"{i}. {article['title']}\n"
                if 'sentiment' in article:
                    sent = article['sentiment']['compound']
                    sent_label = 'POS' if sent >= 0.05 else 'NEG' if sent <= -0.05 else 'NEU'
                    report += f"   Sentiment: {sent_label} ({sent:.3f})\n"
                if article.get('publisher'):
                    report += f"   Source: {article['publisher']}\n"
                report += "\n"

        report += "="*60 + "\n"

        return report
