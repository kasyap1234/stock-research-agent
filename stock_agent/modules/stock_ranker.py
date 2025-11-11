"""
Stock Ranking Module
Ranks and recommends stocks based on multiple scoring criteria
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class StockRanker:
    """
    Ranks stocks based on value, growth, quality, and safety scores
    Provides recommendations based on different investment strategies
    """

    def __init__(
        self,
        value_weight: float = 0.3,
        growth_weight: float = 0.3,
        quality_weight: float = 0.25,
        safety_weight: float = 0.15
    ):
        """
        Initialize the stock ranker

        Args:
            value_weight: Weight for value score
            growth_weight: Weight for growth score
            quality_weight: Weight for quality score
            safety_weight: Weight for safety score
        """
        self.value_weight = value_weight
        self.growth_weight = growth_weight
        self.quality_weight = quality_weight
        self.safety_weight = safety_weight

        # Ensure weights sum to 1
        total = value_weight + growth_weight + quality_weight + safety_weight
        if not np.isclose(total, 1.0):
            logger.warning(f"Weights sum to {total}, normalizing to 1.0")
            self.value_weight /= total
            self.growth_weight /= total
            self.quality_weight /= total
            self.safety_weight /= total

    def rank_stocks(
        self,
        df: pd.DataFrame,
        min_market_cap: float = 1000,
        min_data_quality: float = 0.5
    ) -> pd.DataFrame:
        """
        Rank stocks based on overall score

        Args:
            df: DataFrame with stock data and calculated metrics
            min_market_cap: Minimum market cap in crores
            min_data_quality: Minimum data completeness ratio

        Returns:
            Ranked DataFrame
        """
        logger.info("Ranking stocks...")

        # Filter stocks
        filtered_df = self._filter_stocks(df, min_market_cap, min_data_quality)

        if filtered_df.empty:
            logger.warning("No stocks passed the filters!")
            return pd.DataFrame()

        # Calculate final scores if not already present
        if 'final_score' not in filtered_df.columns:
            filtered_df['final_score'] = (
                filtered_df['value_score'] * self.value_weight +
                filtered_df['growth_score'] * self.growth_weight +
                filtered_df['quality_score'] * self.quality_weight +
                filtered_df['safety_score'] * self.safety_weight
            )

        # Sort by final score
        ranked_df = filtered_df.sort_values('final_score', ascending=False).reset_index(drop=True)

        # Add rank column
        ranked_df['rank'] = range(1, len(ranked_df) + 1)

        logger.info(f"Ranked {len(ranked_df)} stocks")
        return ranked_df

    def _filter_stocks(
        self,
        df: pd.DataFrame,
        min_market_cap: float,
        min_data_quality: float
    ) -> pd.DataFrame:
        """
        Filter stocks based on criteria

        Args:
            df: Input DataFrame
            min_market_cap: Minimum market cap in crores
            min_data_quality: Minimum data completeness

        Returns:
            Filtered DataFrame
        """
        original_count = len(df)

        # Filter by market cap
        if 'market_cap_crores' in df.columns:
            df = df[df['market_cap_crores'] >= min_market_cap]

        # Filter by data quality
        if 'data_completeness' in df.columns:
            df = df[df['data_completeness'] >= min_data_quality]

        # Filter out stocks with invalid prices
        if 'current_price' in df.columns:
            df = df[df['current_price'] > 0]

        # Filter out stocks with invalid overall scores
        if 'overall_score' in df.columns:
            df = df[df['overall_score'] > 0]

        filtered_count = len(df)
        logger.info(f"Filtered from {original_count} to {filtered_count} stocks")

        return df

    def get_top_recommendations(
        self,
        df: pd.DataFrame,
        top_n: int = 10,
        strategy: str = 'balanced'
    ) -> pd.DataFrame:
        """
        Get top N stock recommendations based on strategy

        Args:
            df: Ranked DataFrame
            top_n: Number of top stocks to return
            strategy: Investment strategy ('value', 'growth', 'quality', 'safety', 'balanced')

        Returns:
            DataFrame with top recommendations
        """
        if df.empty:
            return pd.DataFrame()

        # Sort based on strategy
        if strategy == 'value':
            sorted_df = df.sort_values('value_score', ascending=False)
        elif strategy == 'growth':
            sorted_df = df.sort_values('growth_score', ascending=False)
        elif strategy == 'quality':
            sorted_df = df.sort_values('quality_score', ascending=False)
        elif strategy == 'safety':
            sorted_df = df.sort_values('safety_score', ascending=False)
        else:  # balanced
            if 'final_score' in df.columns:
                sorted_df = df.sort_values('final_score', ascending=False)
            else:
                sorted_df = df.sort_values('overall_score', ascending=False)

        return sorted_df.head(top_n).reset_index(drop=True)

    def get_sector_recommendations(
        self,
        df: pd.DataFrame,
        top_n_per_sector: int = 3
    ) -> pd.DataFrame:
        """
        Get top recommendations per sector

        Args:
            df: Ranked DataFrame
            top_n_per_sector: Number of top stocks per sector

        Returns:
            DataFrame with sector-wise recommendations
        """
        if 'sector' not in df.columns or df.empty:
            return df

        sector_recommendations = []

        for sector in df['sector'].unique():
            sector_df = df[df['sector'] == sector]
            if 'final_score' in sector_df.columns:
                top_sector = sector_df.nlargest(top_n_per_sector, 'final_score')
            else:
                top_sector = sector_df.nlargest(top_n_per_sector, 'overall_score')
            sector_recommendations.append(top_sector)

        return pd.concat(sector_recommendations, ignore_index=True)

    def categorize_stocks(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Categorize stocks into different buckets

        Args:
            df: DataFrame with stock data

        Returns:
            Dictionary with categorized DataFrames
        """
        categories = {}

        if df.empty:
            return categories

        # Value stocks (high value score)
        if 'value_score' in df.columns:
            categories['value_stocks'] = df.nlargest(10, 'value_score')

        # Growth stocks (high growth score)
        if 'growth_score' in df.columns:
            categories['growth_stocks'] = df.nlargest(10, 'growth_score')

        # Quality stocks (high quality score)
        if 'quality_score' in df.columns:
            categories['quality_stocks'] = df.nlargest(10, 'quality_score')

        # Safe stocks (high safety score)
        if 'safety_score' in df.columns:
            categories['safe_stocks'] = df.nlargest(10, 'safety_score')

        # Dividend stocks (high dividend yield)
        if 'dividend_yield' in df.columns:
            dividend_df = df[df['dividend_yield'] > 1.0]
            categories['dividend_stocks'] = dividend_df.nlargest(10, 'dividend_yield')

        # Undervalued stocks (low P/E and P/B)
        if 'pe_ratio' in df.columns and 'pb_ratio' in df.columns:
            undervalued = df[
                (df['pe_ratio'] > 0) &
                (df['pe_ratio'] < 15) &
                (df['pb_ratio'] > 0) &
                (df['pb_ratio'] < 2)
            ]
            categories['undervalued_stocks'] = undervalued.nlargest(10, 'overall_score')

        # High ROE stocks
        if 'roe' in df.columns:
            high_roe = df[df['roe'] > 15]
            categories['high_roe_stocks'] = high_roe.nlargest(10, 'roe')

        # Low debt stocks
        if 'debt_to_equity' in df.columns:
            low_debt = df[df['debt_to_equity'] < 0.5]
            categories['low_debt_stocks'] = low_debt.nlargest(10, 'overall_score')

        return categories

    def generate_summary_report(self, df: pd.DataFrame, top_n: int = 10) -> Dict:
        """
        Generate a summary report of the analysis

        Args:
            df: Analyzed DataFrame
            top_n: Number of top stocks to include

        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {'error': 'No data available'}

        report = {
            'total_stocks_analyzed': len(df),
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Top stocks
        if 'final_score' in df.columns:
            top_stocks = df.nlargest(top_n, 'final_score')
        else:
            top_stocks = df.nlargest(top_n, 'overall_score')

        report['top_stocks'] = top_stocks[['symbol', 'name', 'sector', 'overall_score']].to_dict('records')

        # Average metrics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        report['average_metrics'] = df[numeric_cols].mean().to_dict()

        # Sector distribution
        if 'sector' in df.columns:
            report['sector_distribution'] = df['sector'].value_counts().to_dict()

        # Score ranges
        for score_col in ['value_score', 'growth_score', 'quality_score', 'safety_score', 'overall_score']:
            if score_col in df.columns:
                report[f'{score_col}_range'] = {
                    'min': float(df[score_col].min()),
                    'max': float(df[score_col].max()),
                    'mean': float(df[score_col].mean()),
                    'median': float(df[score_col].median())
                }

        # Best performers by category
        if 'pe_ratio' in df.columns:
            valid_pe = df[df['pe_ratio'] > 0]
            if not valid_pe.empty:
                report['lowest_pe'] = valid_pe.nsmallest(5, 'pe_ratio')[['symbol', 'name', 'pe_ratio']].to_dict('records')

        if 'pb_ratio' in df.columns:
            valid_pb = df[df['pb_ratio'] > 0]
            if not valid_pb.empty:
                report['lowest_pb'] = valid_pb.nsmallest(5, 'pb_ratio')[['symbol', 'name', 'pb_ratio']].to_dict('records')

        if 'roe' in df.columns:
            report['highest_roe'] = df.nlargest(5, 'roe')[['symbol', 'name', 'roe']].to_dict('records')

        if 'dividend_yield' in df.columns:
            high_div = df[df['dividend_yield'] > 0]
            if not high_div.empty:
                report['highest_dividend'] = high_div.nlargest(5, 'dividend_yield')[['symbol', 'name', 'dividend_yield']].to_dict('records')

        return report

    def create_comparison_table(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create a comparison table with key metrics

        Args:
            df: DataFrame with stock data
            columns: List of columns to include

        Returns:
            Formatted comparison DataFrame
        """
        if df.empty:
            return pd.DataFrame()

        if columns is None:
            columns = [
                'symbol', 'name', 'sector', 'current_price',
                'market_cap_crores', 'pe_ratio', 'pb_ratio', 'roe',
                'debt_to_equity', 'eps_growth', 'revenue_growth',
                'dividend_yield', 'value_score', 'growth_score',
                'quality_score', 'safety_score', 'overall_score'
            ]

        # Filter to only existing columns
        existing_cols = [col for col in columns if col in df.columns]

        comparison_df = df[existing_cols].copy()

        # Round numeric columns
        numeric_cols = comparison_df.select_dtypes(include=[np.number]).columns
        comparison_df[numeric_cols] = comparison_df[numeric_cols].round(2)

        return comparison_df

    def explain_recommendation(self, stock_data: Dict) -> str:
        """
        Generate a textual explanation for why a stock is recommended

        Args:
            stock_data: Dictionary with stock data

        Returns:
            Explanation string
        """
        symbol = stock_data.get('symbol', 'Unknown')
        name = stock_data.get('name', 'Unknown')
        overall_score = stock_data.get('overall_score', 0)

        explanation = f"\n{'='*60}\n"
        explanation += f"Stock: {name} ({symbol})\n"
        explanation += f"Overall Score: {overall_score:.2f}/100\n"
        explanation += f"{'='*60}\n\n"

        # Value assessment
        pe = stock_data.get('pe_ratio', 0)
        pb = stock_data.get('pb_ratio', 0)
        value_score = stock_data.get('value_score', 0)

        explanation += f"📊 VALUATION (Score: {value_score:.1f}/100)\n"
        if pe > 0:
            explanation += f"  • P/E Ratio: {pe:.2f}"
            if pe < 15:
                explanation += " (Undervalued) ✓\n"
            elif pe < 25:
                explanation += " (Fair) ~\n"
            else:
                explanation += " (Expensive) ✗\n"

        if pb > 0:
            explanation += f"  • P/B Ratio: {pb:.2f}"
            if pb < 2:
                explanation += " (Good value) ✓\n"
            elif pb < 3:
                explanation += " (Fair) ~\n"
            else:
                explanation += " (Pricey) ✗\n"

        # Growth assessment
        eps_growth = stock_data.get('eps_growth', 0)
        rev_growth = stock_data.get('revenue_growth', 0)
        growth_score = stock_data.get('growth_score', 0)

        explanation += f"\n📈 GROWTH (Score: {growth_score:.1f}/100)\n"
        if eps_growth:
            explanation += f"  • EPS Growth: {eps_growth:.1f}%"
            if eps_growth > 15:
                explanation += " (Strong) ✓\n"
            elif eps_growth > 5:
                explanation += " (Moderate) ~\n"
            else:
                explanation += " (Weak) ✗\n"

        if rev_growth:
            explanation += f"  • Revenue Growth: {rev_growth:.1f}%"
            if rev_growth > 10:
                explanation += " (Healthy) ✓\n"
            elif rev_growth > 0:
                explanation += " (Positive) ~\n"
            else:
                explanation += " (Declining) ✗\n"

        # Quality assessment
        roe = stock_data.get('roe', 0)
        profit_margin = stock_data.get('profit_margin', 0)
        quality_score = stock_data.get('quality_score', 0)

        explanation += f"\n💎 QUALITY (Score: {quality_score:.1f}/100)\n"
        if roe:
            explanation += f"  • ROE: {roe:.1f}%"
            if roe > 15:
                explanation += " (Excellent) ✓\n"
            elif roe > 10:
                explanation += " (Good) ~\n"
            else:
                explanation += " (Below average) ✗\n"

        if profit_margin:
            explanation += f"  • Profit Margin: {profit_margin:.1f}%"
            if profit_margin > 10:
                explanation += " (High) ✓\n"
            elif profit_margin > 5:
                explanation += " (Moderate) ~\n"
            else:
                explanation += " (Low) ✗\n"

        # Safety assessment
        de = stock_data.get('debt_to_equity', 0)
        safety_score = stock_data.get('safety_score', 0)

        explanation += f"\n🛡️  SAFETY (Score: {safety_score:.1f}/100)\n"
        if de >= 0:
            explanation += f"  • Debt-to-Equity: {de:.2f}"
            if de < 0.5:
                explanation += " (Very safe) ✓\n"
            elif de < 1.0:
                explanation += " (Safe) ~\n"
            else:
                explanation += " (High debt) ✗\n"

        # Current metrics
        price = stock_data.get('current_price', 0)
        market_cap = stock_data.get('market_cap_crores', 0)
        div_yield = stock_data.get('dividend_yield', 0)

        explanation += f"\n💰 CURRENT METRICS\n"
        explanation += f"  • Price: ₹{price:.2f}\n"
        explanation += f"  • Market Cap: ₹{market_cap:.0f} Cr\n"
        if div_yield:
            explanation += f"  • Dividend Yield: {div_yield:.2f}%\n"

        # Recommendation
        explanation += f"\n🎯 RECOMMENDATION\n"
        if overall_score >= 70:
            explanation += "  Strong Buy - Excellent fundamentals across all metrics\n"
        elif overall_score >= 60:
            explanation += "  Buy - Good fundamentals with minor concerns\n"
        elif overall_score >= 50:
            explanation += "  Hold - Mixed fundamentals, suitable for long-term\n"
        elif overall_score >= 40:
            explanation += "  Neutral - Several concerns, proceed with caution\n"
        else:
            explanation += "  Avoid - Weak fundamentals\n"

        explanation += f"{'='*60}\n"

        return explanation
