import os
import sqlite3
import json
import pandas as pd
from datetime import datetime
import argparse

# Use relative path for data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'insider_trading.db')
JSON_DIR = os.path.join(DATA_DIR, 'json')

def initialize_json_directory():
    """Create JSON directory structure if it doesn't exist."""
    os.makedirs(JSON_DIR, exist_ok=True)
    
    # Create company directories 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT issuer_ticker FROM insider_trading")
    tickers = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    
    for ticker in tickers:
        os.makedirs(os.path.join(JSON_DIR, ticker), exist_ok=True)
    
    print(f"Initialized JSON directory structure for {len(tickers)} companies")

def export_companies_index():
    """Export list of all companies with metadata to companies.json."""
    conn = sqlite3.connect(DB_PATH)
    
    # Get company data
    company_data = pd.read_sql_query("""
        SELECT 
            issuer_ticker as ticker,
            issuer_name as name,
            COUNT(*) as transaction_count,
            MAX(transaction_date) as latest_transaction,
            MIN(transaction_date) as earliest_transaction
        FROM 
            insider_trading
        WHERE 
            issuer_ticker IS NOT NULL
        GROUP BY 
            issuer_ticker, issuer_name
        ORDER BY 
            transaction_count DESC
    """, conn)
    
    # Convert to list of dictionaries for JSON
    companies = company_data.to_dict(orient='records')
    
    # Write to JSON file
    with open(os.path.join(JSON_DIR, 'companies.json'), 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'count': len(companies),
            'companies': companies
        }, f, indent=2)
    
    conn.close()
    print(f"Exported data for {len(companies)} companies to companies.json")

def export_company_transactions(limit=1000):
    """Export comprehensive transaction data for each company."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tickers
    cursor.execute("SELECT DISTINCT issuer_ticker FROM insider_trading WHERE issuer_ticker IS NOT NULL")
    tickers = [row[0] for row in cursor.fetchall()]
    
    for ticker in tickers:
        # Get all trades with complete data
        trades = pd.read_sql_query(f"""
            SELECT 
                id,
                issuer_name,
                reporting_owner,
                reporting_owner_cik,
                reporting_owner_position,
                transaction_date,
                transaction_shares,
                transaction_price,
                transaction_type,
                shares_after_transaction
            FROM 
                insider_trading
            WHERE 
                issuer_ticker = ?
            ORDER BY 
                transaction_date DESC
            LIMIT {limit}
        """, conn, params=[ticker])
        
        # Convert to list of dictionaries for JSON
        trades_list = trades.to_dict(orient='records')
        
        # Write to JSON file with complete data
        with open(os.path.join(JSON_DIR, ticker, 'transactions.json'), 'w') as f:
            json.dump({
                'ticker': ticker,
                'last_updated': datetime.now().isoformat(),
                'count': len(trades_list),
                'transactions': trades_list
            }, f, indent=2)
            
        # Also create quarterly files for this ticker if we have enough data
        if len(trades) > 0:
            # Add quarter information for grouping
            trades['year'] = pd.to_datetime(trades['transaction_date']).dt.year
            trades['quarter'] = pd.to_datetime(trades['transaction_date']).dt.quarter
            
            # Group by year and quarter
            for (year, quarter), group in trades.groupby(['year', 'quarter']):
                quarterly_dir = os.path.join(JSON_DIR, ticker, 'quarterly')
                os.makedirs(quarterly_dir, exist_ok=True)
                
                quarter_file = f"{year}-Q{quarter}.json"
                group_list = group.drop(['year', 'quarter'], axis=1).to_dict(orient='records')
                
                with open(os.path.join(quarterly_dir, quarter_file), 'w') as f:
                    json.dump({
                        'ticker': ticker,
                        'year': int(year),
                        'quarter': int(quarter),
                        'last_updated': datetime.now().isoformat(),
                        'count': len(group_list),
                        'transactions': group_list
                    }, f, indent=2)
    
    conn.close()
    print(f"Exported comprehensive transaction data for {len(tickers)} companies")

def export_summary_data():
    """Export summary with notable transactions across companies."""
    conn = sqlite3.connect(DB_PATH)
    
    # Get large transactions
    large_transactions = pd.read_sql_query("""
        SELECT 
            issuer_ticker as ticker,
            issuer_name as company,
            reporting_owner as insider,
            reporting_owner_position as position,
            transaction_date as date,
            transaction_shares as shares,
            transaction_price as price,
            transaction_type as type,
            (CAST(transaction_shares AS REAL) * CAST(transaction_price AS REAL)) as value
        FROM 
            insider_trading
        WHERE 
            transaction_shares IS NOT NULL 
            AND transaction_price IS NOT NULL
            AND CAST(transaction_shares AS REAL) > 0
        ORDER BY 
            value DESC
        LIMIT 100
    """, conn)
    
    # Get recent transactions
    recent_transactions = pd.read_sql_query("""
        SELECT 
            issuer_ticker as ticker,
            issuer_name as company,
            reporting_owner as insider,
            reporting_owner_position as position,
            transaction_date as date,
            transaction_shares as shares,
            transaction_price as price,
            transaction_type as type,
            (CAST(transaction_shares AS REAL) * CAST(transaction_price AS REAL)) as value
        FROM 
            insider_trading
        ORDER BY 
            transaction_date DESC
        LIMIT 50
    """, conn)
    
    # Write to JSON file
    with open(os.path.join(JSON_DIR, 'summary.json'), 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'large_transactions': large_transactions.to_dict(orient='records'),
            'recent_transactions': recent_transactions.to_dict(orient='records')
        }, f, indent=2)
    
    conn.close()
    print("Exported summary data")

def main():
    """Main function to export SQLite data to JSON files."""
    parser = argparse.ArgumentParser(description='Export insider trading data from SQLite to JSON.')
    args = parser.parse_args()
    
    # Check if SQLite database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: SQLite database not found at {DB_PATH}")
        return
    
    # Initialize JSON directory structure
    initialize_json_directory()
    
    # Export data
    export_companies_index()
    export_company_transactions()
    export_summary_data()
    
    print("JSON export completed successfully")

if __name__ == "__main__":
    main()