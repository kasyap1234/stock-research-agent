"""
Configuration file for Indian Stock Research Agent
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    """Weights for different scoring components"""
    # Value score weights
    pe_weight: float = Field(default=0.35, ge=0, le=1)
    pb_weight: float = Field(default=0.35, ge=0, le=1)
    debt_equity_weight: float = Field(default=0.30, ge=0, le=1)

    # Growth score weights
    eps_growth_weight: float = Field(default=0.5, ge=0, le=1)
    revenue_growth_weight: float = Field(default=0.5, ge=0, le=1)

    # Safety score weights
    debt_safety_weight: float = Field(default=0.4, ge=0, le=1)
    profit_stability_weight: float = Field(default=0.3, ge=0, le=1)
    roe_weight: float = Field(default=0.3, ge=0, le=1)

    # Final recommendation weights
    value_score_weight: float = Field(default=0.3, ge=0, le=1)
    growth_score_weight: float = Field(default=0.4, ge=0, le=1)
    safety_score_weight: float = Field(default=0.3, ge=0, le=1)


class AgentConfig(BaseModel):
    """Main configuration for the stock research agent"""

    # NSE Top stocks - Popular Indian stocks
    nse_stocks: List[str] = Field(
        default=[
            # Banking & Financial
            "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS",
            # IT
            "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS",
            # Energy & Utilities
            "RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS",
            # Auto
            "MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS",
            # FMCG
            "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS",
            # Pharma
            "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
            # Infrastructure & Cement
            "ULTRACEMCO.NS", "GRASIM.NS", "LT.NS",
            # Metals
            "TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS",
            # Telecom
            "BHARTIARTL.NS",
            # Consumer
            "TITAN.NS", "ASIANPAINT.NS",
        ]
    )

    # BSE stocks (can add more)
    bse_stocks: List[str] = Field(default=[])

    # Scoring configuration
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)

    # Top N stocks to recommend
    top_n_recommendations: int = Field(default=10, ge=1, le=50)

    # Data quality thresholds
    min_market_cap: float = Field(default=1000, description="Minimum market cap in crores")
    min_data_quality: float = Field(default=0.5, ge=0, le=1, description="Minimum data completeness ratio")

    # Sentiment analysis
    enable_sentiment: bool = Field(default=True)
    sentiment_weight: float = Field(default=0.1, ge=0, le=1)

    # Output configuration
    output_csv: bool = Field(default=True)
    output_json: bool = Field(default=True)
    output_dir: str = Field(default="output")

    # Caching
    cache_duration_hours: int = Field(default=24)

    # API rate limiting
    request_delay_seconds: float = Field(default=0.5)

    # Ideal ratio benchmarks for Indian markets
    ideal_pe_ratio: float = Field(default=20.0)
    ideal_pb_ratio: float = Field(default=3.0)
    ideal_roe: float = Field(default=15.0)
    ideal_debt_equity: float = Field(default=1.0)

    def get_all_stocks(self) -> List[str]:
        """Get combined list of all stocks"""
        return self.nse_stocks + self.bse_stocks


# Default configuration instance
default_config = AgentConfig()
