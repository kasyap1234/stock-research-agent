#!/usr/bin/env python3
"""
Example script demonstrating various features of the Stock Research Agent
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from stock_agent.agent import StockResearchAgent
from stock_agent.config import AgentConfig, ScoringWeights
import pandas as pd


def example_1_quick_analysis():
    """Example 1: Quick analysis of a few stocks"""

    print("\n" + "="*70)
    print("EXAMPLE 1: Quick Analysis of Top Indian IT Stocks")
    print("="*70 + "\n")

    # Create configuration with just IT stocks
    config = AgentConfig(
        nse_stocks=[
            "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"
        ],
        top_n_recommendations=5,
        enable_sentiment=True
    )

    # Initialize agent (without Gemini for this example)
    agent = StockResearchAgent(config=config)

    # Run analysis
    print("📊 Analyzing IT sector stocks...\n")
    results = agent.run_full_analysis()

    if results['status'] == 'success':
        print("✅ Analysis complete!\n")

        # Display top picks
        top_stocks = pd.DataFrame(results['recommendations']['top_stocks'])
        print("🏆 Top 5 IT Stocks:\n")

        for idx, row in top_stocks.iterrows():
            print(f"{idx+1}. {row['name']} ({row['symbol']})")
            print(f"   Price: ₹{row['current_price']:.2f}")
            print(f"   P/E: {row['pe_ratio']:.2f}")
            print(f"   ROE: {row['roe']:.2f}%")
            print(f"   Overall Score: {row['overall_score']:.2f}/100")
            print()


def example_2_value_investing():
    """Example 2: Value investing strategy"""

    print("\n" + "="*70)
    print("EXAMPLE 2: Value Investing Strategy")
    print("="*70 + "\n")

    # Configure for value investing
    config = AgentConfig(
        nse_stocks=[
            "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS",
            "TCS.NS", "INFY.NS",
            "RELIANCE.NS", "ITC.NS"
        ],

        # Emphasize value metrics
        scoring_weights=ScoringWeights(
            value_score_weight=0.5,    # 50% weight on value
            growth_score_weight=0.2,
            quality_score_weight=0.2,
            safety_score_weight=0.1
        ),

        # Value investing preferences
        ideal_pe_ratio=15.0,
        ideal_pb_ratio=2.0,

        top_n_recommendations=5,
        enable_sentiment=False  # Focus on fundamentals only
    )

    agent = StockResearchAgent(config=config)

    print("💰 Searching for undervalued stocks...\n")
    results = agent.run_full_analysis()

    if results['status'] == 'success':
        top_stocks = pd.DataFrame(results['recommendations']['top_stocks'])

        print("📊 Best Value Picks:\n")
        for idx, row in top_stocks.iterrows():
            print(f"{idx+1}. {row['name']} ({row['symbol']})")
            print(f"   P/E Ratio: {row['pe_ratio']:.2f} (lower is better)")
            print(f"   P/B Ratio: {row['pb_ratio']:.2f} (lower is better)")
            print(f"   Value Score: {row['value_score']:.2f}/100")
            print()


def example_3_compare_stocks():
    """Example 3: Compare two stocks"""

    print("\n" + "="*70)
    print("EXAMPLE 3: Compare Two Stocks")
    print("="*70 + "\n")

    # Compare HDFC Bank vs ICICI Bank
    stock_a = "HDFCBANK.NS"
    stock_b = "ICICIBANK.NS"

    agent = StockResearchAgent()

    print(f"⚖️  Comparing {stock_a} vs {stock_b}...\n")

    results = agent.analyze_specific_stocks([stock_a, stock_b], generate_report=False)

    if stock_a in results and stock_b in results:
        data_a = results[stock_a]
        data_b = results[stock_b]

        # Create comparison table
        comparison = {
            'Metric': [
                'Price (₹)', 'P/E Ratio', 'P/B Ratio', 'ROE (%)',
                'Debt/Equity', 'EPS Growth (%)', 'Overall Score'
            ],
            stock_a: [
                f"{data_a['current_price']:.2f}",
                f"{data_a['pe_ratio']:.2f}",
                f"{data_a['pb_ratio']:.2f}",
                f"{data_a['roe']:.2f}",
                f"{data_a['debt_to_equity']:.2f}",
                f"{data_a['eps_growth']:.2f}",
                f"{data_a['overall_score']:.2f}"
            ],
            stock_b: [
                f"{data_b['current_price']:.2f}",
                f"{data_b['pe_ratio']:.2f}",
                f"{data_b['pb_ratio']:.2f}",
                f"{data_b['roe']:.2f}",
                f"{data_b['debt_to_equity']:.2f}",
                f"{data_b['eps_growth']:.2f}",
                f"{data_b['overall_score']:.2f}"
            ]
        }

        df = pd.DataFrame(comparison)
        print(df.to_string(index=False))
        print()

        # Determine winner
        if data_a['overall_score'] > data_b['overall_score']:
            winner = stock_a
            winner_name = data_a['name']
        else:
            winner = stock_b
            winner_name = data_b['name']

        print(f"🏆 Winner: {winner_name} ({winner})")


def example_4_sector_analysis():
    """Example 4: Analyze multiple sectors"""

    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Sector Analysis")
    print("="*70 + "\n")

    sectors = {
        'IT': ["TCS.NS", "INFY.NS", "WIPRO.NS"],
        'Banking': ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
        'Pharma': ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"]
    }

    print("📊 Analyzing 3 sectors: IT, Banking, Pharma\n")

    for sector_name, stocks in sectors.items():
        print(f"\n--- {sector_name} Sector ---")

        config = AgentConfig(
            nse_stocks=stocks,
            top_n_recommendations=1,
            enable_sentiment=False
        )

        agent = StockResearchAgent(config=config)
        results = agent.run_full_analysis()

        if results['status'] == 'success' and results['recommendations']['top_stocks']:
            top_pick = results['recommendations']['top_stocks'][0]

            print(f"Top Pick: {top_pick['name']} ({top_pick['symbol']})")
            print(f"  Score: {top_pick['overall_score']:.2f}/100")
            print(f"  P/E: {top_pick['pe_ratio']:.2f}")
            print(f"  ROE: {top_pick['roe']:.2f}%")


def example_5_portfolio_check():
    """Example 5: Portfolio health check"""

    print("\n" + "="*70)
    print("EXAMPLE 5: Portfolio Health Check")
    print("="*70 + "\n")

    # Sample portfolio
    portfolio = {
        "TCS.NS": 50,
        "INFY.NS": 75,
        "HDFCBANK.NS": 30,
        "RELIANCE.NS": 40
    }

    print("📊 Analyzing your portfolio...\n")

    agent = StockResearchAgent()
    symbols = list(portfolio.keys())

    results = agent.analyze_specific_stocks(symbols, generate_report=False)

    total_value = 0

    print("Holdings:\n")
    for symbol, shares in portfolio.items():
        if symbol in results and 'error' not in results[symbol]:
            data = results[symbol]
            price = data['current_price']
            score = data['overall_score']
            value = price * shares

            total_value += value

            print(f"• {data['name']} ({symbol})")
            print(f"  Shares: {shares} | Price: ₹{price:.2f} | Value: ₹{value:,.2f}")
            print(f"  Score: {score:.2f}/100 ", end="")

            if score >= 70:
                print("✅ Strong")
            elif score >= 60:
                print("👍 Good")
            elif score >= 50:
                print("⚠️  Moderate")
            else:
                print("⚠️  Weak")
            print()

    print(f"Total Portfolio Value: ₹{total_value:,.2f}\n")


def main():
    """Run all examples"""

    print("\n" + "="*70)
    print("INDIAN STOCK RESEARCH AGENT - EXAMPLE DEMONSTRATIONS")
    print("="*70)

    # Run examples
    try:
        example_1_quick_analysis()
        input("\nPress Enter to continue to next example...")

        example_2_value_investing()
        input("\nPress Enter to continue to next example...")

        example_3_compare_stocks()
        input("\nPress Enter to continue to next example...")

        example_4_sector_analysis()
        input("\nPress Enter to continue to next example...")

        example_5_portfolio_check()

        print("\n" + "="*70)
        print("✅ All examples completed!")
        print("="*70)
        print("\nNote: Set GEMINI_API_KEY environment variable to enable AI features")
        print("Example: export GEMINI_API_KEY='your-key'\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # You can run individual examples:
    # example_1_quick_analysis()
    # example_2_value_investing()
    # example_3_compare_stocks()
    # example_4_sector_analysis()
    # example_5_portfolio_check()

    # Or run all examples:
    main()
