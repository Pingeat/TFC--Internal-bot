# utils/csv_utils.py
import csv
import os
import json
from datetime import datetime

def ensure_csv_exists(file_path, headers):
    """Ensure CSV file exists with headers"""
    try:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
    except Exception as e:
        # Can't use logger here due to circular imports
        print(f"[CSV_UTILS] Error creating CSV file {file_path}: {str(e)}")

def append_to_csv(file_path, data):
    """Append data to CSV file"""
    try:
        # Determine headers based on data
        headers = list(data.keys())
        
        # Ensure file exists with headers
        if not os.path.exists(file_path):
            ensure_csv_exists(file_path, headers)
        
        # Get headers from existing file
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                headers = list(data.keys())
        
        # Append data
        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writerow(data)
    except Exception as e:
        # Can't use logger here due to circular imports
        print(f"[CSV_UTILS] Error appending to CSV {file_path}: {str(e)}")
        raise

def read_csv(file_path):
    """Read data from CSV file"""
    try:
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        # Can't use logger here due to circular imports
        print(f"[CSV_UTILS] Error reading CSV {file_path}: {str(e)}")
        return []