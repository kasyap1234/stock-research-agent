# 🇮🇳 Indian Stock Research Agent

An AI-powered Python agent for comprehensive analysis of Indian stocks (NSE/BSE). Automatically fetches stock data, calculates financial metrics, performs sentiment analysis, and recommends the best stocks based on quantitative analysis.

## ✨ Features

- **📊 Comprehensive Data Fetching**: Automatically fetches stock data from Yahoo Finance for NSE/BSE stocks
- **💹 Financial Metrics Calculation**: Calculates 30+ key financial ratios including:
  - P/E Ratio, P/B Ratio, ROE, ROA
  - Debt-to-Equity, Current Ratio, Quick Ratio
  - EPS Growth, Revenue Growth
  - Dividend Yield, PEG Ratio
  - Graham Number (Intrinsic Value)
- **🎯 Multi-Factor Scoring System**:
  - Value Score (P/E, P/B, Debt/Equity)
  - Growth Score (EPS & Revenue Growth)
  - Quality Score (ROE, Profit Margins)
  - Safety Score (Debt levels, Volatility)
- **📰 Sentiment Analysis**: Scrapes and analyzes stock news for market sentiment
- **🤖 AI-Powered Insights**: Uses Google Gemini API for intelligent market analysis and recommendations
- **📈 Multiple Investment Strategies**: Recommendations for value, growth, quality, and safety investors
- **💻 Interactive CLI**: Beautiful command-line interface with rich formatting
- **📁 Multiple Output Formats**: CSV, JSON reports with detailed analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (optional, for AI features)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd stock-research-agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Gemini API key** (optional but recommended):
```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
```

Get your free API key from: https://makersuite.google.com/app/apikey

### Running the Agent

#### Method 1: Simple Quick Start
```bash
python main.py
```

This will run a complete analysis with default settings and display the top 10 recommended stocks.

#### Method 2: Full CLI with Options
```bash
# Full analysis with all features
python cli.py analyze

# Analyze specific stocks
python cli.py analyze --stocks "TCS.NS,INFY.NS,RELIANCE.NS,HDFCBANK.NS"

# Get top 20 recommendations
python cli.py analyze --top-n 20

# Disable cache for fresh data
python cli.py analyze --no-cache

# Analyze specific stock in detail
python cli.py specific --symbols "RELIANCE.NS"

# Interactive Q&A mode (requires Gemini API key)
python cli.py interactive

# With custom API key
python cli.py analyze --gemini-api-key "your-key"
```

## 📋 Output

The agent generates multiple output files in the `output/` directory:

1. **stock_analysis_full_[timestamp].csv**: Complete analysis of all stocks
2. **top_recommendations_[timestamp].csv**: Top N recommended stocks
3. **analysis_results_[timestamp].json**: Full results including AI insights

### Sample Output
```
🏆 TOP 10 RECOMMENDED STOCKS:

Rank   Symbol         Name                           Score
----------------------------------------------------------------------
1      TCS.NS         Tata Consultancy Services      78.45
2      HDFCBANK.NS    HDFC Bank Limited              76.32
3      INFY.NS        Infosys Limited                74.89
4      RELIANCE.NS    Reliance Industries Limited    73.21
5      ICICIBANK.NS   ICICI Bank Limited             71.56
...
```

## 🏗️ Architecture

```
stock-research-agent/
├── stock_agent/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── agent.py               # Main orchestrator with Gemini AI
│   └── modules/
│       ├── __init__.py
│       ├── data_fetcher.py    # Fetches stock data via yfinance
│       ├── metrics_calculator.py  # Calculates financial ratios
│       ├── stock_ranker.py    # Ranks and scores stocks
│       └── sentiment_analyzer.py  # News & sentiment analysis
├── cli.py                     # Command-line interface
├── main.py                    # Simple entry point
├── requirements.txt           # Python dependencies
├── output/                    # Generated reports
└── README.md
```

## 🔧 Configuration

You can customize the agent behavior by modifying `stock_agent/config.py` or creating a custom configuration:

```python
from stock_agent.config import AgentConfig
from stock_agent.agent import StockResearchAgent

# Custom configuration
config = AgentConfig(
    nse_stocks=["TCS.NS", "INFY.NS", "RELIANCE.NS"],  # Your stock list
    top_n_recommendations=15,
    min_market_cap=5000,  # Minimum market cap in crores
    enable_sentiment=True,
    output_csv=True,
    output_json=True
)

# Initialize agent with custom config
agent = StockResearchAgent(config=config, gemini_api_key="your-key")
results = agent.run_full_analysis()
```

### Key Configuration Options

- **nse_stocks**: List of NSE stock symbols to analyze
- **bse_stocks**: List of BSE stock symbols
- **top_n_recommendations**: Number of top stocks to recommend (default: 10)
- **min_market_cap**: Minimum market cap filter in crores (default: 1000)
- **min_data_quality**: Minimum data completeness ratio (default: 0.5)
- **enable_sentiment**: Enable news sentiment analysis (default: True)
- **scoring_weights**: Customize weights for value/growth/quality/safety scores

