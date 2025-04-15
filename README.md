# SEC Form4 API

A free, public API providing access to SEC Form 4 filings (insider transactions) for all S&P 500 companies, hosted on GitHub Pages.

## Overview

This project automatically collects Form 4 filings from the SEC EDGAR database for all S&P 500 companies. These filings report transactions by company insiders (officers, directors, and significant shareholders) as required by law. The data is processed and provided through a simple, free API accessible to anyone.

## Data Coverage

- **All S&P 500 Companies**: Complete coverage of all companies in the S&P 500 index
- **Detailed Transactions**: Full transaction details for the most recent 3 years
- **Quarterly Summaries**: Quarterly transaction data for the past 10 years
- **Daily Updates**: All data refreshed daily with the latest SEC filings

## API Endpoints

- **All Companies**: `/data/json/companies.json`
- **Company Transactions**: `/data/json/{ticker}/transactions.json`
- **Quarterly Data**: `/data/json/{ticker}/quarterly/{YYYY-Q#}.json`
- **Summary Data**: `/data/json/summary.json`

See the [API Documentation](https://kenny-hk.github.io/sec-form4-api/) for complete details and examples.

## Usage Examples

### JavaScript
```javascript
// Fetch all companies
fetch('https://kenny-hk.github.io/sec-form4-api/data/json/companies.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} companies with Form 4 filing data`);
  });

// Get Apple transactions and filter for sales
fetch('https://kenny-hk.github.io/sec-form4-api/data/json/AAPL/transactions.json')
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
response = requests.get('https://kenny-hk.github.io/sec-form4-api/data/json/summary.json')
data = response.json()

# Convert to DataFrame for easy analysis
large_txs = pd.DataFrame(data['large_transactions'])
print(f"Largest transaction: {large_txs.iloc[0]['ticker']} ${large_txs.iloc[0]['value']:,.2f}")
```

## Data Fields

Each transaction includes:
- **Issuer**: Company name and ticker symbol
- **Reporting Owner**: Name, CIK, and title/position
- **Transaction**: Date, number of shares, price per share, type code
- **Holdings**: Shares owned following transaction
- **Metadata**: Filing details and source information

## Transaction Types

Common transaction type codes include:
- **P**: Purchase of securities on the open market
- **S**: Sale of securities on the open market
- **A**: Grant/award of securities from the company
- **M**: Exercise of options/conversion of derivative securities
- **G**: Gift of securities
- **D**: Disposition of securities to the issuer

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
git clone https://github.com/kenny-hk/sec-form4-api.git
cd sec-form4-api
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

This project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=.
```

## License

[MIT License](LICENSE)

## Disclaimer

This data is sourced directly from SEC EDGAR filings and is provided for informational purposes only. It is not financial advice. All Form 4 data is publicly available through the SEC's EDGAR system.