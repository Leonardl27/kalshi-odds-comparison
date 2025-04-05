# Kalshi Odds Comparison

A tool to compare soccer odds between sportsbooks and Kalshi exchange markets to identify potential value betting opportunities.

## Overview

This project automatically:
1. Collects odds data from major sportsbooks for soccer matches
2. Retrieves corresponding markets from Kalshi
3. Compares implied probabilities to identify discrepancies
4. Reports potential value opportunities

## Setup

### Prerequisites
- Python 3.9+
- API access tokens (config.yaml)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kalshi-odds-comparison.git
cd kalshi-odds-comparison

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config.yaml.example config.yaml
# Edit config.yaml with your API keys
```

## Usage

```bash
# Run the main application
python -m src.main

# Run with specific configuration
python -m src.main --config custom_config.yaml
```

## Testing

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_sportsbook.py
```

## Development

This project follows a modular architecture:
- `data_collection`: Modules for fetching data from external sources
- `analysis`: Tools for converting and comparing odds
- `utils`: Helper functions and utilities

## License

MIT