"""
Setup script for Indian Stock Research Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="indian-stock-research-agent",
    version="1.0.0",
    author="Stock Research Agent",
    description="AI-powered Python agent for comprehensive Indian stock analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock-research-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "stock-agent=cli:main",
        ],
    },
    include_package_data=True,
    keywords="stock analysis india nse bse financial metrics ai agent",
    project_urls={
        "Documentation": "https://github.com/yourusername/stock-research-agent/blob/main/README.md",
        "Source": "https://github.com/yourusername/stock-research-agent",
        "Tracker": "https://github.com/yourusername/stock-research-agent/issues",
    },
)
