#!/usr/bin/env python3
"""
Command Line Interface for Indian Stock Research Agent
"""

import argparse
import sys
import os
import logging
from pathlib import Path
import json
from typing import Optional

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from stock_agent.agent import StockResearchAgent
from stock_agent.config import AgentConfig
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         INDIAN STOCK RESEARCH AGENT                           ║
    ║         AI-Powered Stock Analysis & Recommendations           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def display_top_stocks(stocks_df, top_n=10):
    """Display top stocks in a formatted table"""

    if stocks_df.empty:
        console.print("[red]No stocks to display[/red]")
        return

    table = Table(title=f"🏆 Top {top_n} Recommended Stocks", show_header=True, header_style="bold magenta")

    table.add_column("Rank", style="dim", width=6)
    table.add_column("Symbol", style="cyan", width=12)
    table.add_column("Name", style="white", width=25)
    table.add_column("Sector", style="yellow", width=15)
    table.add_column("Price (₹)", justify="right", style="green")
    table.add_column("P/E", justify="right")
    table.add_column("ROE %", justify="right")
    table.add_column("Score", justify="right", style="bold green")

    for idx, row in stocks_df.head(top_n).iterrows():
        rank = str(idx + 1)
        symbol = row.get('symbol', 'N/A')
        name = row.get('name', 'N/A')[:25]
        sector = row.get('sector', 'N/A')[:15]
        price = f"{row.get('current_price', 0):.2f}"
        pe = f"{row.get('pe_ratio', 0):.2f}" if row.get('pe_ratio', 0) > 0 else "N/A"
        roe = f"{row.get('roe', 0):.2f}" if row.get('roe', 0) > 0 else "N/A"
        score = f"{row.get('overall_score', 0):.2f}"

        table.add_row(rank, symbol, name, sector, price, pe, roe, score)

    console.print(table)


