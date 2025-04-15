"""
Tests for the export_json.py script.
"""
import os
import json
import pytest
import sqlite3
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys

# Add the parent directory to the path so we can import from the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import export_json

class TestExportJson:
    
    def test_initialize_json_directory(self, test_db_path, test_json_dir):
        """Test JSON directory initialization."""
        # Patch dependencies
        with patch('export_json.DB_PATH', test_db_path), \
             patch('export_json.JSON_DIR', test_json_dir):
            
            # Run the function
            export_json.initialize_json_directory()
        
        # Verify company directories were created
        assert os.path.exists(os.path.join(test_json_dir, 'AAPL'))
        assert os.path.exists(os.path.join(test_json_dir, 'MSFT'))
        assert os.path.exists(os.path.join(test_json_dir, 'GOOGL'))
    
    def test_export_companies_index(self, test_db_path, test_json_dir):
        """Test exporting companies index."""
        # Patch dependencies
        with patch('export_json.DB_PATH', test_db_path), \
             patch('export_json.JSON_DIR', test_json_dir):
            
            # Run the function
            export_json.export_companies_index()
        
        # Verify the output file exists
        companies_file = os.path.join(test_json_dir, 'companies.json')
        assert os.path.exists(companies_file)
        
        # Verify the content
        with open(companies_file, 'r') as f:
            data = json.load(f)
        
        assert 'last_updated' in data
        assert 'count' in data
        assert 'companies' in data
        assert data['count'] == 3  # We have 3 companies in test data
        
        # Check company data
        companies = {c['ticker']: c for c in data['companies']}
        assert 'AAPL' in companies
        assert 'MSFT' in companies
        assert 'GOOGL' in companies
        
        assert companies['AAPL']['name'] == 'Apple Inc.'
        assert companies['MSFT']['name'] == 'Microsoft Corp'
        assert companies['GOOGL']['name'] == 'Alphabet Inc.'
        
        # Check transaction counts
        assert companies['AAPL']['transaction_count'] == 5
        assert companies['MSFT']['transaction_count'] == 3
        assert companies['GOOGL']['transaction_count'] == 2
    
    def test_export_company_transactions(self, test_db_path, test_json_dir):
        """Test exporting company transactions."""
        # Patch dependencies
        with patch('export_json.DB_PATH', test_db_path), \
             patch('export_json.JSON_DIR', test_json_dir):
            
            # Initialize directories first
            export_json.initialize_json_directory()
            
            # Run the function
            export_json.export_company_transactions()
        
        # Verify the output files exist
        aapl_file = os.path.join(test_json_dir, 'AAPL', 'transactions.json')
        assert os.path.exists(aapl_file)
        
        # Check quarterly directories
        assert os.path.exists(os.path.join(test_json_dir, 'AAPL', 'quarterly'))
        
        # Verify the content
        with open(aapl_file, 'r') as f:
            data = json.load(f)
        
        assert 'ticker' in data
        assert 'last_updated' in data
        assert 'count' in data
        assert 'transactions' in data
        assert data['ticker'] == 'AAPL'
        assert data['count'] == 5  # 5 AAPL transactions in test data
        
        # Check a specific transaction
        transactions = data['transactions']
        cook_sales = [t for t in transactions if t['reporting_owner'] == 'Cook, Tim' and t['transaction_type'] == 'S']
        assert len(cook_sales) == 1
        assert cook_sales[0]['transaction_shares'] == '10000'
        assert cook_sales[0]['transaction_price'] == '180.25'
        
        # Check quarterly files
        quarterly_files = os.listdir(os.path.join(test_json_dir, 'AAPL', 'quarterly'))
        assert len(quarterly_files) > 0
        
        # Check a quarterly file content
        quarterly_file = os.path.join(test_json_dir, 'AAPL', 'quarterly', quarterly_files[0])
        with open(quarterly_file, 'r') as f:
            quarterly_data = json.load(f)
        
        assert 'year' in quarterly_data
        assert 'quarter' in quarterly_data
        assert 'transactions' in quarterly_data
        assert isinstance(quarterly_data['year'], int)
        assert isinstance(quarterly_data['quarter'], int)
        assert len(quarterly_data['transactions']) > 0
    
    def test_export_summary_data(self, test_db_path, test_json_dir):
        """Test exporting summary data."""
        # Patch dependencies
        with patch('export_json.DB_PATH', test_db_path), \
             patch('export_json.JSON_DIR', test_json_dir):
            
            # Run the function
            export_json.export_summary_data()
        
        # Verify the output file exists
        summary_file = os.path.join(test_json_dir, 'summary.json')
        assert os.path.exists(summary_file)
        
        # Verify the content
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
        assert 'last_updated' in data
        assert 'large_transactions' in data
        assert 'recent_transactions' in data
        
        # Check large transactions
        assert len(data['large_transactions']) > 0
        
        # MSFT transaction should be in top transactions (15000 shares at $380.50)
        msft_present = False
        for txn in data['large_transactions']:
            if txn['ticker'] == 'MSFT' and txn['insider'] == 'Nadella, Satya':
                msft_present = True
                assert float(txn['shares']) == 15000.0
                assert float(txn['price']) == 380.50
                break
        
        assert msft_present, "Expected large MSFT transaction not found"
        
        # Check recent transactions
        assert len(data['recent_transactions']) > 0
    
    def test_main_function(self, test_db_path, test_json_dir):
        """Test the main function."""
        # Patch dependencies and function calls
        with patch('export_json.DB_PATH', test_db_path), \
             patch('export_json.JSON_DIR', test_json_dir), \
             patch('export_json.initialize_json_directory') as mock_init, \
             patch('export_json.export_companies_index') as mock_companies, \
             patch('export_json.export_company_transactions') as mock_transactions, \
             patch('export_json.export_summary_data') as mock_summary, \
             patch('os.path.exists', return_value=True):  # Simulate DB exists
            
            # Run the main function
            export_json.main()
        
        # Verify all functions were called
        mock_init.assert_called_once()
        mock_companies.assert_called_once()
        mock_transactions.assert_called_once()
        mock_summary.assert_called_once()
    
    def test_missing_database_error(self, test_db_path, test_json_dir):
        """Test handling of missing database."""
        # Patch dependencies
        with patch('export_json.DB_PATH', '/nonexistent/path.db'), \
             patch('os.path.exists', return_value=False), \
             patch('export_json.initialize_json_directory') as mock_init, \
             patch('export_json.export_companies_index') as mock_companies:
            
            # Run the main function
            export_json.main()
        
        # Verify functions were not called
        mock_init.assert_not_called()
        mock_companies.assert_not_called()
    
    def test_empty_database(self, tmp_path):
        """Test handling of an empty database."""
        # Create empty database
        empty_db_path = os.path.join(tmp_path, "empty.db")
        conn = sqlite3.connect(empty_db_path)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()
        
        # Create empty JSON directory
        empty_json_dir = os.path.join(tmp_path, "json")
        os.makedirs(empty_json_dir, exist_ok=True)
        
        # Patch dependencies
        with patch('export_json.DB_PATH', empty_db_path), \
             patch('export_json.JSON_DIR', empty_json_dir):
            
            # Initialize directory (should handle empty case)
            export_json.initialize_json_directory()
            
            # Export companies (should handle empty case)
            export_json.export_companies_index()
            
            # Export transactions (should handle empty case)
            export_json.export_company_transactions()
            
            # Export summary (should handle empty case)
            export_json.export_summary_data()
        
        # Verify the output files still exist but are empty/minimal
        companies_file = os.path.join(empty_json_dir, 'companies.json')
        assert os.path.exists(companies_file)
        
        with open(companies_file, 'r') as f:
            data = json.load(f)
        
        assert data['count'] == 0
        assert len(data['companies']) == 0