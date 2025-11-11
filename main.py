#!/usr/bin/env python3
"""
Simple entry point for Indian Stock Research Agent
Run this for a quick start with default settings
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from stock_agent.agent import StockResearchAgent
from stock_agent.config import AgentConfig
import pandas as pd


def main():
    """
    Main entry point - runs a complete stock analysis with default settings
    """

    print("="*70)
    print("INDIAN STOCK RESEARCH AGENT")
    print("="*70)
    print()

    # Get API key from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        print("⚠️  Warning: GEMINI_API_KEY not set. AI features will be disabled.")
        print("   To enable AI features, set the environment variable:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        print()

    # Create agent with default configuration
    print("🚀 Initializing agent...")
    config = AgentConfig()
    agent = StockResearchAgent(config=config, gemini_api_key=gemini_api_key)

    # Run analysis
    print("📊 Starting stock analysis...")
    print(f"   Analyzing {len(config.get_all_stocks())} stocks...")
    print()

    results = agent.run_full_analysis()

    # Display results
    if results.get('status') == 'success':
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE!")
        print("="*70)

        # Show top 10 stocks
        if 'recommendations' in results:
            top_stocks = pd.DataFrame(results['recommendations']['top_stocks'])

            print("\n🏆 TOP 10 RECOMMENDED STOCKS:\n")
            print(f"{'Rank':<6} {'Symbol':<14} {'Name':<30} {'Score':<8}")
            print("-" * 70)

            for idx, row in top_stocks.head(10).iterrows():
                rank = idx + 1
                symbol = row.get('symbol', 'N/A')
                name = row.get('name', 'N/A')[:28]
                score = row.get('overall_score', 0)

                print(f"{rank:<6} {symbol:<14} {name:<30} {score:.2f}")

        # Show output files
        if 'output_files' in results:
            print("\n📁 OUTPUT FILES:")
            for file_type, file_path in results['output_files'].items():
                print(f"   • {file_path}")

        print("\n" + "="*70)
        print("✨ Check the output directory for detailed CSV and JSON reports!")
        print("="*70)
        print()

    else:
        print(f"\n❌ Analysis failed: {results.get('error')}")
        print()
        return 1

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