def display_strategy_picks(results):
    """Display picks by different strategies"""

    if 'recommendations_by_strategy' not in results:
        return

    strategies = results['recommendations_by_strategy']

    for strategy_name, stocks in strategies.items():
        if not stocks:
            continue

        table = Table(title=f"📊 Top {strategy_name.capitalize()} Picks", show_header=True)

        table.add_column("Symbol", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Score", justify="right", style="green")

        for stock in stocks[:5]:
            table.add_row(
                stock.get('symbol', 'N/A'),
                stock.get('name', 'N/A')[:30],
                f"{stock.get('overall_score', 0):.2f}"
            )

        console.print(table)


def display_ai_insights(insights):
    """Display AI-powered insights"""

    if not insights:
        return

    console.print("\n[bold cyan]🤖 AI-Powered Insights[/bold cyan]\n")

    if 'market_overview' in insights:
        panel = Panel(
            insights['market_overview'],
            title="Market Overview",
            border_style="blue"
        )
        console.print(panel)
        console.print()

    if 'top_pick_analysis' in insights:
        panel = Panel(
            insights['top_pick_analysis'],
            title="Top Pick Analysis",
            border_style="green"
        )
        console.print(panel)
        console.print()

    if 'sector_analysis' in insights:
        panel = Panel(
            insights['sector_analysis'],
            title="Sector Analysis",
            border_style="yellow"
        )
        console.print(panel)
        console.print()


def run_full_analysis(args):
    """Run full stock analysis"""

    print_banner()

    # Get Gemini API key
    gemini_api_key = args.gemini_api_key or os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        console.print("[yellow]Warning: No Gemini API key provided. AI features will be disabled.[/yellow]")
        console.print("[yellow]Set GEMINI_API_KEY environment variable or use --gemini-api-key flag[/yellow]\n")

    # Initialize agent
    console.print("[cyan]Initializing Stock Research Agent...[/cyan]")

    config = AgentConfig()

    # Override config if custom stocks provided
    if args.stocks:
        symbols = [s.strip() for s in args.stocks.split(',')]
        config.nse_stocks = symbols

    if args.top_n:
        config.top_n_recommendations = args.top_n

    agent = StockResearchAgent(config=config, gemini_api_key=gemini_api_key)

    # Run analysis
    console.print("\n[bold green]Starting analysis...[/bold green]\n")

    with Progress() as progress:
        task = progress.add_task("[cyan]Analyzing stocks...", total=100)

        results = agent.run_full_analysis(use_cache=not args.no_cache)

        progress.update(task, completed=100)

    if results.get('status') == 'failed':
        console.print(f"[red]Analysis failed: {results.get('error')}[/red]")
        return

    # Display results
    console.print("\n[bold green]✓ Analysis Complete![/bold green]\n")

    # Display summary statistics
    if 'summary' in results:
        summary = results['summary']
        console.print(f"[cyan]Total stocks analyzed: {summary.get('total_stocks_analyzed', 0)}[/cyan]")

    # Display top stocks
    if 'recommendations' in results and 'top_stocks' in results['recommendations']:
        import pandas as pd
        top_df = pd.DataFrame(results['recommendations']['top_stocks'])
        display_top_stocks(top_df, top_n=args.top_n or 10)

    # Display strategy picks
    if not args.no_strategy_picks:
        console.print("\n")
        display_strategy_picks(results)

    # Display AI insights
    if 'ai_insights' in results and not args.no_ai:
        display_ai_insights(results['ai_insights'])

    # Display output files
    if 'output_files' in results:
        console.print("\n[bold cyan]Output Files:[/bold cyan]")
        for file_type, file_path in results['output_files'].items():
            console.print(f"  • {file_type}: {file_path}")

    console.print("\n[bold green]Analysis complete! Check the output directory for detailed results.[/bold green]\n")


def analyze_specific(args):
    """Analyze specific stocks"""

    print_banner()

    symbols = [s.strip() for s in args.symbols.split(',')]

    gemini_api_key = args.gemini_api_key or os.getenv('GEMINI_API_KEY')

    agent = StockResearchAgent(gemini_api_key=gemini_api_key)

    console.print(f"\n[cyan]Analyzing: {', '.join(symbols)}[/cyan]\n")

    results = agent.analyze_specific_stocks(symbols, generate_report=True)

    for symbol, data in results.items():
        if 'error' in data:
            console.print(f"[red]Error for {symbol}: {data['error']}[/red]\n")
            continue

        # Display recommendation report
        if 'recommendation_report' in data:
            console.print(data['recommendation_report'])

        # Display sentiment if available
        if 'sentiment' in data:
            sentiment = data['sentiment']
            sentiment_color = "green" if sentiment['sentiment_label'] == 'positive' else "red" if sentiment['sentiment_label'] == 'negative' else "yellow"

            console.print(f"\n[{sentiment_color}]Sentiment: {sentiment['sentiment_label'].upper()} ({sentiment['sentiment_score']:.3f})[/{sentiment_color}]")
            console.print(f"News articles analyzed: {sentiment['news_count']}\n")


def interactive_mode(args):
    """Run agent in interactive Q&A mode"""

    print_banner()

    gemini_api_key = args.gemini_api_key or os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        console.print("[red]Error: Gemini API key required for interactive mode[/red]")
        console.print("[yellow]Set GEMINI_API_KEY environment variable or use --gemini-api-key flag[/yellow]")
        return

    agent = StockResearchAgent(gemini_api_key=gemini_api_key)

    console.print("\n[cyan]Interactive Mode - Ask questions about Indian stocks[/cyan]")
    console.print("[dim]Type 'exit' or 'quit' to exit[/dim]\n")

    # Optionally load context data
    context_data = None

    if args.load_analysis:
        try:
            import pandas as pd
            context_data = pd.read_csv(args.load_analysis)
            console.print(f"[green]Loaded analysis data from {args.load_analysis}[/green]\n")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load analysis file: {str(e)}[/yellow]\n")

    while True:
        try:
            question = console.input("[bold cyan]You:[/bold cyan] ")

            if question.lower() in ['exit', 'quit', 'q']:
                console.print("[cyan]Goodbye![/cyan]")
                break

            if not question.strip():
                continue

            console.print("\n[dim]Thinking...[/dim]\n")

            answer = agent.get_ai_answer(question, context_data=context_data)

            console.print(f"[bold green]Agent:[/bold green] {answer}\n")

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]\n")


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Indian Stock Research Agent - AI-powered stock analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full analysis with default stocks
  python cli.py analyze

  # Analyze specific stocks
  python cli.py analyze --stocks "TCS.NS,INFY.NS,RELIANCE.NS"

  # Analyze a single stock in detail
  python cli.py specific --symbols "HDFCBANK.NS"

  # Interactive Q&A mode
  python cli.py interactive --gemini-api-key "your-key"

  # Run with Gemini API key from environment
  export GEMINI_API_KEY="your-key"
  python cli.py analyze
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run full stock analysis')
    analyze_parser.add_argument(
        '--stocks',
        type=str,
        help='Comma-separated list of stock symbols (e.g., "TCS.NS,INFY.NS")'
    )
    analyze_parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of top recommendations (default: 10)'
    )
    analyze_parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching, fetch fresh data'
    )
    analyze_parser.add_argument(
        '--no-strategy-picks',
        action='store_true',
        help='Skip displaying strategy-specific picks'
    )
    analyze_parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI insights'
    )
    analyze_parser.add_argument(
        '--gemini-api-key',
        type=str,
        help='Gemini API key for AI features'
    )

    # Specific stock analysis
    specific_parser = subparsers.add_parser('specific', help='Analyze specific stocks in detail')
    specific_parser.add_argument(
        '--symbols',
        type=str,
        required=True,
        help='Comma-separated stock symbols to analyze'
    )
    specific_parser.add_argument(
        '--gemini-api-key',
        type=str,
        help='Gemini API key for AI features'
    )

    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive Q&A mode')
    interactive_parser.add_argument(
        '--gemini-api-key',
        type=str,
        help='Gemini API key (required for interactive mode)'
    )
    interactive_parser.add_argument(
        '--load-analysis',
        type=str,
        help='Load previous analysis CSV for context'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'analyze':
            run_full_analysis(args)
        elif args.command == 'specific':
            analyze_specific(args)
        elif args.command == 'interactive':
            interactive_mode(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == '__main__':
    main()
