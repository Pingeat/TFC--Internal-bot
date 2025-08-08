# # utils/logger.py
# import logging
# import os
# from datetime import datetime

# def get_logger(name):
#     """Create and configure a logger"""
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)
    
#     # Create formatter
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
#     # Create console handler
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)
#     logger.addHandler(console_handler)
    
#     return logger

# def log_user_activity(user_id, activity_type, details):
#     """Log user activity to CSV and logger"""
#     # Get the logger (don't do this at module level to avoid circular imports)
#     logger = get_logger("activity")
    
#     # Log to console first
#     logger.info(f"{user_id} - {activity_type}: {details}")
    
#     # Try to log to CSV, but don't fail if it doesn't work
#     try:
#         from utils.csv_utils import append_to_csv
#         from config.settings import USER_LOG_CSV
        
#         # Create log entry
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         log_entry = {
#             "timestamp": timestamp,
#             "user_id": user_id,
#             "activity_type": activity_type,
#             "details": details
#         }
        
#         # Log to CSV
#         append_to_csv(USER_LOG_CSV, log_entry)
#     except Exception as e:
#         # We can't use the normal logger here due to potential circular imports
#         print(f"[LOGGER] Failed to log to CSV: {str(e)}")







# utils/logger.py
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from config.settings import USER_LOG_CSV

IST = ZoneInfo("Asia/Kolkata")
def get_logger(name):
    """Create and configure a logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_user_activity(user_id, activity_type, details):
    """Log user activity to CSV and logger"""
    # Get the logger (don't do this at module level to avoid circular imports)
    logger = get_logger("activity")
    
    # Log to console first
    logger.info(f"{user_id} - {activity_type}: {details}")
    
    # Try to log to CSV, but don't fail if it doesn't work
    try:
        from utils.csv_utils import append_to_csv
        
        # Create log entry
        timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details
        }
        
        # Log to CSV
        append_to_csv(USER_LOG_CSV, log_entry)
    except Exception as e:
        # We can't use the normal logger here due to potential circular imports
        print(f"[LOGGER] Failed to log to CSV: {str(e)}")


def truncate_text(text, max_length=24):
    """Truncate text to specified max length, adding ellipsis if needed"""
    if len(text) > max_length:
        return text[:max_length-1] + "…"
    return text