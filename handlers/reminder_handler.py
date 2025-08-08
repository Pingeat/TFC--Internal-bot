# handlers/reminder_handler.py
from zoneinfo import ZoneInfo

import pytz
from services.whatsapp_service import send_daily_delivery_list, send_production_lists
from utils.logger import get_logger
from datetime import datetime
import threading
import time

logger = get_logger("reminder_handler")
IST = ZoneInfo('Asia/Kolkata')
# def send_morning_reminders():
#     """Send morning reminders at 7:05 AM"""
#     logger.info("Sending daily reminders at 7:05 AM")
#     send_daily_reminder_to_branches()

# def send_kitchen_notifications():
#     """Send kitchen notifications at 7:00 AM"""
#     logger.info("Sending kitchen notifications at 7:00 AM")
#     send_production_lists()
#     send_daily_delivery_list()

# def schedule_daily_tasks():
#     """Schedule daily tasks to run at specific times"""
#     logger.info("Starting daily tasks scheduler")
    
#     # Run continuously
#     while True:
#         now = datetime.now()
        
#         # Check if it's time for morning reminders (7:05 AM)
#         if now.hour == 15 and now.minute == 44:
#             send_morning_reminders()
        
#         # Check if it's time for kitchen notifications (7:00 AM)
#         if now.hour == 15 and now.minute == 44:
#             send_kitchen_notifications()
        
#         # Sleep for 1 minute before checking again
#         time.sleep(60)



def send_morning_reminders():
    """Send morning reminders at 7:05 AM (skip on Sunday)"""
    # Skip if today is Sunday (Monday is 0, Sunday is 6)
    if datetime.now(IST).weekday() == 6:  # Sunday
        logger.info("Today is Sunday. Kitchen is closed. Skipping morning reminders.")
        return
    
    logger.info("Sending daily reminders at 7:05 AM")
    # send_daily_reminder_to_branches()

def send_kitchen_notifications():
    """Send kitchen notifications at 7:00 AM (skip on Sunday)"""
    # Skip if today is Sunday (Monday is 0, Sunday is 6)
    if datetime.now(IST).weekday() == 6:  # Sunday
        logger.info("Today is Sunday. Kitchen is closed. Skipping kitchen notifications.")
        return
    
    logger.info("Sending kitchen notifications at 7:00 AM")
    send_production_lists()
    send_daily_delivery_list()

def schedule_daily_tasks():
    """Schedule daily tasks to run at specific times"""
    logger.info("Starting daily tasks scheduler")
    
    # Run continuously
    while True:
        now = get_current_ist()
        logger.info(now)
        # Skip if today is Sunday (Monday is 0, Sunday is 6)
        if now.weekday() == 6:  # Sunday
            logger.info("Today is Sunday. Kitchen is closed. Skipping reminders and notifications.")
            time.sleep(60)
            continue
        
        # Check if it's time for morning reminders (7:05 AM)
        if now.hour == 7 and now.minute == 5:
            send_morning_reminders()
        
        # Check if it's time for kitchen notifications (7:00 AM)
        if now.hour == 7 and now.minute == 0:
            send_kitchen_notifications()
            
        if now.hour == 19 and now.minute == 17:
            send_kitchen_notifications()
        
        # Sleep for 1 minute before checking again
        time.sleep(60)





IST = pytz.timezone('Asia/Kolkata')

def get_current_ist():
    """Return current time in Indian Standard Time"""
    return datetime.now(IST)