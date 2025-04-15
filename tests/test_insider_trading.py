"""
Tests for the InsiderTrading.py script.
"""
import os
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import xml.etree.ElementTree as ET
from io import StringIO

# Add the parent directory to the path so we can import from the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import InsiderTrading

class TestInsiderTrading:
    
    def test_get_sp500_companies(self, monkeypatch):
        """Test that get_sp500_companies fetches and returns the correct data."""
        # Mock data
        mock_csv = StringIO("Symbol,Name,Sector\nAAPL,Apple Inc.,Technology\nMSFT,Microsoft Corp,Technology")
        
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = mock_csv.getvalue()
        
        with patch('requests.get', return_value=mock_response):
            companies = InsiderTrading.get_sp500_companies()
        
        assert companies == ["AAPL", "MSFT"]
    
    def test_get_sp500_companies_handles_errors(self, monkeypatch):
        """Test that get_sp500_companies handles network errors gracefully."""
        # Mock a failed request
        with patch('requests.get', side_effect=Exception("Network error")):
            companies = InsiderTrading.get_sp500_companies()
        
        # Should return default list
        assert companies == ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]
    
    def test_initialize_database(self, tmp_path):
        """Test database initialization."""
        # Create a test database file path
        test_db_path = os.path.join(tmp_path, "test_insider_trading.db")
        
        # Patch DB_PATH to use our test path
        with patch('InsiderTrading.DB_PATH', test_db_path):
            InsiderTrading.initialize_database()
        
        # Check that the database was created with the expected tables
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert ('insider_trading',) in tables
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        assert ('idx_issuer_ticker',) in indexes
        assert ('idx_transaction_date',) in indexes
        assert ('idx_reporting_owner',) in indexes
        
        conn.close()

    def test_query_insider_trading(self, test_db_path):
        """Test query_insider_trading function with various filters."""
        # Patch DB_PATH
        with patch('InsiderTrading.DB_PATH', test_db_path):
            # Test without filters
            result = InsiderTrading.query_insider_trading()
            assert len(result) > 0
            
            # Test with ticker filter
            result = InsiderTrading.query_insider_trading(ticker="AAPL")
            assert len(result) == 5
            assert all(row['issuer_ticker'] == 'AAPL' for _, row in result.iterrows())
            
            # Test with date range
            result = InsiderTrading.query_insider_trading(
                date_from="2025-01-01",
                date_to="2025-02-01"
            )
            assert len(result) > 0
            for _, row in result.iterrows():
                assert "2025-01-01" <= row['transaction_date'] <= "2025-02-01"
            
            # Test with limit
            result = InsiderTrading.query_insider_trading(limit=3)
            assert len(result) == 3

    def test_form4_processing(self, tmp_path, monkeypatch):
        """Test form 4 filing processing from XML."""
        # Create mock XML file
        form4_xml = """
        <ownershipDocument>
            <issuer>
                <issuerName>Apple Inc.</issuerName>
                <issuerTradingSymbol>AAPL</issuerTradingSymbol>
            </issuer>
            <reportingOwner>
                <reportingOwnerId>
                    <rptOwnerCik>0001111111</rptOwnerCik>
                    <rptOwnerName>Test, User</rptOwnerName>
                </reportingOwnerId>
                <reportingOwnerRelationship>
                    <officerTitle>CEO</officerTitle>
                </reportingOwnerRelationship>
            </reportingOwner>
            <nonDerivativeTable>
                <nonDerivativeTransaction>
                    <transactionDate>
                        <value>2025-03-15</value>
                    </transactionDate>
                    <transactionCoding>
                        <transactionCode>S</transactionCode>
                    </transactionCoding>
                    <transactionShares>
                        <value>5000</value>
                    </transactionShares>
                    <transactionPricePerShare>
                        <value>200.00</value>
                    </transactionPricePerShare>
                    <sharesOwnedFollowingTransaction>
                        <value>95000</value>
                    </sharesOwnedFollowingTransaction>
                </nonDerivativeTransaction>
            </nonDerivativeTable>
        </ownershipDocument>
        """
        
        # Create a test directory with XML file
        test_data_dir = os.path.join(tmp_path, "data")
        os.makedirs(os.path.join(test_data_dir, "sec-edgar-filings"), exist_ok=True)
        
        xml_file_path = os.path.join(test_data_dir, "test_form4.xml")
        with open(xml_file_path, "w") as f:
            f.write(form4_xml)
        
        # Create test database
        test_db_path = os.path.join(tmp_path, "test_insider_trading.db")
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS insider_trading (
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
        conn.commit()
        conn.close()
        
        # Mock dependencies
        with patch('InsiderTrading.DB_PATH', test_db_path), \
             patch('InsiderTrading.DATA_DIR', test_data_dir), \
             patch('glob.glob', return_value=[xml_file_path]):
            
            # Run the processing function
            InsiderTrading.process_form4_filings()
        
        # Verify the data was correctly inserted
        conn = sqlite3.connect(test_db_path)
        df = pd.read_sql_query("SELECT * FROM insider_trading", conn)
        conn.close()
        
        assert len(df) == 1
        assert df.iloc[0]['issuer_name'] == "Apple Inc."
        assert df.iloc[0]['issuer_ticker'] == "AAPL"
        assert df.iloc[0]['reporting_owner'] == "Test, User"
        assert df.iloc[0]['reporting_owner_cik'] == "0001111111"
        assert df.iloc[0]['reporting_owner_position'] == "CEO"
        assert df.iloc[0]['transaction_date'] == "2025-03-15"
        assert df.iloc[0]['transaction_shares'] == "5000"
        assert df.iloc[0]['transaction_price'] == "200.00"
        assert df.iloc[0]['transaction_type'] == "S"
        assert df.iloc[0]['shares_after_transaction'] == "95000"
        assert df.iloc[0]['source_file'] == xml_file_path