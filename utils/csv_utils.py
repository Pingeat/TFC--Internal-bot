# utils/csv_utils.py
import os
import csv
from datetime import datetime
from config.settings import (
    ORDERS_CSV,
    FEEDBACK_CSV,
    USER_LOG_CSV,
    OFF_HOUR_USERS_CSV,
    PROMO_LOG_CSV
)

def initialize_csv_files():
    """Initialize CSV files if they don't exist"""
    print("[CSV] Initializing CSV files...")
    
    # Orders CSV
    if not os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Order ID", "Customer Number", "Order Time", "Branch", 
                "Items", "Total", "Payment Mode", "Paid", "Status", "Notes"
            ])
        print(f"[CSV] Created {ORDERS_CSV}")
    
    # Feedback CSV
    if not os.path.exists(FEEDBACK_CSV):
        with open(FEEDBACK_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Customer Number", "Order ID", "Rating", "Comment", "Timestamp"])
        print(f"[CSV] Created {FEEDBACK_CSV}")
    
    # User Log CSV
    if not os.path.exists(USER_LOG_CSV):
        with open(USER_LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Customer Number", "Timestamp", "Step", "Info"])
        print(f"[CSV] Created {USER_LOG_CSV}")
    
    # Off Hour Users CSV
    if not os.path.exists(OFF_HOUR_USERS_CSV):
        with open(OFF_HOUR_USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Phone Number", "Date"])
        print(f"[CSV] Created {OFF_HOUR_USERS_CSV}")
    
    # Promo Log CSV
    if not os.path.exists(PROMO_LOG_CSV):
        with open(PROMO_LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Phone Number", "Promo Name", "Date Sent"])
        print(f"[CSV] Created {PROMO_LOG_CSV}")

def log_order_to_csv(order_data):
    """Log order to CSV file"""
    try:
        # Format items for CSV
        items_str = "; ".join([f"{item['item']} x{item['quantity']}" for item in order_data["items"]])
        
        with open(ORDERS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                order_data["order_id"],
                order_data["customer_number"],
                order_data["order_time"],
                order_data["branch"],
                items_str,
                order_data["total"],
                "Online" if order_data["payment_required"] else "COD",
                "Yes" if order_data.get("payment_status") == "completed" else "No",
                order_data["status"],
                order_data.get("notes", "")
            ])
        
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity(order_data["customer_number"], "order_logged", f"Order ID: {order_data['order_id']}")
        print(f"[CSV] Order logged: {order_data['order_id']}")
    except Exception as e:
        print(f"[CSV] Error logging order: {e}")
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity("system", "csv_error", f"Error logging order: {str(e)}")

def log_feedback(customer_number, order_id, rating, comment):
    """Log feedback to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(FEEDBACK_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                customer_number,
                order_id,
                rating,
                comment,
                timestamp
            ])
        
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity(customer_number, "feedback_logged", f"Order ID: {order_id}, Rating: {rating}")
        print(f"[CSV] Feedback logged for order {order_id}")
    except Exception as e:
        print(f"[CSV] Error logging feedback: {e}")
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity(customer_number, "csv_error", f"Error logging feedback: {str(e)}")

def log_user_activity_csv(phone, step, info=""):
    """Log user activity to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(USER_LOG_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                phone,
                timestamp,
                step,
                info
            ])
    except Exception as e:
        print(f"[CSV] Error logging user activity: {e}")

def log_off_hour_user(phone):
    """Log off-hour user"""
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        
        with open(OFF_HOUR_USERS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                phone,
                date
            ])
        
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity(phone, "off_hour_logged", "User contacted during off-hours")
        print(f"[CSV] Off-hour user logged: {phone}")
    except Exception as e:
        print(f"[CSV] Error logging off-hour user: {e}")
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity("system", "csv_error", f"Error logging off-hour user: {str(e)}")

def log_promo_sent(phone, promo_name):
    """Log sent promotion"""
    try:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(PROMO_LOG_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                phone,
                promo_name,
                date
            ])
        
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity(phone, "promo_logged", f"Promo: {promo_name}")
        print(f"[CSV] Promotion logged for {phone}: {promo_name}")
    except Exception as e:
        print(f"[CSV] Error logging promotion: {e}")
        # LOCAL IMPORT - Fixed circular dependency
        from utils.logger import log_user_activity
        log_user_activity("system", "csv_error", f"Error logging promotion: {str(e)}")

# Initialize CSV files when module is imported
initialize_csv_files()