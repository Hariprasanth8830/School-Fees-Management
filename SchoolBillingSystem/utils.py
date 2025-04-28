import os
import json
import logging
from datetime import datetime

def ensure_data_files():
    """Create data directory and initialize empty JSON files if they don't exist"""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Define the files we need
    required_files = [
        'students.json',
        'fees.json',
        'bills.json',
        'payments.json'
    ]
    
    # Initialize each file with an empty array if it doesn't exist
    for file_name in required_files:
        file_path = os.path.join('data', file_name)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)
                logging.info(f"Created empty file: {file_path}")

def load_data(file_name):
    """Load data from a JSON file"""
    file_path = os.path.join('data', file_name)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        # Return empty list if there's an error
        return []

def save_data(file_name, data):
    """Save data to a JSON file"""
    file_path = os.path.join('data', file_name)
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Data saved to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving to {file_path}: {str(e)}")
        return False

def generate_bill_number():
    """Generate a unique bill number with format: BILL-YYYYMMDD-XXXX"""
    # Get current date
    today = datetime.now()
    date_part = today.strftime('%Y%m%d')
    
    # Load existing bills to determine the next sequential number
    bills = load_data('bills.json')
    
    # Filter bills created today
    today_bills = [bill for bill in bills if bill.get('created_at', '').startswith(today.strftime('%Y-%m-%d'))]
    
    # Get the next sequence number
    next_seq = len(today_bills) + 1
    
    # Format the bill number
    bill_number = f"BILL-{date_part}-{next_seq:04d}"
    
    return bill_number
