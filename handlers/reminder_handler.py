# handlers/reminder_handler.py
from services.order_service import send_daily_reminder_to_branches, send_production_lists, send_daily_delivery_list
from utils.logger import log_user_activity
from datetime import datetime, time
import threading
import time as time_module

def send_morning_reminders():
    """Send morning reminders at 7:05 AM"""
    log_user_activity("system", "morning_reminders", "Sending daily reminders")
    print("[REMINDERS] Sending daily reminders at 7:05 AM")
    send_daily_reminder_to_branches()

def send_kitchen_notifications():
    """Send kitchen notifications at 7:00 AM"""
    log_user_activity("system", "kitchen_notifications", "Sending kitchen notifications")
    print("[REMINDERS] Sending kitchen notifications at 7:00 AM")
    send_production_lists()
    send_daily_delivery_list()

def schedule_daily_tasks():
    """Schedule daily tasks to run at specific times"""
    log_user_activity("system", "scheduler_started", "Daily tasks scheduler started")
    print("[SCHEDULER] Starting daily tasks scheduler")
    
    # Run continuously
    while True:
        now = datetime.now()
        
        # Check if it's time for morning reminders (7:05 AM)
        if now.hour == 7 and now.minute == 5:
            send_morning_reminders()
        
        # Check if it's time for kitchen notifications (7:00 AM)
        if now.hour == 7 and now.minute == 0:
            send_kitchen_notifications()
        
        # Sleep for 1 minute before checking again
        time_module.sleep(60)