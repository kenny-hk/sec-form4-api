# Insider Trading Detection

A Python tool for downloading, analyzing, and detecting patterns in Form 4 filings from the SEC EDGAR database.

## Overview

This project downloads Form 4 filings (insider trading reports) from the SEC EDGAR database for specified companies and time periods. It extracts key information from these filings, such as:

- Issuer name and ticker
- Reporting owner
- Transaction date
- Transaction shares
- Transaction price
- Transaction type

This data can be used to analyze insider trading patterns and potentially identify suspicious activity.

## Features

- Download Form 4 filings for multiple companies
- Specify date ranges for data collection
- Extract and structure insider trading data
- Save data for further analysis

## Requirements

- Python 3.6+
- pandas
- sec-edgar-downloader

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/insider-trading-detection.git
cd insider-trading-detection
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python InsiderTrading.py
```

By default, the script will:
1. Download Form 4 filings for AAPL, MSFT, AMZN, GOOGL, and META from the past 6 months
2. Extract insider trading information from these filings
3. Save the data to a CSV file in the data directory

## Customization

You can modify the script to:
- Change the companies being tracked
- Adjust the date range
- Modify the data extraction process

## Future Improvements

- Implement SQLite database for more efficient data storage and querying
- Add visualization tools for insider trading patterns
- Expand to cover all Fortune 500 companies
- Implement anomaly detection algorithms

## License

[MIT License](LICENSE)
