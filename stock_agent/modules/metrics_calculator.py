"""
Financial Metrics Calculator Module
Calculates key financial ratios and metrics for stock analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Calculates comprehensive financial metrics and ratios for stock analysis
    """

    def __init__(self):
        """Initialize the metrics calculator"""
        pass

    def calculate_all_metrics(self, stock_data: Dict) -> Dict:
        """
        Calculate all financial metrics for a stock

        Args:
            stock_data: Dictionary containing raw stock data

        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}

        # Price-to-Earnings (P/E) Ratio
        metrics['pe_ratio'] = self.calculate_pe_ratio(
            stock_data.get('current_price', 0),
            stock_data.get('eps', 0)
        )

        # Price-to-Book (P/B) Ratio
        metrics['pb_ratio'] = self.calculate_pb_ratio(
            stock_data.get('current_price', 0),
            stock_data.get('book_value_per_share', 0),
            stock_data.get('pb_ratio', 0)  # Use existing if available
        )

        # Return on Equity (ROE)
        metrics['roe'] = self.calculate_roe(
            stock_data.get('net_income', 0),
            stock_data.get('stockholder_equity', 0),
            stock_data.get('roe', 0)  # Use existing if available
        )

        # Return on Assets (ROA)
        metrics['roa'] = self.calculate_roa(
            stock_data.get('net_income', 0),
            stock_data.get('total_assets', 0),
            stock_data.get('roa', 0)
        )

        # Debt-to-Equity Ratio
        metrics['debt_to_equity'] = self.calculate_debt_to_equity(
            stock_data.get('total_debt', 0),
            stock_data.get('stockholder_equity', 0),
            stock_data.get('debt_to_equity', 0)
        )

        # Dividend Yield
        metrics['dividend_yield'] = self.calculate_dividend_yield(
            stock_data.get('dividend_rate', 0),
            stock_data.get('current_price', 0),
            stock_data.get('dividend_yield', 0)
        )

        # EPS Growth Rate
        metrics['eps_growth'] = self.calculate_eps_growth(
            stock_data.get('earnings_growth', 0),
            stock_data.get('earnings_quarterly_growth', 0)
        )

        # Revenue Growth Rate
        metrics['revenue_growth'] = self.calculate_revenue_growth(
            stock_data.get('revenue_growth', 0),
            stock_data.get('revenue_growth_calculated', 0)
        )

        # Current Ratio (Liquidity)
        metrics['current_ratio'] = stock_data.get('current_ratio', 0)

        # Quick Ratio (Acid Test)
        metrics['quick_ratio'] = stock_data.get('quick_ratio', 0)

        # Profit Margin
        metrics['profit_margin'] = stock_data.get('profit_margins', 0) * 100 if stock_data.get('profit_margins') else 0

        # Operating Margin
        metrics['operating_margin'] = stock_data.get('operating_margins', 0) * 100 if stock_data.get('operating_margins') else 0

        # Free Cash Flow per Share
        metrics['fcf_per_share'] = self.calculate_fcf_per_share(
            stock_data.get('free_cash_flow', 0),
            stock_data.get('shares_outstanding', 0)
        )

        # Interest Coverage Ratio
        metrics['interest_coverage'] = self.calculate_interest_coverage(
            stock_data.get('ebitda', 0),
            stock_data.get('interest_expense', 0)
        )

        # PEG Ratio (P/E to Growth)
        metrics['peg_ratio'] = self.calculate_peg_ratio(
            metrics['pe_ratio'],
            metrics['eps_growth'],
            stock_data.get('peg_ratio', 0)
        )

        # Asset Turnover Ratio
        metrics['asset_turnover'] = self.calculate_asset_turnover(
            stock_data.get('total_revenue', 0),
            stock_data.get('total_assets', 0)
        )

        # Equity Multiplier
        metrics['equity_multiplier'] = self.calculate_equity_multiplier(
            stock_data.get('total_assets', 0),
            stock_data.get('stockholder_equity', 0)
        )

        # DuPont ROE (Decomposed)
        metrics['dupont_roe'] = self.calculate_dupont_roe(
            metrics['profit_margin'] / 100 if metrics['profit_margin'] else 0,
            metrics['asset_turnover'],
            metrics['equity_multiplier']
        )

        # Graham Number (Intrinsic Value Estimate)
        metrics['graham_number'] = self.calculate_graham_number(
            stock_data.get('eps', 0),
            stock_data.get('book_value_per_share', 0)
        )

        # Value Score (0-100, higher is better value)
        metrics['value_score'] = self.calculate_value_score(
            metrics['pe_ratio'],
            metrics['pb_ratio'],
            metrics['debt_to_equity']
        )

        # Growth Score (0-100, higher is better growth)
        metrics['growth_score'] = self.calculate_growth_score(
            metrics['eps_growth'],
            metrics['revenue_growth']
        )

        # Quality Score (0-100, higher is better quality)
        metrics['quality_score'] = self.calculate_quality_score(
            metrics['roe'],
            metrics['profit_margin'],
            metrics['debt_to_equity']
        )

        # Safety Score (0-100, higher is safer)
        metrics['safety_score'] = self.calculate_safety_score(
            metrics['debt_to_equity'],
            metrics['current_ratio'],
            stock_data.get('volatility', 0)
        )

        # Overall Score (weighted combination)
        metrics['overall_score'] = self.calculate_overall_score(
            metrics['value_score'],
            metrics['growth_score'],
            metrics['quality_score'],
            metrics['safety_score']
        )

        return metrics

    # Individual metric calculation methods

    def calculate_pe_ratio(self, price: float, eps: float) -> float:
        """Calculate Price-to-Earnings ratio"""
        if eps and eps > 0:
            return price / eps
        return 0

    def calculate_pb_ratio(self, price: float, book_value: float, existing_pb: float = 0) -> float:
        """Calculate Price-to-Book ratio"""
        if existing_pb:
            return existing_pb
        if book_value and book_value > 0:
            return price / book_value
        return 0

    def calculate_roe(self, net_income: float, equity: float, existing_roe: float = 0) -> float:
        """Calculate Return on Equity (as percentage)"""
        if existing_roe:
            return existing_roe * 100 if existing_roe < 1 else existing_roe
        if equity and equity > 0:
            return (net_income / equity) * 100
        return 0

    def calculate_roa(self, net_income: float, total_assets: float, existing_roa: float = 0) -> float:
        """Calculate Return on Assets (as percentage)"""
        if existing_roa:
            return existing_roa * 100 if existing_roa < 1 else existing_roa
        if total_assets and total_assets > 0:
            return (net_income / total_assets) * 100
        return 0

    def calculate_debt_to_equity(self, total_debt: float, equity: float, existing_de: float = 0) -> float:
        """Calculate Debt-to-Equity ratio"""
        if existing_de:
            return existing_de
        if equity and equity > 0:
            return total_debt / equity
        return 0

    def calculate_dividend_yield(self, dividend: float, price: float, existing_yield: float = 0) -> float:
        """Calculate Dividend Yield (as percentage)"""
        if existing_yield:
            return existing_yield * 100 if existing_yield < 1 else existing_yield
        if price and price > 0:
            return (dividend / price) * 100
        return 0

    def calculate_eps_growth(self, annual_growth: float, quarterly_growth: float) -> float:
        """Calculate EPS growth rate (as percentage)"""
        # Prefer quarterly growth as it's more recent, fall back to annual
        if quarterly_growth:
            return quarterly_growth * 100 if quarterly_growth < 1 else quarterly_growth
        if annual_growth:
            return annual_growth * 100 if annual_growth < 1 else annual_growth
        return 0

    def calculate_revenue_growth(self, existing_growth: float, calculated_growth: float) -> float:
        """Calculate Revenue growth rate (as percentage)"""
        if calculated_growth:
            return calculated_growth
        if existing_growth:
            return existing_growth * 100 if existing_growth < 1 else existing_growth
        return 0

    def calculate_fcf_per_share(self, fcf: float, shares: float) -> float:
        """Calculate Free Cash Flow per share"""
        if shares and shares > 0:
            return fcf / shares
        return 0

    def calculate_interest_coverage(self, ebitda: float, interest: float) -> float:
        """Calculate Interest Coverage ratio"""
        if interest and interest > 0:
            return ebitda / interest
        return 0

    def calculate_peg_ratio(self, pe: float, growth: float, existing_peg: float = 0) -> float:
        """Calculate PEG ratio"""
        if existing_peg:
            return existing_peg
        if growth and growth > 0:
            return pe / growth
        return 0

    def calculate_asset_turnover(self, revenue: float, assets: float) -> float:
        """Calculate Asset Turnover ratio"""
        if assets and assets > 0:
            return revenue / assets
        return 0

    def calculate_equity_multiplier(self, assets: float, equity: float) -> float:
        """Calculate Equity Multiplier"""
        if equity and equity > 0:
            return assets / equity
        return 0

    def calculate_dupont_roe(self, profit_margin: float, asset_turnover: float, equity_multiplier: float) -> float:
        """Calculate DuPont ROE (decomposed)"""
        return profit_margin * asset_turnover * equity_multiplier * 100

    def calculate_graham_number(self, eps: float, book_value: float) -> float:
        """
        Calculate Graham Number (intrinsic value estimate)
        Graham Number = √(22.5 × EPS × Book Value per Share)
        """
        if eps > 0 and book_value > 0:
            return np.sqrt(22.5 * eps * book_value)
        return 0

    # Scoring methods

    def calculate_value_score(self, pe: float, pb: float, de: float, weights: tuple = (0.35, 0.35, 0.30)) -> float:
        """
        Calculate value score (0-100, higher is better)
        Based on P/E, P/B, and Debt/Equity ratios
        """
        pe_score = self._normalize_pe_score(pe)
        pb_score = self._normalize_pb_score(pb)
        de_score = self._normalize_de_score(de)

        return (pe_score * weights[0] + pb_score * weights[1] + de_score * weights[2]) * 100

    def calculate_growth_score(self, eps_growth: float, revenue_growth: float, weights: tuple = (0.6, 0.4)) -> float:
        """
        Calculate growth score (0-100, higher is better)
        Based on EPS growth and revenue growth
        """
        eps_score = self._normalize_growth(eps_growth)
        rev_score = self._normalize_growth(revenue_growth)

        return (eps_score * weights[0] + rev_score * weights[1]) * 100

    def calculate_quality_score(self, roe: float, profit_margin: float, de: float) -> float:
        """
        Calculate quality score (0-100, higher is better)
        Based on ROE, profit margin, and low debt
        """
        roe_score = self._normalize_roe(roe)
        margin_score = self._normalize_margin(profit_margin)
        de_score = self._normalize_de_score(de)

        return (roe_score * 0.4 + margin_score * 0.3 + de_score * 0.3) * 100

    def calculate_safety_score(self, de: float, current_ratio: float, volatility: float) -> float:
        """
        Calculate safety score (0-100, higher is safer)
        Based on low debt, good liquidity, and low volatility
        """
        de_score = self._normalize_de_score(de)
        liquidity_score = self._normalize_liquidity(current_ratio)
        vol_score = self._normalize_volatility(volatility)

        return (de_score * 0.4 + liquidity_score * 0.3 + vol_score * 0.3) * 100

    def calculate_overall_score(
        self,
        value: float,
        growth: float,
        quality: float,
        safety: float,
        weights: tuple = (0.3, 0.3, 0.25, 0.15)
    ) -> float:
        """
        Calculate overall score (0-100, higher is better)
        Weighted combination of all scores
        """
        return (value * weights[0] + growth * weights[1] + quality * weights[2] + safety * weights[3])

    # Normalization helper methods (convert raw metrics to 0-1 scores)

    def _normalize_pe_score(self, pe: float) -> float:
        """Normalize P/E ratio to 0-1 score (lower P/E is better)"""
        if pe <= 0:
            return 0
        if pe < 10:
            return 1.0
        elif pe < 15:
            return 0.9
        elif pe < 20:
            return 0.8
        elif pe < 25:
            return 0.6
        elif pe < 30:
            return 0.4
        elif pe < 40:
            return 0.2
        else:
            return 0.1

    def _normalize_pb_score(self, pb: float) -> float:
        """Normalize P/B ratio to 0-1 score (lower P/B is better)"""
        if pb <= 0:
            return 0
        if pb < 1:
            return 1.0
        elif pb < 2:
            return 0.9
        elif pb < 3:
            return 0.7
        elif pb < 4:
            return 0.5
        elif pb < 5:
            return 0.3
        else:
            return 0.1

    def _normalize_de_score(self, de: float) -> float:
        """Normalize Debt/Equity to 0-1 score (lower is better)"""
        if de < 0:
            return 0
        if de < 0.3:
            return 1.0
        elif de < 0.5:
            return 0.9
        elif de < 1.0:
            return 0.7
        elif de < 1.5:
            return 0.5
        elif de < 2.0:
            return 0.3
        else:
            return 0.1

    def _normalize_growth(self, growth: float) -> float:
        """Normalize growth rate to 0-1 score (higher is better)"""
        if growth < 0:
            return max(0, 0.3 + growth / 100)  # Penalty for negative growth
        if growth > 50:
            return 1.0
        elif growth > 30:
            return 0.9
        elif growth > 20:
            return 0.8
        elif growth > 15:
            return 0.7
        elif growth > 10:
            return 0.6
        elif growth > 5:
            return 0.5
        else:
            return 0.3

    def _normalize_roe(self, roe: float) -> float:
        """Normalize ROE to 0-1 score (higher is better)"""
        if roe < 0:
            return 0
        if roe > 25:
            return 1.0
        elif roe > 20:
            return 0.9
        elif roe > 15:
            return 0.8
        elif roe > 12:
            return 0.7
        elif roe > 10:
            return 0.6
        elif roe > 8:
            return 0.5
        else:
            return 0.3

    def _normalize_margin(self, margin: float) -> float:
        """Normalize profit margin to 0-1 score (higher is better)"""
        if margin < 0:
            return 0
        if margin > 20:
            return 1.0
        elif margin > 15:
            return 0.9
        elif margin > 10:
            return 0.8
        elif margin > 7:
            return 0.7
        elif margin > 5:
            return 0.6
        else:
            return 0.4

    def _normalize_liquidity(self, current_ratio: float) -> float:
        """Normalize current ratio to 0-1 score (1.5-3 is ideal)"""
        if current_ratio < 0.5:
            return 0
        if 1.5 <= current_ratio <= 3:
            return 1.0
        elif 1.2 <= current_ratio < 1.5:
            return 0.8
        elif 3 < current_ratio <= 4:
            return 0.8
        elif 1.0 <= current_ratio < 1.2:
            return 0.6
        else:
            return 0.4

    def _normalize_volatility(self, volatility: float) -> float:
        """Normalize volatility to 0-1 score (lower is better)"""
        if volatility < 15:
            return 1.0
        elif volatility < 25:
            return 0.8
        elif volatility < 35:
            return 0.6
        elif volatility < 50:
            return 0.4
        else:
            return 0.2

    def calculate_metrics_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate metrics for all stocks in a DataFrame

        Args:
            df: DataFrame with stock data

        Returns:
            DataFrame with added metric columns
        """
        logger.info(f"Calculating metrics for {len(df)} stocks...")

        metrics_list = []
        for idx, row in df.iterrows():
            stock_dict = row.to_dict()
            metrics = self.calculate_all_metrics(stock_dict)
            metrics_list.append(metrics)

        metrics_df = pd.DataFrame(metrics_list)

        # Combine with original data
        result_df = pd.concat([df.reset_index(drop=True), metrics_df], axis=1)

        logger.info("Metrics calculation complete!")
        return result_df
