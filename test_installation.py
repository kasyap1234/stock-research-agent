#!/usr/bin/env python3
"""
Test script to verify the Stock Research Agent installation
"""

import sys
import os
from pathlib import Path


def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")

    required_files = [
        'requirements.txt',
        'README.md',
        'USAGE.md',
        'setup.py',
        'main.py',
        'cli.py',
        'example.py',
        '.gitignore',
        '.env.example',
        'stock_agent/__init__.py',
        'stock_agent/config.py',
        'stock_agent/agent.py',
        'stock_agent/modules/__init__.py',
        'stock_agent/modules/data_fetcher.py',
        'stock_agent/modules/metrics_calculator.py',
        'stock_agent/modules/stock_ranker.py',
        'stock_agent/modules/sentiment_analyzer.py',
    ]

    missing_files = []
    for file_path in required_files:
        full_path = Path(file_path)
        if not full_path.exists():
            missing_files.append(file_path)
            print(f"  ✗ Missing: {file_path}")
        else:
            print(f"  ✓ Found: {file_path}")

    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} files")
        return False
    else:
        print("\n✅ All files present")
        return True


def test_python_syntax():
    """Test Python syntax of all files"""
    print("\nTesting Python syntax...")

    python_files = [
        'main.py',
        'cli.py',
        'example.py',
        'setup.py',
        'stock_agent/__init__.py',
        'stock_agent/config.py',
        'stock_agent/agent.py',
        'stock_agent/modules/__init__.py',
        'stock_agent/modules/data_fetcher.py',
        'stock_agent/modules/metrics_calculator.py',
        'stock_agent/modules/stock_ranker.py',
        'stock_agent/modules/sentiment_analyzer.py',
    ]

    errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"  ✓ {file_path}")
        except SyntaxError as e:
            errors.append((file_path, str(e)))
            print(f"  ✗ {file_path}: {e}")

    if errors:
        print(f"\n❌ Syntax errors in {len(errors)} files")
        return False
    else:
        print("\n✅ No syntax errors")
        return True


def check_dependencies():
    """Check if dependencies are installed"""
    print("\nChecking dependencies...")

    required_packages = [
        'yfinance',
        'pandas',
        'numpy',
        'requests',
        'beautifulsoup4',
        'vaderSentiment',
        'rich',
        'pydantic',
    ]

    optional_packages = [
        'google.generativeai',
        'langchain',
        'streamlit',
    ]

    missing_required = []
    missing_optional = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"  ✗ {package} (REQUIRED)")

    for package in optional_packages:
        try:
            __import__(package.replace('-', '_').replace('.', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            missing_optional.append(package)
            print(f"  ⚠ {package} (OPTIONAL)")

    if missing_required:
        print(f"\n⚠️  Missing {len(missing_required)} required packages")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages installed")
        if missing_optional:
            print(f"⚠️  {len(missing_optional)} optional packages not installed")
        return True


def test_imports():
    """Test that modules can be imported"""
    print("\nTesting imports...")

    try:
        # Add to path
        sys.path.insert(0, str(Path(__file__).parent))

        print("  Testing config module...")
        from stock_agent.config import AgentConfig
        print("  ✓ Config module OK")

        print("  Testing data fetcher module...")
        from stock_agent.modules.data_fetcher import StockDataFetcher
        print("  ✓ Data fetcher module OK")

        print("  Testing metrics calculator module...")
        from stock_agent.modules.metrics_calculator import MetricsCalculator
        print("  ✓ Metrics calculator module OK")

        print("  Testing stock ranker module...")
        from stock_agent.modules.stock_ranker import StockRanker
        print("  ✓ Stock ranker module OK")

        print("  Testing sentiment analyzer module...")
        from stock_agent.modules.sentiment_analyzer import SentimentAnalyzer
        print("  ✓ Sentiment analyzer module OK")

        print("  Testing main agent module...")
        from stock_agent.agent import StockResearchAgent
        print("  ✓ Main agent module OK")

        print("\n✅ All imports successful")
        return True

    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("INDIAN STOCK RESEARCH AGENT - INSTALLATION TEST")
    print("="*70)
    print()

    # Change to project directory
    os.chdir(Path(__file__).parent)

    # Run tests
    results = []

    results.append(("File Structure", test_file_structure()))
    results.append(("Python Syntax", test_python_syntax()))
    results.append(("Dependencies", check_dependencies()))

    # Only test imports if dependencies are installed
    if results[-1][1]:
        results.append(("Module Imports", test_imports()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n🎉 All tests passed! The agent is ready to use.")
        print("\nNext steps:")
        print("  1. Set up your Gemini API key:")
        print("     export GEMINI_API_KEY='your-key-here'")
        print("  2. Run the agent:")
        print("     python main.py")
        print("     or")
        print("     python cli.py analyze")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        if not results[2][1]:  # Dependencies failed
            print("\nTo install dependencies:")
            print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
