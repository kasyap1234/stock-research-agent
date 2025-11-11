# Usage Guide - Indian Stock Research Agent

This guide provides detailed examples and use cases for the Stock Research Agent.

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Advanced Usage](#advanced-usage)
3. [Programmatic Usage](#programmatic-usage)
4. [Custom Configuration](#custom-configuration)
5. [Use Cases](#use-cases)

## Basic Usage

### 1. Quick Start - Default Analysis

The simplest way to run the agent:

```bash
python main.py
```

This will:
- Analyze 40+ popular Indian stocks from NSE
- Calculate all financial metrics
- Perform sentiment analysis
- Generate recommendations
- Save results to `output/` directory

### 2. CLI Full Analysis

For more control:

```bash
python cli.py analyze
```

**With custom stocks:**
```bash
python cli.py analyze --stocks "TCS.NS,INFY.NS,WIPRO.NS,HCLTECH.NS,TECHM.NS"
```

**Get top 20 recommendations:**
```bash
python cli.py analyze --top-n 20
```

**Fresh data (no cache):**
```bash
python cli.py analyze --no-cache
```

### 3. Analyze Specific Stocks

Deep dive into specific stocks:

```bash
# Single stock
python cli.py specific --symbols "RELIANCE.NS"

# Multiple stocks
python cli.py specific --symbols "TCS.NS,INFY.NS,HDFCBANK.NS"
```

This provides:
- Detailed financial metrics
- Valuation analysis
- Growth assessment
- Quality and safety scores
- Sentiment analysis
- Investment recommendation

### 4. Interactive Mode

Chat with the AI about stocks:

```bash
export GEMINI_API_KEY='your-key'
python cli.py interactive
```

Example conversation:
```
You: Which IT stocks have the best growth potential?
Agent: Based on the analysis, TCS and Infosys show strong growth...

You: What's the debt situation for Reliance?
Agent: Reliance Industries has a debt-to-equity ratio of...

You: Compare HDFC Bank and ICICI Bank
Agent: Both are strong banking stocks. HDFC Bank shows...
```

## Advanced Usage

### Environment Variables

Set up your environment:

```bash
# Required for AI features
export GEMINI_API_KEY='your-gemini-api-key'

# Optional: Custom output directory
export OUTPUT_DIR='./my_analysis'

# Optional: Logging level
export LOG_LEVEL='DEBUG'
```

### Custom Stock Lists

Create a file `my_stocks.txt`:
```
TCS.NS
INFY.NS
WIPRO.NS
HCLTECH.NS
TECHM.NS
```

Run analysis:
```bash
python cli.py analyze --stocks "$(cat my_stocks.txt | tr '\n' ',')"
```

### Sector-Specific Analysis

**Analyze IT sector:**
```bash
python cli.py analyze --stocks "TCS.NS,INFY.NS,WIPRO.NS,HCLTECH.NS,TECHM.NS"
```

**Analyze Banking sector:**
```bash
python cli.py analyze --stocks "HDFCBANK.NS,ICICIBANK.NS,KOTAKBANK.NS,AXISBANK.NS,SBIN.NS"
```

**Analyze Pharma sector:**
```bash
python cli.py analyze --stocks "SUNPHARMA.NS,DRREDDY.NS,CIPLA.NS,DIVISLAB.NS,LUPIN.NS"
```

## Programmatic Usage

### Basic Python Script

```python
from stock_agent.agent import StockResearchAgent
import os

# Initialize agent
api_key = os.getenv('GEMINI_API_KEY')
agent = StockResearchAgent(gemini_api_key=api_key)

# Run full analysis
results = agent.run_full_analysis()

# Access results
if results['status'] == 'success':
    top_stocks = results['recommendations']['top_stocks']

    for stock in top_stocks[:5]:
        print(f"{stock['symbol']}: {stock['name']} - Score: {stock['overall_score']:.2f}")
```

### Custom Configuration

```python
from stock_agent.agent import StockResearchAgent
from stock_agent.config import AgentConfig, ScoringWeights

# Create custom configuration
config = AgentConfig(
    # Custom stock list
    nse_stocks=[
        "TCS.NS", "INFY.NS", "HDFCBANK.NS", "RELIANCE.NS", "ICICIBANK.NS"
    ],

    # Recommendations
    top_n_recommendations=15,

    # Filtering
    min_market_cap=5000,  # Only large caps
    min_data_quality=0.7,  # High quality data only

    # Sentiment
    enable_sentiment=True,
    sentiment_weight=0.15,

    # Output
    output_csv=True,
    output_json=True,
    output_dir="my_output"
)

# Custom scoring weights
config.scoring_weights = ScoringWeights(
    value_score_weight=0.4,    # Emphasize value
    growth_score_weight=0.2,   # Less emphasis on growth
    quality_score_weight=0.3,
    safety_score_weight=0.1
)

# Initialize with custom config
agent = StockResearchAgent(config=config, gemini_api_key="your-key")

# Run analysis
results = agent.run_full_analysis()
```

### Analyze Specific Stocks Programmatically

```python
from stock_agent.agent import StockResearchAgent

agent = StockResearchAgent()

# Analyze specific stocks
symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
results = agent.analyze_specific_stocks(symbols, generate_report=True)

# Print detailed reports
for symbol, data in results.items():
    if 'recommendation_report' in data:
        print(data['recommendation_report'])
```

### Ask AI Questions

```python
from stock_agent.agent import StockResearchAgent
import pandas as pd

agent = StockResearchAgent(gemini_api_key="your-key")

# Load previous analysis for context
df = pd.read_csv("output/stock_analysis_full_20240101_120000.csv")

# Ask questions
answer = agent.get_ai_answer(
    "Which stocks have the best risk-reward ratio?",
    context_data=df
)

print(answer)
```

## Custom Configuration

### Creating a Config File

Create `my_config.py`:

```python
from stock_agent.config import AgentConfig, ScoringWeights

# Value investing configuration
value_config = AgentConfig(
    nse_stocks=[
        # Add your stocks here
        "TCS.NS", "INFY.NS", # ... more stocks
    ],

    scoring_weights=ScoringWeights(
        value_score_weight=0.5,   # Heavy weight on value
        growth_score_weight=0.2,
        quality_score_weight=0.2,
        safety_score_weight=0.1
    ),

    # Value investor preferences
    ideal_pe_ratio=15.0,
    ideal_pb_ratio=2.0,
    ideal_debt_equity=0.5,

    top_n_recommendations=10,
    min_market_cap=2000,
    enable_sentiment=False  # Pure fundamentals
)

# Growth investing configuration
growth_config = AgentConfig(
    scoring_weights=ScoringWeights(
        value_score_weight=0.1,
        growth_score_weight=0.6,  # Heavy weight on growth
        quality_score_weight=0.2,
        safety_score_weight=0.1
    ),

    min_market_cap=500,  # Include mid-caps for growth
    enable_sentiment=True
)
```

Use it:
```python
from my_config import value_config
from stock_agent.agent import StockResearchAgent

agent = StockResearchAgent(config=value_config)
results = agent.run_full_analysis()
```

## Use Cases

### Use Case 1: Daily Stock Screening

Create a daily screening script `daily_screen.py`:

```python
#!/usr/bin/env python3
from stock_agent.agent import StockResearchAgent
from stock_agent.config import AgentConfig
import datetime

# Configure for daily screening
config = AgentConfig(
    top_n_recommendations=20,
    enable_sentiment=True,
    output_dir=f"daily_screens/{datetime.date.today()}"
)

agent = StockResearchAgent(config=config)
results = agent.run_full_analysis(use_cache=False)  # Fresh data

print(f"Analysis complete. Top picks saved to {config.output_dir}")
```

Run daily:
```bash
python daily_screen.py
```

### Use Case 2: Sector Rotation Strategy

```python
from stock_agent.agent import StockResearchAgent
from stock_agent.config import AgentConfig

sectors = {
    'IT': ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
    'Banking': ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS"],
    'Pharma': ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
    'Auto': ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS"]
}

results = {}

for sector_name, stocks in sectors.items():
    config = AgentConfig(nse_stocks=stocks)
    agent = StockResearchAgent(config=config)

    sector_results = agent.run_full_analysis()
    results[sector_name] = sector_results

    # Get top pick from this sector
    if sector_results['status'] == 'success':
        top_pick = sector_results['recommendations']['top_stocks'][0]
        print(f"\n{sector_name} Top Pick: {top_pick['symbol']} - {top_pick['name']}")
        print(f"Score: {top_pick['overall_score']:.2f}")
```

### Use Case 3: Compare Two Stocks

```python
from stock_agent.agent import StockResearchAgent
import pandas as pd

agent = StockResearchAgent()

# Compare two stocks
stock_a = "TCS.NS"
stock_b = "INFY.NS"

results = agent.analyze_specific_stocks([stock_a, stock_b])

# Create comparison
comparison = pd.DataFrame([
    {
        'Metric': 'P/E Ratio',
        stock_a: results[stock_a]['pe_ratio'],
        stock_b: results[stock_b]['pe_ratio']
    },
    {
        'Metric': 'ROE',
        stock_a: results[stock_a]['roe'],
        stock_b: results[stock_b]['roe']
    },
    {
        'Metric': 'EPS Growth',
        stock_a: results[stock_a]['eps_growth'],
        stock_b: results[stock_b]['eps_growth']
    },
    {
        'Metric': 'Overall Score',
        stock_a: results[stock_a]['overall_score'],
        stock_b: results[stock_b]['overall_score']
    }
])

print(comparison.to_string(index=False))
```

### Use Case 4: Portfolio Health Check

```python
from stock_agent.agent import StockResearchAgent

# Your portfolio
portfolio = {
    "TCS.NS": 100,      # shares
    "INFY.NS": 150,
    "HDFCBANK.NS": 50,
    "RELIANCE.NS": 75
}

agent = StockResearchAgent()
symbols = list(portfolio.keys())

# Analyze portfolio stocks
results = agent.analyze_specific_stocks(symbols)

print("\n=== PORTFOLIO HEALTH CHECK ===\n")

for symbol, shares in portfolio.items():
    data = results[symbol]
    current_price = data['current_price']
    overall_score = data['overall_score']

    holding_value = current_price * shares

    print(f"{symbol}:")
    print(f"  Shares: {shares}")
    print(f"  Current Price: ₹{current_price:.2f}")
    print(f"  Holding Value: ₹{holding_value:,.2f}")
    print(f"  Overall Score: {overall_score:.2f}/100")

    if overall_score >= 70:
        print(f"  ✓ Strong - Consider holding/buying")
    elif overall_score >= 50:
        print(f"  ~ Moderate - Monitor closely")
    else:
        print(f"  ✗ Weak - Consider reviewing position")
    print()
```

### Use Case 5: Automated Email Reports

```python
from stock_agent.agent import StockResearchAgent
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

agent = StockResearchAgent(gemini_api_key="your-key")
results = agent.run_full_analysis()

if results['status'] == 'success':
    # Prepare email
    msg = MIMEMultipart()
    msg['Subject'] = f"Daily Stock Report - {results['start_time']}"
    msg['From'] = "agent@example.com"
    msg['To'] = "you@example.com"

    # Create body
    top_stocks = results['recommendations']['top_stocks'][:5]

    body = "Top 5 Stock Recommendations:\n\n"
    for i, stock in enumerate(top_stocks, 1):
        body += f"{i}. {stock['name']} ({stock['symbol']})\n"
        body += f"   Score: {stock['overall_score']:.2f}\n"
        body += f"   Price: ₹{stock['current_price']:.2f}\n\n"

    if 'ai_insights' in results and 'market_overview' in results['ai_insights']:
        body += "\nMarket Overview:\n"
        body += results['ai_insights']['market_overview']

    msg.attach(MIMEText(body, 'plain'))

    # Send email (configure your SMTP settings)
    # smtp_server.send_message(msg)

    print("Email report prepared!")
```

## Tips and Best Practices

### 1. Data Quality
- Use `--no-cache` periodically for fresh data
- Check `data_completeness` scores in output
- Filter with `min_data_quality` for reliable results

### 2. Performance
- Use caching for faster repeated analyses
- Analyze specific sectors rather than all stocks
- Use parallel processing (built-in)

### 3. Investment Strategy
- Combine multiple strategies (value + quality)
- Use sentiment as a tiebreaker, not primary factor
- Cross-reference with other analysis tools

### 4. API Usage
- Respect rate limits
- Cache results when appropriate
- Use appropriate delays between requests

### 5. Interpreting Scores
- Overall score > 70: Strong candidate
- Overall score 60-70: Good candidate
- Overall score 50-60: Moderate candidate
- Overall score < 50: Weak candidate

Remember: This tool is for analysis only. Always do your own research and consult with financial advisors before making investment decisions.
