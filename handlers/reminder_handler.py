# handlers/reminder_handler.py
from services.order_service import (
    send_production_lists,
    send_daily_delivery_list,
    send_daily_reminder_to_branches
)
from utils.logger import get_logger
from datetime import datetime
import threading
import time

logger = get_logger("reminder_handler")

def send_morning_reminders():
    """Send morning reminders at 7:05 AM"""
    logger.info("Sending daily reminders at 7:05 AM")
    send_daily_reminder_to_branches()

def send_kitchen_notifications():
    """Send kitchen notifications at 7:00 AM"""
    logger.info("Sending kitchen notifications at 7:00 AM")
    send_production_lists()
    send_daily_delivery_list()

def schedule_daily_tasks():
    """Schedule daily tasks to run at specific times"""
    logger.info("Starting daily tasks scheduler")
    
    # Run continuously
    while True:
        now = datetime.now()
        
        # Check if it's time for morning reminders (7:05 AM)
        if now.hour == 19 and now.minute == 12:
            send_morning_reminders()
        
        # Check if it's time for kitchen notifications (7:00 AM)
        if now.hour == 19 and now.minute == 12:
            send_kitchen_notifications()
        
        # Sleep for 1 minute before checking again
        time.sleep(60)