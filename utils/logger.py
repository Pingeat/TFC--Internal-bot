# utils/logger.py
import csv
from datetime import datetime
from pytz import timezone
from config.settings import USER_LOG_CSV
from utils.csv_utils import log_user_activity_csv

def log_user_activity(phone, step, info=""):
    """Log user activity with timestamp"""
    try:
        ist = timezone('Asia/Kolkata')
        timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOGGER] {phone}: {step} - {info}")
        
        # Log to CSV
        log_user_activity_csv(phone, step, info)
    except Exception as e:
        print(f"[LOGGER] Error logging activity: {e}")