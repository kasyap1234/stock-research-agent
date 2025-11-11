"""
Indian Stock Research Agent
A comprehensive Python-based agent for analyzing Indian stocks from NSE/BSE.
"""

__version__ = "1.0.0"
__author__ = "Stock Research Agent"

from stock_agent.modules.data_fetcher import StockDataFetcher
from stock_agent.modules.metrics_calculator import MetricsCalculator
from stock_agent.modules.stock_ranker import StockRanker
from stock_agent.modules.sentiment_analyzer import SentimentAnalyzer
from stock_agent.agent import StockResearchAgent

__all__ = [
    "StockDataFetcher",
    "MetricsCalculator",
    "StockRanker",
    "SentimentAnalyzer",
    "StockResearchAgent",
]