## 📊 Metrics Explained

### Value Metrics
- **P/E Ratio**: Price-to-Earnings ratio (lower is better for value)
- **P/B Ratio**: Price-to-Book ratio (lower indicates undervaluation)
- **Graham Number**: Intrinsic value estimate using Benjamin Graham's formula

### Growth Metrics
- **EPS Growth**: Earnings per share growth rate
- **Revenue Growth**: Year-over-year revenue growth
- **PEG Ratio**: P/E to Growth ratio (< 1 is attractive)

### Quality Metrics
- **ROE**: Return on Equity (higher is better, > 15% is good)
- **ROA**: Return on Assets
- **Profit Margin**: Net profit as % of revenue

### Safety Metrics
- **Debt-to-Equity**: Total debt divided by shareholder equity (< 1 is safer)
- **Current Ratio**: Current assets / current liabilities (> 1.5 is healthy)
- **Volatility**: Price volatility (lower is more stable)

### Overall Score
Weighted combination of:
- Value Score (30%)
- Growth Score (30%)
- Quality Score (25%)
- Safety Score (15%)

## 🤖 AI Features (Gemini Integration)

When a Gemini API key is provided, the agent can:

1. **Market Overview**: AI-generated summary of market trends
2. **Top Pick Analysis**: Detailed AI analysis of the top recommended stock
3. **Sector Analysis**: Insights on promising sectors
4. **Interactive Q&A**: Ask questions about stocks and get AI-powered answers

```bash
# Interactive mode
python cli.py interactive

You: Which IT stocks look undervalued right now?
Agent: Based on the current analysis, TCS and Infosys show attractive valuations...

You: What are the risks with high debt stocks?
Agent: High debt stocks carry several risks...
```

## 📈 Investment Strategies

The agent provides recommendations for different investment styles:

### Value Investing
Focuses on stocks with low P/E, low P/B ratios, and strong fundamentals
```bash
# Get value picks from the full analysis
python cli.py analyze
# Check the "Top Value Picks" section
```

### Growth Investing
Focuses on stocks with high EPS growth and revenue growth
```bash
# Growth stocks are highlighted in strategy-specific recommendations
```

### Quality Investing
Focuses on stocks with high ROE, strong profit margins, and low debt
```bash
# Quality stocks shown in the analysis
```

### Safety/Defensive
Focuses on stable stocks with low debt and low volatility
```bash
# Safety picks for conservative investors
```

## ⚠️ Important Notes

### Legal & Ethical
- This tool is for **educational and research purposes only**
- **Not financial advice** - always do your own research
- Use yfinance and public APIs (no unauthorized scraping)
- Check Yahoo Finance terms of service

### Data Quality
- Data is fetched from Yahoo Finance via yfinance library
- Some stocks may have incomplete data
- The agent filters stocks based on data quality thresholds
- Cache is used to reduce API calls (24-hour default)

### Limitations
- Past performance doesn't guarantee future results
- Fundamental analysis is just one aspect of stock evaluation
- Market sentiment and macroeconomic factors not fully captured
- News sentiment is based on headlines only

## 🔬 Testing

To test the system:

```bash
# Test with a small set of stocks
python cli.py analyze --stocks "TCS.NS,INFY.NS,RELIANCE.NS"

# Test specific stock analysis
python cli.py specific --symbols "HDFCBANK.NS"

# Test without cache (fresh data)
python cli.py analyze --no-cache
```

## 🛠️ Troubleshooting

### "No stock data fetched"
- Check your internet connection
- Verify stock symbols are correct (use .NS for NSE, .BO for BSE)
- Try with --no-cache flag

### "Gemini API error"
- Verify your API key is correct
- Check you have API quota available
- Ensure GEMINI_API_KEY environment variable is set

### "Module not found"
- Run `pip install -r requirements.txt` again
- Ensure you're using Python 3.8+

### Rate Limiting
- The agent includes delays between API calls
- If you hit rate limits, increase `request_delay_seconds` in config

## 📚 Dependencies

### Core Libraries
- **yfinance**: Stock data fetching
- **pandas**: Data manipulation
- **numpy**: Numerical calculations
- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing

### AI & NLP
- **google-generativeai**: Gemini API integration
- **vaderSentiment**: Sentiment analysis
- **langchain**: Optional advanced agent features

### CLI & Visualization
- **rich**: Beautiful terminal output
- **tabulate**: Table formatting
- **streamlit**: Optional web dashboard (future)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add more data sources
- Implement technical analysis indicators
- Create web dashboard
- Add backtesting capabilities
- Support for international markets

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- Yahoo Finance for data (via yfinance)
- Google Gemini for AI capabilities
- VADER Sentiment for sentiment analysis

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the code documentation

---

**⚠️ Disclaimer**: This software is for educational purposes only. Always consult with a qualified financial advisor before making investment decisions. The creators are not responsible for any financial losses incurred through the use of this tool.
