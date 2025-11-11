"""
Stock Data Fetcher Module
Fetches stock data from Yahoo Finance using yfinance for Indian stocks (NSE/BSE)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """
    Fetches comprehensive stock data for Indian stocks from NSE and BSE
    """

    def __init__(self, delay: float = 0.5):
        """
        Initialize the data fetcher

        Args:
            delay: Delay between API requests in seconds
        """
        self.delay = delay
        self.cache: Dict[str, Dict] = {}
        self.cache_timestamp: Dict[str, datetime] = {}

    def fetch_stock_data(self, symbol: str, use_cache: bool = True, cache_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive data for a single stock

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            use_cache: Whether to use cached data
            cache_hours: Cache validity in hours

        Returns:
            Dictionary containing stock data or None if failed
        """
        # Check cache
        if use_cache and symbol in self.cache:
            cache_age = datetime.now() - self.cache_timestamp.get(symbol, datetime.min)
            if cache_age < timedelta(hours=cache_hours):
                logger.info(f"Using cached data for {symbol}")
                return self.cache[symbol]

        try:
            logger.info(f"Fetching data for {symbol}")
            ticker = yf.Ticker(symbol)

            # Fetch various data points
            info = ticker.info
            history = ticker.history(period="1y")
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            quarterly_financials = ticker.quarterly_financials

            # Extract key metrics
            stock_data = self._extract_stock_metrics(
                symbol, info, history, financials, balance_sheet, cashflow, quarterly_financials
            )

            # Cache the data
            self.cache[symbol] = stock_data
            self.cache_timestamp[symbol] = datetime.now()

            # Rate limiting
            time.sleep(self.delay)

            return stock_data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def _extract_stock_metrics(
        self,
        symbol: str,
        info: Dict,
        history: pd.DataFrame,
        financials: pd.DataFrame,
        balance_sheet: pd.DataFrame,
        cashflow: pd.DataFrame,
        quarterly_financials: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Extract and organize stock metrics from raw data

        Args:
            symbol: Stock symbol
            info: Stock info from yfinance
            history: Historical price data
            financials: Annual financials
            balance_sheet: Balance sheet data
            cashflow: Cash flow data
            quarterly_financials: Quarterly financials

        Returns:
            Dictionary with organized stock data
        """
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        if current_price == 0 and not history.empty:
            current_price = history['Close'].iloc[-1]

        # Basic info
        data = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'current_price': current_price,
            'currency': info.get('currency', 'INR'),
            'exchange': info.get('exchange', 'NSE'),
        }

        # Market metrics
        data.update({
            'market_cap': info.get('marketCap', 0),
            'market_cap_crores': info.get('marketCap', 0) / 10000000,  # Convert to crores
            'enterprise_value': info.get('enterpriseValue', 0),
            'shares_outstanding': info.get('sharesOutstanding', 0),
        })

        # Price metrics
        data.update({
            'previous_close': info.get('previousClose', 0),
            'open': info.get('open', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'volume': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0),
        })

        # Valuation ratios
        data.update({
            'pe_ratio': info.get('trailingPE', 0) or info.get('forwardPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
        })

        # Profitability metrics
        data.update({
            'profit_margins': info.get('profitMargins', 0),
            'operating_margins': info.get('operatingMargins', 0),
            'gross_margins': info.get('grossMargins', 0),
            'roe': info.get('returnOnEquity', 0),
            'roa': info.get('returnOnAssets', 0),
        })

        # Earnings metrics
        data.update({
            'eps': info.get('trailingEps', 0) or info.get('forwardEps', 0),
            'forward_eps': info.get('forwardEps', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0),
        })

        # Dividend metrics
        data.update({
            'dividend_rate': info.get('dividendRate', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'payout_ratio': info.get('payoutRatio', 0),
        })

        # Debt metrics
        data.update({
            'total_debt': info.get('totalDebt', 0),
            'total_cash': info.get('totalCash', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'quick_ratio': info.get('quickRatio', 0),
        })

        # Balance sheet data
        if not balance_sheet.empty:
            try:
                latest_bs = balance_sheet.iloc[:, 0]
                data.update({
                    'total_assets': latest_bs.get('Total Assets', 0),
                    'total_liabilities': latest_bs.get('Total Liabilities Net Minority Interest', 0),
                    'stockholder_equity': latest_bs.get('Stockholders Equity', 0) or latest_bs.get('Total Equity Gross Minority Interest', 0),
                })
            except Exception as e:
                logger.debug(f"Error extracting balance sheet for {symbol}: {e}")

        # Financials data
        if not financials.empty:
            try:
                latest_fin = financials.iloc[:, 0]
                data.update({
                    'total_revenue': latest_fin.get('Total Revenue', 0),
                    'net_income': latest_fin.get('Net Income', 0),
                    'operating_income': latest_fin.get('Operating Income', 0),
                    'ebitda': info.get('ebitda', 0),
                })

                # Calculate growth rates if we have historical data
                if financials.shape[1] > 1:
                    try:
                        current_revenue = financials.iloc[0, 0] if 'Total Revenue' in financials.index else 0
                        previous_revenue = financials.iloc[0, 1] if 'Total Revenue' in financials.index else 0
                        if previous_revenue and previous_revenue != 0:
                            data['revenue_growth_calculated'] = ((current_revenue - previous_revenue) / abs(previous_revenue)) * 100

                        current_ni = financials.iloc[0, 0] if 'Net Income' in financials.index else 0
                        previous_ni = financials.iloc[0, 1] if 'Net Income' in financials.index else 0
                        if previous_ni and previous_ni != 0:
                            data['net_income_growth'] = ((current_ni - previous_ni) / abs(previous_ni)) * 100
                    except:
                        pass

            except Exception as e:
                logger.debug(f"Error extracting financials for {symbol}: {e}")

        # Historical performance
        if not history.empty:
            try:
                data.update({
                    'ytd_return': self._calculate_ytd_return(history),
                    'one_year_return': self._calculate_return(history, days=252),
                    'six_month_return': self._calculate_return(history, days=126),
                    'three_month_return': self._calculate_return(history, days=63),
                    'one_month_return': self._calculate_return(history, days=21),
                    'volatility': self._calculate_volatility(history),
                })
            except Exception as e:
                logger.debug(f"Error calculating returns for {symbol}: {e}")

        # Book value per share
        if data.get('stockholder_equity', 0) and data.get('shares_outstanding', 0):
            data['book_value_per_share'] = data['stockholder_equity'] / data['shares_outstanding']
        else:
            data['book_value_per_share'] = 0

        # Calculate missing P/B ratio if we have book value
        if not data['pb_ratio'] and data['book_value_per_share'] and current_price:
            data['pb_ratio'] = current_price / data['book_value_per_share']

        # Data completeness score
        data['data_completeness'] = self._calculate_data_completeness(data)

        # Last updated timestamp
        data['last_updated'] = datetime.now().isoformat()

        return data

    def _calculate_ytd_return(self, history: pd.DataFrame) -> float:
        """Calculate year-to-date return"""
        try:
            if history.empty:
                return 0

            current_year = datetime.now().year
            ytd_data = history[history.index.year == current_year]

            if len(ytd_data) < 2:
                return 0

            start_price = ytd_data['Close'].iloc[0]
            end_price = ytd_data['Close'].iloc[-1]

            return ((end_price - start_price) / start_price) * 100
        except:
            return 0

    def _calculate_return(self, history: pd.DataFrame, days: int) -> float:
        """Calculate return over specified number of days"""
        try:
            if len(history) < days:
                return 0

            start_price = history['Close'].iloc[-days]
            end_price = history['Close'].iloc[-1]

            return ((end_price - start_price) / start_price) * 100
        except:
            return 0

    def _calculate_volatility(self, history: pd.DataFrame, period: int = 252) -> float:
        """Calculate annualized volatility"""
        try:
            if history.empty:
                return 0

            returns = history['Close'].pct_change().dropna()
            return returns.std() * np.sqrt(period) * 100
        except:
            return 0

    def _calculate_data_completeness(self, data: Dict) -> float:
        """
        Calculate what percentage of important fields have valid data

        Args:
            data: Stock data dictionary

        Returns:
            Completeness score between 0 and 1
        """
        important_fields = [
            'current_price', 'market_cap', 'pe_ratio', 'pb_ratio', 'eps',
            'roe', 'debt_to_equity', 'total_revenue', 'net_income',
            'stockholder_equity', 'dividend_yield'
        ]

        valid_count = sum(
            1 for field in important_fields
            if data.get(field) and data[field] != 0
        )

        return valid_count / len(important_fields)

    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        use_cache: bool = True,
        max_workers: int = 5
    ) -> pd.DataFrame:
        """
        Fetch data for multiple stocks using parallel processing

        Args:
            symbols: List of stock symbols
            use_cache: Whether to use cached data
            max_workers: Maximum number of parallel workers

        Returns:
            DataFrame containing data for all stocks
        """
        results = []

        logger.info(f"Fetching data for {len(symbols)} stocks...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_stock_data, symbol, use_cache): symbol
                for symbol in symbols
            }

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                        logger.info(f"✓ Successfully fetched {symbol}")
                    else:
                        logger.warning(f"✗ Failed to fetch {symbol}")
                except Exception as e:
                    logger.error(f"✗ Exception for {symbol}: {str(e)}")

        logger.info(f"Successfully fetched {len(results)} out of {len(symbols)} stocks")

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV"""
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")

    def load_from_csv(self, filename: str) -> pd.DataFrame:
        """Load DataFrame from CSV"""
        return pd.read_csv(filename)
