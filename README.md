# S&P 500 Insider Trading API

A free, public API for S&P 500 insider trading data from SEC Form 4 filings, hosted on GitHub Pages.

## Overview

This project automatically collects Form 4 filings (insider trading reports) from the SEC EDGAR database for S&P 500 companies. It processes and provides this data through a simple, free API accessible to anyone. The data includes:

- Issuer name and ticker
- Reporting owner and position
- Transaction date, shares, and price
- Transaction type
- Post-transaction holdings

## Features

- **Daily Updates**: New Form 4 filings are downloaded and processed daily
- **JSON API**: Clean, structured data in JSON format
- **Free & Public**: No authentication or API keys required
- **Multiple Endpoints**: Access data by company, recent transactions, or largest trades
- **GitHub Pages Hosting**: Fast, reliable static file hosting

## API Endpoints

- **All Companies**: `/data/json/companies.json`
- **Company Transactions**: `/data/json/{ticker}/latest.json`
- **Summary Data**: `/data/json/summary.json`

See the [API Documentation](https://yourusername.github.io/insider-trading-detection/) for complete details and examples.

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Disclaimer

This data is sourced directly from SEC EDGAR filings and is provided for informational purposes only. It is not financial advice.
