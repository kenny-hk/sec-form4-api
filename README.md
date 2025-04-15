# S&P 500 Insider Trading API

A free, public API for S&P 500 insider trading data from SEC Form 4 filings, hosted on GitHub Pages.

## Overview

This project automatically collects Form 4 filings (insider trading reports) from the SEC EDGAR database for all S&P 500 companies. It processes and provides this data through a simple, free API accessible to anyone. The data includes:

- Issuer name and ticker
- Reporting owner and position
- Transaction date, shares, and price
- Transaction type
- Post-transaction holdings

## Data Retention

To optimize storage and performance while maintaining comprehensive historical data:

- **Detailed Transactions:** Full transaction details for the most recent 3 years
- **Quarterly Summaries:** Quarterly transaction data for the past 10 years
- **Daily Updates:** All data refreshed daily with the latest SEC filings

## Features

- **Daily Updates**: New Form 4 filings are downloaded and processed daily
- **JSON API**: Clean, structured data in JSON format
- **Free & Public**: No authentication or API keys required
- **Multiple Endpoints**: Access data by company, recent transactions, or largest trades
- **GitHub Pages Hosting**: Fast, reliable static file hosting

## API Endpoints

- **All Companies**: `/data/json/companies.json`
- **Company Transactions**: `/data/json/{ticker}/transactions.json`
- **Quarterly Data**: `/data/json/{ticker}/quarterly/{YYYY-Q#}.json`
- **Summary Data**: `/data/json/summary.json`

See the [API Documentation](https://kenny-hk.github.io/insider-trading-detection/) for complete details and examples.

## Usage Examples

### JavaScript
```javascript
// Fetch all companies
fetch('https://kenny-hk.github.io/insider-trading-detection/data/json/companies.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} companies with insider trading data`);
  });

// Get Apple transactions and filter for sales
fetch('https://kenny-hk.github.io/insider-trading-detection/data/json/AAPL/transactions.json')
  .then(response => response.json())
  .then(data => {
    const sales = data.transactions.filter(tx => tx.transaction_type === 'S');
    console.log(`Found ${sales.length} sale transactions by Apple insiders`);
  });
```

### Python
```python
import requests
import pandas as pd

# Get all large transactions from summary
response = requests.get('https://kenny-hk.github.io/insider-trading-detection/data/json/summary.json')
data = response.json()

# Convert to DataFrame for easy analysis
large_txs = pd.DataFrame(data['large_transactions'])
print(f"Largest transaction: {large_txs.iloc[0]['ticker']} ${large_txs.iloc[0]['value']:,.2f}")
```

## How It Works

1. **Data Collection**: GitHub Actions runs daily to download new Form 4 filings
2. **Processing**: Python scripts parse XML files and store data in SQLite
3. **API Generation**: Data is exported from SQLite to structured JSON files
4. **Hosting**: JSON files are committed to the repository and served via GitHub Pages

## Local Development

### Requirements

- Python 3.6+
- pandas
- sec-edgar-downloader
- sqlite3

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/insider-trading-detection.git
cd insider-trading-detection
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

### Usage

Run the data collection script:

```bash
python InsiderTrading.py [--no-download] [--limit NUM_COMPANIES]
```

Generate the JSON API files:

```bash
python export_json.py
```

## Testing

This project uses pytest for testing. The test suite includes:

- Unit tests for data collection functionality
- Unit tests for JSON export functionality
- Structure tests for GitHub Actions workflows

To run the tests:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=.

# Run specific test file
pytest tests/test_export_json.py
```

The test suite ensures:
- Proper handling of different transaction types
- Correct formatting of JSON data
- Error resilience with bad or missing data
- Validation of workflow configurations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Before submitting a pull request, please:
1. Add tests for any new features or bug fixes
2. Run the existing test suite to ensure everything passes
3. Ensure your code follows the project's coding style

## License

[MIT License](LICENSE)

## Disclaimer

This data is sourced directly from SEC EDGAR filings and is provided for informational purposes only. It is not financial advice.
