# 🚀 Quick Start Guide

Get started with the Indian Stock Research Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including:
- yfinance (stock data)
- pandas, numpy (data processing)
- beautifulsoup4 (web scraping)
- vaderSentiment (sentiment analysis)
- rich (beautiful CLI output)
- google-generativeai (Gemini AI - optional)

## Step 2: Set Up Gemini API Key (Optional but Recommended)

Get a free API key from: https://makersuite.google.com/app/apikey

```bash
export GEMINI_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your key
```

## Step 3: Run Your First Analysis

### Option A: Simple Quick Start
```bash
python main.py
```

This analyzes 40+ popular Indian stocks and shows the top 10 recommendations.

### Option B: Full CLI
```bash
# Full analysis with all features
python cli.py analyze

# Analyze specific stocks
python cli.py analyze --stocks "TCS.NS,INFY.NS,RELIANCE.NS"

# Get detailed analysis of a single stock
python cli.py specific --symbols "HDFCBANK.NS"
```

### Option C: Run Examples
```bash
python example.py
```

This demonstrates 5 different use cases with real examples.

## Step 4: Check the Results

Results are saved in the `output/` directory:
- `stock_analysis_full_*.csv` - Complete analysis
- `top_recommendations_*.csv` - Top picks
- `analysis_results_*.json` - Full results with AI insights

## Example Output

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

## Interactive Mode (with Gemini API)

```bash
python cli.py interactive

You: Which IT stocks look undervalued?
Agent: Based on current analysis, TCS and Infosys show attractive valuations...

You: What are the risks with Reliance?
Agent: Reliance has high debt levels, but strong cash flow...
```

## Common Use Cases

### Analyze a Specific Sector
```bash
# IT Sector
python cli.py analyze --stocks "TCS.NS,INFY.NS,WIPRO.NS,HCLTECH.NS,TECHM.NS"

# Banking Sector
python cli.py analyze --stocks "HDFCBANK.NS,ICICIBANK.NS,KOTAKBANK.NS,AXISBANK.NS"
```

### Compare Two Stocks
```bash
python cli.py specific --symbols "HDFCBANK.NS,ICICIBANK.NS"
```

### Get Top 20 Recommendations
```bash
python cli.py analyze --top-n 20
```

### Fresh Data (No Cache)
```bash
python cli.py analyze --no-cache
```

## Need Help?

- **Documentation**: See `README.md` for full documentation
- **Usage Examples**: See `USAGE.md` for detailed examples
- **Test Installation**: Run `python test_installation.py`
- **Issues**: Check troubleshooting section in README.md

## Understanding the Metrics

### Key Scores (0-100, higher is better)
- **Overall Score**: Combined score across all factors
- **Value Score**: Based on P/E, P/B ratios
- **Growth Score**: Based on EPS and revenue growth
- **Quality Score**: Based on ROE and profit margins
- **Safety Score**: Based on debt levels and volatility

### Investment Recommendations
- **70+**: Strong Buy - Excellent fundamentals
- **60-70**: Buy - Good fundamentals
- **50-60**: Hold - Mixed signals
- **40-50**: Neutral - Several concerns
- **<40**: Avoid - Weak fundamentals

## What's Next?

1. **Customize**: Modify `stock_agent/config.py` for your preferences
2. **Schedule**: Set up daily analysis with cron jobs
3. **Integrate**: Use the Python API in your own scripts
4. **Explore**: Try different investment strategies (value, growth, quality)

## ⚠️ Important Disclaimer

This tool is for **educational and research purposes only**. It is **NOT financial advice**. Always:
- Do your own research
- Consult qualified financial advisors
- Understand that past performance ≠ future results
- Consider your risk tolerance and investment goals

---

**Happy Investing! 📈**
