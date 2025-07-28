# services/order_service.py
import csv
import uuid
import random
import string
from datetime import datetime, timedelta
from config.settings import ORDERS_CSV, BRANCHES, PAYMENT_BRANCHES, CUT_OFF_HOUR
from stateHandlers.redis_state import (
    get_user_state, set_user_state, get_user_cart, clear_user_cart,
    add_pending_order, add_active_order, get_order_status, update_order_status
)
from services.whatsapp_service import (
    send_order_confirmation, send_payment_link, send_status_update
)
from utils.logger import log_user_activity
from utils.csv_utils import log_order_to_csv

def generate_order_id():
    """Generate a unique order ID"""
    prefix = "FCT"
    timestamp = datetime.now().strftime("%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{random_part}"

def process_order(user_id, branch):
    """Process the user's order"""
    log_user_activity(user_id, "order_processing", f"Branch: {branch}")
    
    state = get_user_state(user_id)
    cart = get_user_cart(user_id)
    
    if not cart:
        log_user_activity(user_id, "order_error", "Empty cart")
        return False, "Your cart is empty. Please add items before placing an order."
    
    order_id = generate_order_id()
    total = sum(item["quantity"] * item["price"] for item in cart)
    
    # Determine if payment is required
    payment_required = branch.lower() in [b.lower() for b in PAYMENT_BRANCHES]
    
    # Create order data
    order_data = {
        "order_id": order_id,
        "customer_number": user_id,
        "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "branch": branch,
        "items": cart,
        "total": total,
        "payment_required": payment_required,
        "status": "pending",
        "payment_status": "pending" if payment_required else "completed"
    }
    
    # Add to pending orders in Redis
    add_pending_order(order_id, order_data)
    
    # Log to CSV
    log_order_to_csv(order_data)
    
    # Send confirmation message
    send_order_confirmation(user_id, order_id, branch, cart, total, payment_required)
    
    # If payment is required, send payment link
    if payment_required:
        send_payment_link(user_id, order_id, total)
    
    # Clear user's cart
    clear_user_cart(user_id)
    
    # Update user state
    state["step"] = "order_placed"
    state["order_id"] = order_id
    set_user_state(user_id, state)
    
    log_user_activity(user_id, "order_placed", f"Order ID: {order_id}, Total: {total}")
    
    return True, order_id

def confirm_order(whatsapp_number, payment_method, order_id, paid=False):
    """Confirm order after payment"""
    log_user_activity(whatsapp_number, "order_confirmation", f"Order ID: {order_id}, Paid: {paid}")
    
    # Get order from pending orders
    order_data = get_order_status(order_id)
    
    if not order_data:
        log_user_activity(whatsapp_number, "order_error", f"Order not found: {order_id}")
        return False, "Order not found"
    
    if paid:
        # Move from pending to active
        order_data["payment_status"] = "completed"
        order_data["status"] = "confirmed"
        
        # Remove from pending
        from stateHandlers.redis_state import remove_pending_order
        remove_pending_order(order_id)
        
        # Add to active
        from stateHandlers.redis_state import add_active_order
        add_active_order(order_id, order_data)
        
        # Send confirmation to user
        message = f"✅ *Payment Confirmed!*\n\nYour order #{order_id} has been confirmed and will be processed."
        from services.whatsapp_service import send_text_message
        send_text_message(whatsapp_number, message)
        
        log_user_activity(whatsapp_number, "order_confirmed", f"Order ID: {order_id}")
        return True, "Order confirmed"
    
    log_user_activity(whatsapp_number, "order_error", f"Payment not completed for order: {order_id}")
    return False, "Payment not completed"

def update_order_status_internal(order_id, status, notes=None):
    """Internal function to update order status"""
    result = update_order_status(order_id, status, notes)
    
    if result:
        # Get customer number from order data
        customer_number = result.get("customer_number")
        
        # Send status update to customer
        if customer_number:
            from services.whatsapp_service import send_status_update
            send_status_update(customer_number, order_id, status, notes)
        
        log_user_activity(customer_number or "system", "order_status_updated", 
                         f"Order ID: {order_id}, Status: {status}")
        return True
    
    return False

def get_todays_orders():
    """Get all orders for today's cycle"""
    # In a real implementation, you would fetch from Redis or CSV
    # For now, we'll return a sample
    
    # Determine today's cycle start time (7 AM today)
    now = datetime.now()
    cycle_start = now.replace(hour=CUT_OFF_HOUR, minute=0, second=0, microsecond=0)
    
    if now.hour < CUT_OFF_HOUR:
        # If before 7 AM, consider yesterday's 7 AM as cycle start
        cycle_start = cycle_start - timedelta(days=1)
    
    # In a real implementation, you would filter orders based on time
    # For now, return a sample
    return [
        {
            "order_id": "FCT0715A1B2",
            "branch": "nanakramguda",
            "items": [
                {"item": "banana", "quantity": 3, "unit": "kg"},
                {"item": "custard can", "quantity": 1},
                {"item": "apricot delight", "quantity": 5},
                {"item": "strawberry delight", "quantity": 2}
            ]
        },
        {
            "order_id": "FCT0715C3D4",
            "branch": "manikonda",
            "items": [
                {"item": "custard can", "quantity": 2},
                {"item": "oatmeal", "quantity": 2, "unit": "kg"},
                {"item": "strawberry delight", "quantity": 4},
                {"item": "blueberry delight", "quantity": 1},
                {"item": "apple", "quantity": 2, "unit": "kg"},
                {"item": "hand gloves", "quantity": 1, "unit": "pack"}
            ]
        }
    ]

def get_production_lists():
    """Get production lists for Sochin and Sagar"""
    orders = get_todays_orders()
    
    sochin_items = {}
    sagar_items = {}
    
    for order in orders:
        for item in order["items"]:
            item_name = item["item"].lower()
            
            # Check if it's Sochin's responsibility
            if item_name in ["custard can", "mango custard", "oatmeal", "less sugar custards"]:
                if item_name in sochin_items:
                    sochin_items[item_name] += item["quantity"]
                else:
                    sochin_items[item_name] = item["quantity"]
            
            # Check if it's Sagar's responsibility
            elif "delight" in item_name:
                if item_name in sagar_items:
                    sagar_items[item_name] += item["quantity"]
                else:
                    sagar_items[item_name] = item["quantity"]
    
    return {
        "sochin": sochin_items,
        "sagar": sagar_items
    }

def get_delivery_list():
    """Get delivery list for Ashok"""
    orders = get_todays_orders()
    
    delivery_list = {}
    
    for order in orders:
        branch = order["branch"]
        if branch not in delivery_list:
            delivery_list[branch] = []
        
        for item in order["items"]:
            delivery_list[branch].append(item)
    
    return delivery_list

def send_production_lists():
    """Send production lists to Sochin and Sagar"""
    lists = get_production_lists()
    
    # Format Sochin's list
    sochin_msg = ""
    for item, quantity in lists["sochin"].items():
        if "kg" in item:
            sochin_msg += f"- {item.title()} - {quantity}kg\n"
        else:
            sochin_msg += f"- {item.title()} - {quantity}\n"
    
    # Format Sagar's list
    sagar_msg = ""
    for item, quantity in lists["sagar"].items():
        if "kg" in item:
            sagar_msg += f"- {item.title()} - {quantity}kg\n"
        else:
            sagar_msg += f"- {item.title()} - {quantity}\n"
    
    # Send messages
    from services.whatsapp_service import send_text_message
    from config.settings import STAFF_CONTACTS
    
    if sochin_msg:
        send_text_message(STAFF_CONTACTS["sochin"], 
                         f"🍳 *PRODUCTION LIST - SOCHIN*\n\n{sochin_msg}\n\nPlease prepare these items for delivery today.")
    
    if sagar_msg:
        send_text_message(STAFF_CONTACTS["sagar"], 
                         f"🍰 *PRODUCTION LIST - SAGAR*\n\n{sagar_msg}\n\nPlease prepare these items for delivery today.")

def send_daily_delivery_list():
    """Send delivery list to Ashok"""
    delivery_list = get_delivery_list()
    
    if not delivery_list:
        return
    
    msg = "📦 *DELIVERY SCHEDULE*\n\n"
    
    for branch, items in delivery_list.items():
        msg += f"*{branch.title()}:*\n"
        for item in items:
            if "unit" in item:
                msg += f"- {item['item'].title()} - {item['quantity']}{item['unit']}\n"
            else:
                msg += f"- {item['item'].title()} - {item['quantity']}\n"
        msg += "\n"
    
    from services.whatsapp_service import send_text_message
    from config.settings import STAFF_CONTACTS
    
    send_text_message(STAFF_CONTACTS["ashok"], msg)

def send_daily_reminder_to_branches():
    """Send daily reminder to all branches"""
    reminder_msg = "⏰ *DAILY REMINDER*\n\nHello! Please order any raw materials required today via WhatsApp bot.\n\n*Cut-off time:* 7:00 AM tomorrow\n\nReply with 'menu' to start ordering."
    
    from config.settings import BRANCHES
    from services.whatsapp_service import send_text_message
    
    # In a real implementation, you would have actual branch numbers
    # For demo, we'll use sample numbers
    branch_numbers = {
        "madhapur": "919876543210",
        "kondapur": "919876543211",
        "west maredpally": "919876543212",
        "manikonda": "919876543213",
        "nanakramguda": "919876543214",
        "nizampet": "919876543215",
        "miyapur": "919876543216",
        "pragathinagar": "919876543217"
    }
    
    for branch, number in branch_numbers.items():
        send_text_message(number, reminder_msg)