from datetime import datetime, timedelta
import argparse  # for --no download option command line argument
import pandas as pd
import os
import glob
import xml.etree.ElementTree as ET
import json
from sec_edgar_downloader import Downloader

# Use relative path for data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def main():
    """Main function to download and analyze Form 4 filings."""
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Process SEC Form 4 filings.')
    parser.add_argument('--no-download', action='store_true', 
                        help='Skip downloading new filings and only process existing files')
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not args.no_download:
        # Only run download code if --no-download is NOT specified
        # Define date range for Form 4 filings
        end_date = datetime.now().strftime("%Y-%m-%d")  # Today
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")  # 6 months ago
        print(f"Using sec-edgar-downloader to fetch Form 4 filings from {start_date} to {end_date}...")
        
        # Initialize the downloader with company name and user email (required by SEC)
        company_name = "For Good Measure Limited"
        user_email = "kennylamitunes@yahoo.com"
        dl = Downloader(company_name, user_email, DATA_DIR)
        
        # Define companies to track
        companies = ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]
        
        # Download Form 4 filings for each company
        for ticker in companies:
            try:
                print(f"Downloading Form 4 filings for {ticker}...")
                # Download Form 4 filings within the specified date range
                # Set download_details=True to get the XML files
                dl.get("4", ticker, after=start_date, before=end_date, download_details=True)
                print(f"Successfully downloaded Form 4 filings for {ticker}")
            except Exception as e:
                print(f"Error downloading Form 4 filings for {ticker}: {e}")
    else:
        print("Skipping download, processing existing files only...")
    
    # Check the downloaded data structure
    check_downloaded_data()
    
    # Process the downloaded Form 4 filings
    process_form4_filings()

def check_downloaded_data():
    """Examines the downloaded data structure and prints information about it."""
    print("\nChecking downloaded data structure:")
    
    # List directories and files
    if not os.path.exists(DATA_DIR):
        print(f"Error: Directory {DATA_DIR} does not exist")
        return
    
    # Count files 
    print(f"\nDirectory structure:")
    for root, dirs, files in os.walk(DATA_DIR):
        depth = root.replace(DATA_DIR, '').count(os.sep)
        indent = ' ' * 4 * depth
        print(f"{indent}{os.path.basename(root)}/")
        if depth < 2:  # Only show files for the first two levels
            for file in files:
                print(f"{indent}    {file}")
    
    # Find XML files
    xml_files = glob.glob(f"{DATA_DIR}/**/*.xml", recursive=True)
    print(f"\nFound {len(xml_files)} XML files")
    
    # Examine a sample XML file if available
    if xml_files:
        sample_file = xml_files[0]
        print(f"\nExamining sample XML file: {os.path.basename(sample_file)}")
        try:
            tree = ET.parse(sample_file)
            root = tree.getroot()
            print(f"Root tag: {root.tag}")
            print(f"Namespace: {root.attrib}")
            print("\nChild elements:")
            for child in list(root)[:5]:  # Print first 5 children
                print(f"  {child.tag}")
        except Exception as e:
            print(f"Error parsing XML: {e}")

def process_form4_filings():
    """Process the downloaded Form 4 filings to extract insider trading information."""
    print("\nProcessing Form 4 filings...")
    
    # Find all XML files (Form 4 filings are in XML format)
    xml_files = glob.glob(f"{DATA_DIR}/**/*.xml", recursive=True)
    
    if not xml_files:
        print("No XML files found to process")
        return
    
    # Create a DataFrame to store the insider trading data
    insider_data = []
    
    for xml_file in xml_files:
        try:
            # Parse the XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract relevant information
            issuer_name = None
            issuer_ticker = None
            reporting_owner = None
            reporting_owner_cik = None  # Added for CIK
            transaction_date = None
            transaction_shares = None
            transaction_price = None
            transaction_type = None
            shares_after_transaction = None  # Added for shares owned after transaction
            
            # Extract issuer information
            for elem in root.findall(".//issuerName"):
                issuer_name = elem.text
                break
            
            for elem in root.findall(".//issuerTradingSymbol"):
                issuer_ticker = elem.text
                break
            
            # Extract reporting owner information
            for elem in root.findall(".//rptOwnerName"):
                reporting_owner = elem.text
                break
            
            # Extract reporting owner CIK
            for elem in root.findall(".//rptOwnerCik"):
                reporting_owner_cik = elem.text
                break
            
            # Extract transaction information
            # Get the first non-derivative transaction (for simplicity)
            non_derivative_transactions = root.findall(".//nonDerivativeTransaction")
            if non_derivative_transactions:
                transaction = non_derivative_transactions[0]  # Get the first transaction
                
                # Extract transaction date
                date_elem = transaction.find(".//transactionDate/value")
                if date_elem is not None:
                    transaction_date = date_elem.text
                
                # Extract transaction shares
                shares_elem = transaction.find(".//transactionShares/value")
                if shares_elem is not None:
                    transaction_shares = shares_elem.text
                
                # Extract transaction price
                price_elem = transaction.find(".//transactionPricePerShare/value")
                if price_elem is not None:
                    transaction_price = price_elem.text
                
                # Extract transaction code
                code_elem = transaction.find(".//transactionCode")
                if code_elem is not None:
                    transaction_type = code_elem.text
                
                # Extract shares owned after transaction
                post_shares_elem = transaction.find(".//sharesOwnedFollowingTransaction/value")
                if post_shares_elem is not None:
                    shares_after_transaction = post_shares_elem.text
            
            # Add to our data list
            insider_data.append({
                'issuer_name': issuer_name,
                'issuer_ticker': issuer_ticker,
                'reporting_owner': reporting_owner,
                'reporting_owner_cik': reporting_owner_cik,  # Added CIK
                'transaction_date': transaction_date,
                'transaction_shares': transaction_shares,
                'transaction_price': transaction_price,
                'transaction_type': transaction_type,
                'shares_after_transaction': shares_after_transaction,  # Added shares after transaction
                'source_file': xml_file  # Full path instead of just filename
            })
        
        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
    
    # Convert to DataFrame
    if insider_data:
        df = pd.DataFrame(insider_data)
        print("\nInsider Trading Data Summary:")
        print(f"Total transactions: {len(df)}")
        
        # Save to CSV
        csv_path = os.path.join(DATA_DIR, 'insider_trading_data.csv')
        df.to_csv(csv_path, index=False)
        print(f"Saved insider trading data to {csv_path}")
        
        # Display sample data
        if len(df) > 0:
            print("\nSample transactions:")
            print(df.head(5).to_string())
    else:
        print("No insider trading data extracted")

if __name__ == "__main__":
    main()
