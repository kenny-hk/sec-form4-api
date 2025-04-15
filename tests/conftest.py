"""
Common fixtures for tests.
"""
import os
import pytest
import sqlite3
import pandas as pd
from datetime import datetime

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary test database."""
    db_path = os.path.join(tmp_path, 'test_insider_trading.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test table
    cursor.execute('''
    CREATE TABLE insider_trading (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issuer_name TEXT,
        issuer_ticker TEXT,
        reporting_owner TEXT,
        reporting_owner_cik TEXT,
        reporting_owner_position TEXT,
        transaction_date TEXT,
        transaction_shares TEXT,
        transaction_price TEXT,
        transaction_type TEXT,
        shares_after_transaction TEXT,
        source_file TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert test data for multiple companies
    test_data = [
        # AAPL data - different transaction types and dates
        ('Apple Inc.', 'AAPL', 'Cook, Tim', '0001111111', 'CEO', '2025-01-15', '10000', '180.25', 'S', '500000', 'test_file.xml', datetime.now()),
        ('Apple Inc.', 'AAPL', 'Cook, Tim', '0001111111', 'CEO', '2024-11-10', '5000', '175.50', 'P', '490000', 'test_file.xml', datetime.now()),
        ('Apple Inc.', 'AAPL', 'Maestri, Luca', '0002222222', 'CFO', '2025-02-20', '8000', '185.00', 'S', '200000', 'test_file.xml', datetime.now()),
        ('Apple Inc.', 'AAPL', 'Maestri, Luca', '0002222222', 'CFO', '2024-12-05', '3000', '0', 'A', '192000', 'test_file.xml', datetime.now()),
        ('Apple Inc.', 'AAPL', 'Williams, Jeff', '0003333333', 'COO', '2025-03-10', '7500', '190.75', 'S', '150000', 'test_file.xml', datetime.now()),
        
        # MSFT data
        ('Microsoft Corp', 'MSFT', 'Nadella, Satya', '0004444444', 'CEO', '2025-01-20', '15000', '380.50', 'S', '800000', 'test_file.xml', datetime.now()),
        ('Microsoft Corp', 'MSFT', 'Nadella, Satya', '0004444444', 'CEO', '2024-12-15', '10000', '0', 'A', '785000', 'test_file.xml', datetime.now()),
        ('Microsoft Corp', 'MSFT', 'Hood, Amy', '0005555555', 'CFO', '2025-02-10', '5000', '390.25', 'S', '150000', 'test_file.xml', datetime.now()),
        
        # GOOGL data
        ('Alphabet Inc.', 'GOOGL', 'Pichai, Sundar', '0006666666', 'CEO', '2025-01-05', '8000', '150.50', 'S', '300000', 'test_file.xml', datetime.now()),
        ('Alphabet Inc.', 'GOOGL', 'Porat, Ruth', '0007777777', 'CFO', '2024-11-25', '4000', '145.75', 'S', '120000', 'test_file.xml', datetime.now()),
    ]
    
    cursor.executemany('''
    INSERT INTO insider_trading 
    (issuer_name, issuer_ticker, reporting_owner, reporting_owner_cik, 
     reporting_owner_position, transaction_date, transaction_shares, 
     transaction_price, transaction_type, shares_after_transaction, source_file, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_data)
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_issuer_ticker ON insider_trading (issuer_ticker)')
    cursor.execute('CREATE INDEX idx_transaction_date ON insider_trading (transaction_date)')
    
    conn.commit()
    conn.close()
    
    return db_path

@pytest.fixture
def test_json_dir(tmp_path):
    """Create a temporary directory for JSON output."""
    json_dir = os.path.join(tmp_path, 'json')
    os.makedirs(json_dir, exist_ok=True)
    return json_dir