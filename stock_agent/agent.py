"""
Main Stock Research Agent
Orchestrates the entire stock analysis workflow with Gemini API integration
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
import logging
import json
import os
from datetime import datetime
from pathlib import Path

# Import modules
from stock_agent.modules.data_fetcher import StockDataFetcher
from stock_agent.modules.metrics_calculator import MetricsCalculator
from stock_agent.modules.stock_ranker import StockRanker
from stock_agent.modules.sentiment_analyzer import SentimentAnalyzer
from stock_agent.config import AgentConfig, default_config

# Import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI package not available. Gemini features will be disabled.")

logger = logging.getLogger(__name__)


class StockResearchAgent:
    """
    Main agent that orchestrates stock research with AI-powered insights
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize the stock research agent

        Args:
            config: Agent configuration
            gemini_api_key: Google Gemini API key
        """
        self.config = config or default_config

        # Initialize modules
        self.data_fetcher = StockDataFetcher(delay=self.config.request_delay_seconds)
        self.metrics_calculator = MetricsCalculator()
        self.stock_ranker = StockRanker(
            value_weight=self.config.scoring_weights.value_score_weight,
            growth_weight=self.config.scoring_weights.growth_score_weight,
            quality_weight=self.config.scoring_weights.quality_score_weight,
            safety_weight=self.config.scoring_weights.safety_score_weight
        )
        self.sentiment_analyzer = SentimentAnalyzer() if self.config.enable_sentiment else None

        # Initialize Gemini API
        self.gemini_model = None
        if GEMINI_AVAILABLE and gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✓ Gemini API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {str(e)}")
        elif not gemini_api_key:
            logger.warning("No Gemini API key provided. AI-powered insights will be disabled.")

        # Create output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    def run_full_analysis(
        self,
        symbols: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete stock analysis workflow

        Args:
            symbols: List of stock symbols (uses config if None)
            use_cache: Whether to use cached data

        Returns:
            Dictionary with analysis results
        """
        logger.info("="*70)
        logger.info("INDIAN STOCK RESEARCH AGENT - FULL ANALYSIS")
        logger.info("="*70)

        results = {
            'start_time': datetime.now().isoformat(),
            'config': self.config.dict() if hasattr(self.config, 'dict') else {},
            'steps': {}
        }

        try:
            # Step 1: Fetch stock data
            logger.info("\n📊 STEP 1: Fetching stock data...")
            symbols = symbols or self.config.get_all_stocks()
            stock_data_df = self.data_fetcher.fetch_multiple_stocks(
                symbols,
                use_cache=use_cache
            )

            if stock_data_df.empty:
                logger.error("No stock data fetched. Aborting analysis.")
                results['error'] = "No stock data available"
                return results

            results['steps']['data_fetching'] = {
                'total_requested': len(symbols),
                'successfully_fetched': len(stock_data_df),
                'failed': len(symbols) - len(stock_data_df)
            }

            logger.info(f"✓ Fetched data for {len(stock_data_df)} stocks")

            # Step 2: Calculate metrics
            logger.info("\n📈 STEP 2: Calculating financial metrics...")
            analyzed_df = self.metrics_calculator.calculate_metrics_for_dataframe(stock_data_df)

            results['steps']['metrics_calculation'] = {
                'stocks_analyzed': len(analyzed_df),
                'metrics_calculated': True
            }

            logger.info(f"✓ Calculated metrics for {len(analyzed_df)} stocks")

            # Step 3: Add sentiment analysis
            if self.config.enable_sentiment and self.sentiment_analyzer:
                logger.info("\n💭 STEP 3: Analyzing sentiment...")
                analyzed_df = self.sentiment_analyzer.add_sentiment_to_dataframe(
                    analyzed_df,
                    sentiment_weight=self.config.sentiment_weight
                )

                results['steps']['sentiment_analysis'] = {
                    'enabled': True,
                    'stocks_analyzed': len(analyzed_df)
                }

                logger.info("✓ Sentiment analysis complete")
            else:
                results['steps']['sentiment_analysis'] = {'enabled': False}

            # Step 4: Rank stocks
            logger.info("\n🏆 STEP 4: Ranking stocks...")
            ranked_df = self.stock_ranker.rank_stocks(
                analyzed_df,
                min_market_cap=self.config.min_market_cap,
                min_data_quality=self.config.min_data_quality
            )

            if ranked_df.empty:
                logger.error("No stocks passed the ranking filters.")
                results['error'] = "No stocks qualified after filtering"
                return results

            results['steps']['ranking'] = {
                'stocks_ranked': len(ranked_df),
                'top_n': self.config.top_n_recommendations
            }

            logger.info(f"✓ Ranked {len(ranked_df)} stocks")

            # Step 5: Get recommendations
            logger.info("\n🎯 STEP 5: Generating recommendations...")
            top_stocks = self.stock_ranker.get_top_recommendations(
                ranked_df,
                top_n=self.config.top_n_recommendations,
                strategy='balanced'
            )

            results['recommendations'] = {
                'top_stocks': top_stocks.to_dict('records'),
                'count': len(top_stocks)
            }

            # Generate different strategy recommendations
            results['recommendations_by_strategy'] = {}
            for strategy in ['value', 'growth', 'quality', 'safety']:
                strategy_picks = self.stock_ranker.get_top_recommendations(
                    ranked_df,
                    top_n=5,
                    strategy=strategy
                )
                results['recommendations_by_strategy'][strategy] = strategy_picks[['symbol', 'name', 'overall_score']].to_dict('records')

            logger.info(f"✓ Generated top {len(top_stocks)} recommendations")

            # Step 6: Generate AI-powered insights (if Gemini is available)
            if self.gemini_model:
                logger.info("\n🤖 STEP 6: Generating AI-powered insights...")
                try:
                    ai_insights = self._generate_ai_insights(top_stocks, ranked_df)
                    results['ai_insights'] = ai_insights
                    logger.info("✓ AI insights generated")
                except Exception as e:
                    logger.error(f"Failed to generate AI insights: {str(e)}")
                    results['ai_insights'] = {'error': str(e)}

            # Step 7: Generate summary report
            logger.info("\n📋 STEP 7: Generating summary report...")
            summary = self.stock_ranker.generate_summary_report(
                ranked_df,
                top_n=self.config.top_n_recommendations
            )
            results['summary'] = summary

            # Step 8: Save outputs
            logger.info("\n💾 STEP 8: Saving outputs...")
            output_files = self._save_outputs(ranked_df, top_stocks, results)
            results['output_files'] = output_files

            results['end_time'] = datetime.now().isoformat()
            results['status'] = 'success'

            logger.info("\n" + "="*70)
            logger.info("✓ ANALYSIS COMPLETE!")
            logger.info("="*70)

            return results

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            results['error'] = str(e)
            results['status'] = 'failed'
            return results

    def _generate_ai_insights(self, top_stocks: pd.DataFrame, all_stocks: pd.DataFrame) -> Dict[str, str]:
        """
        Generate AI-powered insights using Gemini API

        Args:
            top_stocks: DataFrame with top recommended stocks
            all_stocks: DataFrame with all analyzed stocks

        Returns:
            Dictionary with AI insights
        """
        insights = {}

        # Prepare data summary for Gemini
        top_5 = top_stocks.head(5)

        summary_text = "Here are the top 5 Indian stocks based on comprehensive analysis:\n\n"

        for idx, row in top_5.iterrows():
            summary_text += f"{idx+1}. {row['name']} ({row['symbol']})\n"
            summary_text += f"   - Sector: {row.get('sector', 'N/A')}\n"
            summary_text += f"   - Current Price: ₹{row.get('current_price', 0):.2f}\n"
            summary_text += f"   - P/E Ratio: {row.get('pe_ratio', 0):.2f}\n"
            summary_text += f"   - ROE: {row.get('roe', 0):.2f}%\n"
            summary_text += f"   - EPS Growth: {row.get('eps_growth', 0):.2f}%\n"
            summary_text += f"   - Debt/Equity: {row.get('debt_to_equity', 0):.2f}\n"
            summary_text += f"   - Overall Score: {row.get('overall_score', 0):.2f}/100\n\n"

        # Generate market overview
        try:
            prompt = f"""As a financial analyst, provide a brief market overview and investment insights based on these top Indian stocks:

{summary_text}

Please provide:
1. A brief market sentiment summary (2-3 sentences)
2. Key sectoral trends visible from these stocks (2-3 sentences)
3. General investment considerations for these stocks (2-3 sentences)

Keep the response concise and professional."""

            response = self.gemini_model.generate_content(prompt)
            insights['market_overview'] = response.text

        except Exception as e:
            logger.error(f"Error generating market overview: {str(e)}")
            insights['market_overview'] = "Unable to generate AI insights at this time."

        # Generate top pick analysis
        try:
            if not top_5.empty:
                top_pick = top_5.iloc[0]
                prompt = f"""Analyze this top-ranked Indian stock and explain why it might be a good investment:

Stock: {top_pick['name']} ({top_pick['symbol']})
Sector: {top_pick.get('sector', 'N/A')}
Current Price: ₹{top_pick.get('current_price', 0):.2f}
P/E Ratio: {top_pick.get('pe_ratio', 0):.2f}
P/B Ratio: {top_pick.get('pb_ratio', 0):.2f}
ROE: {top_pick.get('roe', 0):.2f}%
Debt/Equity: {top_pick.get('debt_to_equity', 0):.2f}
EPS Growth: {top_pick.get('eps_growth', 0):.2f}%
Overall Score: {top_pick.get('overall_score', 0):.2f}/100

Provide a 3-4 sentence analysis highlighting the key strengths and any potential concerns."""

                response = self.gemini_model.generate_content(prompt)
                insights['top_pick_analysis'] = response.text

        except Exception as e:
            logger.error(f"Error generating top pick analysis: {str(e)}")
            insights['top_pick_analysis'] = "Unable to generate top pick analysis."

        # Generate sector analysis
        try:
            if 'sector' in all_stocks.columns:
                sector_stats = all_stocks.groupby('sector').agg({
                    'overall_score': 'mean',
                    'symbol': 'count'
                }).round(2)

                sector_text = "Sector-wise average scores:\n"
                for sector, row in sector_stats.iterrows():
                    sector_text += f"- {sector}: {row['overall_score']:.2f} ({int(row['symbol'])} stocks)\n"

                prompt = f"""Based on this sector analysis of Indian stocks:

{sector_text}

Which 2-3 sectors look most promising for investment and why? (Keep it brief, 2-3 sentences)"""

                response = self.gemini_model.generate_content(prompt)
                insights['sector_analysis'] = response.text

        except Exception as e:
            logger.error(f"Error generating sector analysis: {str(e)}")
            insights['sector_analysis'] = "Unable to generate sector analysis."

        return insights

    def _save_outputs(
        self,
        ranked_df: pd.DataFrame,
        top_stocks: pd.DataFrame,
        results: Dict
    ) -> Dict[str, str]:
        """
        Save outputs to various formats

        Args:
            ranked_df: Full ranked DataFrame
            top_stocks: Top recommendations DataFrame
            results: Full results dictionary

        Returns:
            Dictionary with output file paths
        """
        output_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save full analysis to CSV
        if self.config.output_csv:
            csv_path = os.path.join(
                self.config.output_dir,
                f"stock_analysis_full_{timestamp}.csv"
            )
            ranked_df.to_csv(csv_path, index=False)
            output_files['full_csv'] = csv_path
            logger.info(f"✓ Saved full analysis to {csv_path}")

            # Save top recommendations to CSV
            top_csv_path = os.path.join(
                self.config.output_dir,
                f"top_recommendations_{timestamp}.csv"
            )
            top_stocks.to_csv(top_csv_path, index=False)
            output_files['top_csv'] = top_csv_path
            logger.info(f"✓ Saved top recommendations to {top_csv_path}")

        # Save results to JSON
        if self.config.output_json:
            json_path = os.path.join(
                self.config.output_dir,
                f"analysis_results_{timestamp}.json"
            )

            # Convert DataFrames to serializable format
            results_copy = results.copy()
            if 'recommendations' in results_copy and 'top_stocks' in results_copy['recommendations']:
                # Already in dict format from to_dict('records')
                pass

            with open(json_path, 'w') as f:
                json.dump(results_copy, f, indent=2, default=str)

            output_files['json'] = json_path
            logger.info(f"✓ Saved results to {json_path}")

        return output_files

    def analyze_specific_stocks(
        self,
        symbols: List[str],
        generate_report: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze specific stocks and optionally generate detailed reports

        Args:
            symbols: List of stock symbols to analyze
            generate_report: Whether to generate detailed text reports

        Returns:
            Analysis results
        """
        logger.info(f"Analyzing specific stocks: {', '.join(symbols)}")

        results = {}

        for symbol in symbols:
            try:
                # Fetch data
                stock_data = self.data_fetcher.fetch_stock_data(symbol)

                if not stock_data:
                    results[symbol] = {'error': 'Failed to fetch data'}
                    continue

                # Calculate metrics
                metrics = self.metrics_calculator.calculate_all_metrics(stock_data)

                # Combine data and metrics
                full_data = {**stock_data, **metrics}

                # Add sentiment if enabled
                if self.config.enable_sentiment and self.sentiment_analyzer:
                    sentiment = self.sentiment_analyzer.analyze_stock_sentiment(symbol)
                    full_data['sentiment'] = sentiment

                # Generate explanation
                if generate_report:
                    explanation = self.stock_ranker.explain_recommendation(full_data)
                    full_data['recommendation_report'] = explanation

                results[symbol] = full_data

            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                results[symbol] = {'error': str(e)}

        return results

    def get_ai_answer(self, question: str, context_data: Optional[pd.DataFrame] = None) -> str:
        """
        Get AI-powered answer to a question about stocks using Gemini

        Args:
            question: User's question
            context_data: Optional DataFrame with stock data for context

        Returns:
            AI-generated answer
        """
        if not self.gemini_model:
            return "AI features are not available. Please provide a Gemini API key."

        try:
            # Build context
            context = "You are a financial analyst assistant specializing in Indian stock markets.\n\n"

            if context_data is not None and not context_data.empty:
                context += "Here is the current stock data:\n"
                # Add summary statistics
                context += f"Total stocks analyzed: {len(context_data)}\n"

                if 'sector' in context_data.columns:
                    context += f"Sectors: {', '.join(context_data['sector'].unique())}\n"

                # Add top 5 stocks
                if 'overall_score' in context_data.columns:
                    top_5 = context_data.nlargest(5, 'overall_score')
                    context += "\nTop 5 stocks:\n"
                    for idx, row in top_5.iterrows():
                        context += f"- {row['name']} ({row['symbol']}): Score {row['overall_score']:.2f}\n"

            context += f"\nUser Question: {question}\n\n"
            context += "Please provide a helpful, accurate answer based on the data. If the data doesn't contain enough information, say so."

            response = self.gemini_model.generate_content(context)
            return response.text

        except Exception as e:
            logger.error(f"Error generating AI answer: {str(e)}")
            return f"Error: Unable to generate AI answer. {str(e)}"
