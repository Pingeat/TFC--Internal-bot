# # services/order_service.py
# import uuid
# import json
# from datetime import datetime
# from utils.logger import get_logger
# from utils.csv_utils import append_to_csv, read_csv
# from config.settings import ORDERS_CSV, ORDER_STATUS, PAYMENT_BRANCHES
# from stateHandlers.redis_state import redis_state
# from services.whatsapp_service import (
#     send_order_confirmation,
#     notify_supervisor,
#     send_payment_link
# )
# import csv

# logger = get_logger("order_service")

# def generate_order_id():
#     """Generate a unique order ID"""
#     return f"FCT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"

# def place_order(user_id, branch):
#     """Place an order from user's cart"""
#     logger.info(f"Placing order for user {user_id} from branch {branch}")
    
#     # Get cart
#     cart = redis_state.get_cart(user_id)
#     if not cart["items"]:
#         logger.warning(f"Cart is empty for user {user_id}")
#         return False, "Your cart is empty. Please add items before placing an order."
    
#     # Generate order ID
#     order_id = generate_order_id()
    
#     # Check if payment is required
#     payment_required = branch.lower() in [b.lower() for b in PAYMENT_BRANCHES]
    
#     # Prepare order data
#     order_data = {
#         "order_id": order_id,
#         "user_id": user_id,
#         "branch": branch,
#         "items": json.dumps(cart["items"]),
#         "total": cart["total"],
#         "status": ORDER_STATUS["PENDING"],
#         "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "payment_required": str(payment_required),
#         "payment_status": "PENDING" if payment_required else "PAID"
#     }
    
#     # Save to CSV
#     try:
#         append_to_csv(ORDERS_CSV, order_data)
#         logger.info(f"Order {order_id} saved to CSV")
#     except Exception as e:
#         logger.error(f"Failed to save order {order_id}: {str(e)}")
#         return False, "Failed to save order. Please try again."
    
#     # Notify supervisor
#     notify_supervisor(order_id, branch, cart["items"])
    
#     # Clear cart
#     redis_state.clear_cart(user_id)
    
#     # Handle payment if required
#     if payment_required:
#         # In a real implementation, this would generate a Razorpay payment link
#         # payment_link = f"https://api.razorpay.com/v1/payment_links/create?order_id={order_id}&amount={cart['total']}"
        
#         # Send payment link
#         send_payment_link(user_id, order_id, cart["total"])
        
#         return True, f"Order #{order_id} placed successfully! Please complete payment to confirm your order."
#     else:
#         # Send order confirmation
#         send_order_confirmation(user_id, order_id, branch)
        
#         # Update order status to PAID
#         update_order_status(order_id, ORDER_STATUS["PAID"])
        
#         return True, f"Order #{order_id} placed successfully! Your order is being processed."

# def confirm_order(whatsapp_number, payment_method, order_id, paid=False):
#     """Confirm order after payment"""
#     logger.info(f"Confirming order {order_id} for {whatsapp_number}")
    
#     # Find the order
#     orders = read_csv(ORDERS_CSV)
#     order = next((o for o in orders if o["order_id"] == order_id), None)
    
#     if not order:
#         logger.error(f"Order {order_id} not found")
#         return False
    
#     if paid:
#         # Update order status
#         update_order_status(order_id, ORDER_STATUS["PAID"])
        
#         # Send order confirmation
#         send_order_confirmation(whatsapp_number, order_id, order["branch"])
        
#         logger.info(f"Order {order_id} confirmed and payment marked as paid")
#         return True
    
#     logger.warning(f"Order {order_id} confirmation failed - payment not completed")
#     return False

# def update_order_status(order_id, status):
#     """Update order status"""
#     logger.info(f"Updating order {order_id} status to {status}")
    
#     # Read existing orders
#     orders = read_csv(ORDERS_CSV)
    
#     # Update status for the matching order
#     updated = False
#     for order in orders:
#         print("[ORDER]:", order)
#         if order["order_id"] == order_id:
#             order["status"] = status
#             order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             updated = True
#             break
    
#     if not updated:
#         logger.error(f"Order {order_id} not found for status update")
#         return False
    
#     # Rewrite CSV with updated order
#     try:
#         # Get headers from original CSV
#         with open(ORDERS_CSV, 'r') as f:
#             reader = csv.reader(f)
#             try:
#                 headers = next(reader)
#             except StopIteration:
#                 # If file is empty, use keys from first order
#                 headers = list(orders[0].keys()) if orders else []
        
#         # Write updated data
#         with open(ORDERS_CSV, 'w', newline='') as f:
#             writer = csv.DictWriter(f, fieldnames=headers)
#             writer.writeheader()
#             for order in orders:
#                 writer.writerow(order)
        
#         logger.info(f"Order {order_id} status updated to {status}")
#         return True
#     except Exception as e:
#         logger.error(f"Failed to update order status: {str(e)}")
#         return False

# def send_production_lists():
#     """Wrapper for sending production lists"""
#     from services.whatsapp_service import send_production_list
#     send_production_list()

# def send_daily_delivery_list():
#     """Wrapper for sending daily delivery list"""
#     from services.whatsapp_service import send_delivery_list
#     send_delivery_list()

# def send_daily_reminder_to_branches():
#     """Wrapper for sending daily reminder"""
#     from services.whatsapp_service import send_daily_reminder
#     send_daily_reminder()







# services/order_service.py
import uuid
import json
from datetime import datetime
from utils.logger import get_logger
from utils.csv_utils import append_to_csv, read_csv
from config.settings import ORDERS_CSV, ORDER_STATUS, PAYMENT_BRANCHES, PRODUCT_CATEGORIES, STAFF_CONTACTS
from stateHandlers.redis_state import redis_state
from services.whatsapp_service import (
    send_order_confirmation,
    notify_supervisor,
    send_payment_link,
    send_text_message
)
import csv

logger = get_logger("order_service")

def generate_order_id():
    """Generate a unique order ID"""
    return f"FCT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"

def place_order(user_id, branch):
    """Place an order from user's cart"""
    logger.info(f"Placing order for user {user_id} from branch {branch}")
    
    # Get cart
    cart = redis_state.get_cart(user_id)
    if not cart["items"]:
        logger.warning(f"Cart is empty for user {user_id}")
        return False, "Your cart is empty. Please add items before placing an order."
    
    # Generate order ID
    order_id = generate_order_id()
    
    # Check if payment is required
    payment_required = branch.lower() in [b.lower() for b in PAYMENT_BRANCHES]
    
    # Prepare order data
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "branch": branch,
        "items": json.dumps(cart["items"]),
        "total": cart["total"],
        "status": ORDER_STATUS["PENDING"],
        "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payment_required": str(payment_required),
        "payment_status": "PENDING" if payment_required else "PAID"
    }
    
    # Save to CSV
    try:
        append_to_csv(ORDERS_CSV, order_data)
        logger.info(f"Order {order_id} saved to CSV")
    except Exception as e:
        logger.error(f"Failed to save order {order_id}: {str(e)}")
        return False, "Failed to save order. Please try again."
    
    # Notify supervisor
    notify_supervisor(order_id, branch, cart["items"])
    
    # Clear cart
    redis_state.clear_cart(user_id)
    
    # Handle payment if required
    if payment_required:
        # In a real implementation, this would generate a Razorpay payment link
        # payment_link = f"https://api.razorpay.com/v1/payment_links/create?order_id={order_id}&amount={cart['total']}"
        
        # Send payment link
        send_payment_link(user_id, order_id, cart["total"])
        
        return True, f"Order #{order_id} placed successfully! Please complete payment to confirm your order."
    else:
        # Send order confirmation WITH ORDER ITEMS
        send_order_confirmation(user_id, order_id, branch, cart["items"], cart["total"])
        
        # Update order status to PAID
        update_order_status(order_id, ORDER_STATUS["PAID"])
        
        return True, f"Order #{order_id} placed successfully! Your order is being processed."


def update_order_status(order_id, status):
    """Update order status in Redis and CSV with notifications"""
    logger.info(f"Updating order {order_id} status to {status}")
    
    # Validate status
    valid_statuses = list(ORDER_STATUS.values())
    if status not in valid_statuses:
        logger.error(f"Invalid status '{status}' for order {order_id}. Valid statuses: {valid_statuses}")
        return False
    
    # Try to find the order in Redis first (primary data source)
    order = None
    all_orders = redis_state.redis.lrange("orders:all", 0, -1)
    order_index = -1
    
    for i, order_str in enumerate(all_orders):
        o = json.loads(order_str)
        if o["order_id"] == order_id:
            order = o
            order_index = i
            break
    
    # If not found in Redis, check CSV as fallback
    if not order:
        logger.warning(f"Order {order_id} not found in Redis, checking CSV")
        orders = read_csv(ORDERS_CSV)
        for i, o in enumerate(orders):
            if o["order_id"] == order_id:
                # Reconstruct order structure
                order = {
                    "order_id": o["order_id"],
                    "user_id": o["user_id"],
                    "branch": o["branch"],
                    "items": json.loads(o["items"]),
                    "total": float(o["total"]),
                    "status": o["status"],
                    "order_date": o["order_date"],
                    "payment_required": o["payment_required"] == "True",
                    "payment_status": o["payment_status"]
                }
                order_index = i
                # Re-add to Redis since it was missing
                redis_state.redis.rpush("orders:all", json.dumps(order))
                redis_state.redis.rpush(f"orders:branch:{order['branch'].lower()}", json.dumps(order))
                logger.info(f"Recovered order {order_id} from CSV and added back to Redis")
                break
    
    if not order:
        logger.error(f"Order {order_id} not found in Redis or CSV")
        return False
    
    # Don't allow status downgrade
    status_priority = {
        ORDER_STATUS["PENDING"]: 1,
        ORDER_STATUS["PAID"]: 2,
        ORDER_STATUS["READY"]: 3,
        ORDER_STATUS["DELIVERED"]: 4,
        ORDER_STATUS["COMPLETED"]: 5
    }
    
    current_priority = status_priority.get(order["status"], 0)
    new_priority = status_priority.get(status, 0)
    
    if new_priority < current_priority:
        logger.warning(f"Attempt to downgrade status for order {order_id} from {order['status']} to {status}")
        return False
    
    # Update the order
    updated_order = {
        **order,
        "status": status,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Update in Redis
    if order_index >= 0:
        # Update in main orders list
        redis_state.redis.lset("orders:all", order_index, json.dumps(updated_order))
        
        # Update in branch-specific list
        branch_orders = redis_state.redis.lrange(f"orders:branch:{order['branch'].lower()}", 0, -1)
        for i, order_str in enumerate(branch_orders):
            o = json.loads(order_str)
            if o["order_id"] == order_id:
                redis_state.redis.lset(f"orders:branch:{order['branch'].lower()}", i, json.dumps(updated_order))
                break
    
    # Update in CSV as backup
    try:
        update_order_in_csv(order_id, updated_order)
    except Exception as e:
        logger.error(f"Failed to update CSV for order {order_id}: {str(e)}")
        # Continue execution since Redis has the update
    
    # Send notifications based on new status
    if status == ORDER_STATUS["READY"]:
        # Notify delivery person (Ashok) that order is ready
        message = f"📦 *ORDER READY FOR DELIVERY*\n\nOrder ID: #{order_id}\nBranch: {order['branch'].title()}"
        send_text_message(STAFF_CONTACTS["ashok"], message)
        
        # Notify customer that order is ready
        send_text_message(order["user_id"], f"📦 Your order #{order_id} is ready for delivery!")
        
    elif status == ORDER_STATUS["DELIVERED"]:
        # Notify customer that order has been delivered
        send_text_message(order["user_id"], f"✅ Your order #{order_id} has been delivered successfully!")
        
        # Check if all orders for the day are delivered
        todays_orders = redis_state.get_todays_orders()
        all_delivered = all(o["status"] == ORDER_STATUS["DELIVERED"] for o in todays_orders)
        
        if all_delivered:
            # Notify supervisor that all orders are delivered
            send_text_message(STAFF_CONTACTS["krishna"], "✅ *ALL ORDERS DELIVERED*\n\nAll orders for today have been successfully delivered.")
    
    elif status == ORDER_STATUS["COMPLETED"]:
        # Final completion notification
        send_text_message(STAFF_CONTACTS["krishna"], f"✅ *DAY COMPLETED*\n\nOrder #{order_id} marked as completed. All processes finished.")
    
    logger.info(f"Order {order_id} status updated to {status} successfully")
    return True

def confirm_order(whatsapp_number, payment_method, order_id, paid=False):
    """Confirm order after payment with Redis-first approach"""
    logger.info(f"Confirming order {order_id} for {whatsapp_number}")
    
    # Try to find the order in Redis first
    order = None
    all_orders = redis_state.redis.lrange("orders:all", 0, -1)
    for order_str in all_orders:
        o = json.loads(order_str)
        if o["order_id"] == order_id:
            order = o
            break
    
    # If not found in Redis, check CSV as fallback
    if not order:
        logger.warning(f"Order {order_id} not found in Redis, checking CSV")
        orders = read_csv(ORDERS_CSV)
        for o in orders:
            if o["order_id"] == order_id:
                # Reconstruct order structure
                order = {
                    "order_id": o["order_id"],
                    "user_id": o["user_id"],
                    "branch": o["branch"],
                    "items": json.loads(o["items"]),
                    "total": float(o["total"]),
                    "status": o["status"],
                    "order_date": o["order_date"],
                    "payment_required": o["payment_required"] == "True",
                    "payment_status": o["payment_status"]
                }
                # Re-add to Redis since it was missing
                redis_state.redis.rpush("orders:all", json.dumps(order))
                redis_state.redis.rpush(f"orders:branch:{order['branch'].lower()}", json.dumps(order))
                logger.info(f"Recovered order {order_id} from CSV and added back to Redis")
                break
    
    if not order:
        logger.error(f"Order {order_id} not found in Redis or CSV")
        return False
    
    if paid:
        # Update order status in Redis
        updated_order = {
            **order,
            "status": ORDER_STATUS["PAID"],
            "payment_status": "PAID",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Replace the order in Redis
        all_orders = redis_state.redis.lrange("orders:all", 0, -1)
        for i, order_str in enumerate(all_orders):
            o = json.loads(order_str)
            if o["order_id"] == order_id:
                redis_state.redis.lset("orders:all", i, json.dumps(updated_order))
                break
        
        # Update branch-specific list
        branch_orders = redis_state.redis.lrange(f"orders:branch:{order['branch'].lower()}", 0, -1)
        for i, order_str in enumerate(branch_orders):
            o = json.loads(order_str)
            if o["order_id"] == order_id:
                redis_state.redis.lset(f"orders:branch:{order['branch'].lower()}", i, json.dumps(updated_order))
                break
        
        # Also update CSV as backup
        try:
            update_order_in_csv(order_id, updated_order)
        except Exception as e:
            logger.error(f"Failed to update CSV for order {order_id}: {str(e)}")
        
        # Send order confirmation
        send_order_confirmation(whatsapp_number, order_id, order["branch"])
        
        logger.info(f"Order {order_id} confirmed and payment marked as paid")
        return True
    
    logger.warning(f"Order {order_id} confirmation failed - payment not completed")
    return False

def update_order_in_csv(order_id, order_data):
    """Update an order in the CSV file"""
    try:
        # Read existing orders
        orders = read_csv(ORDERS_CSV)
        
        # Update the matching order
        updated = False
        for i, order in enumerate(orders):
            if order["order_id"] == order_id:
                # Convert Redis order format to CSV format
                orders[i] = {
                    "order_id": order_data["order_id"],
                    "user_id": order_data["user_id"],
                    "branch": order_data["branch"],
                    "items": json.dumps(order_data["items"]),
                    "total": order_data["total"],
                    "status": order_data["status"],
                    "order_date": order_data["order_date"],
                    "payment_required": str(order_data["payment_required"]),
                    "payment_status": order_data["payment_status"],
                    "updated_at": order_data.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                }
                updated = True
                break
        
        if not updated:
            logger.warning(f"Order {order_id} not found in CSV for update, adding new entry")
            # Add as new entry if not found
            append_to_csv(ORDERS_CSV, {
                "order_id": order_data["order_id"],
                "user_id": order_data["user_id"],
                "branch": order_data["branch"],
                "items": json.dumps(order_data["items"]),
                "total": order_data["total"],
                "status": order_data["status"],
                "order_date": order_data["order_date"],
                "payment_required": str(order_data["payment_required"]),
                "payment_status": order_data["payment_status"],
                "updated_at": order_data.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })
            return True
        
        # Rewrite CSV with updated order
        with open(ORDERS_CSV, 'w', newline='') as f:
            headers = list(orders[0].keys()) if orders else [
                "order_id", "user_id", "branch", "items", "total", "status", 
                "order_date", "payment_required", "payment_status", "updated_at"
            ]
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for order in orders:
                writer.writerow(order)
        
        logger.info(f"Order {order_id} updated in CSV")
        return True
    except Exception as e:
        logger.error(f"Failed to update order in CSV: {str(e)}")
        return False

def send_production_lists():
    """Send production lists to chefs at 7:00 AM using Redis data"""
    logger.info("Sending production lists to chefs from Redis")
    
    # Get orders directly from Redis (primary source)
    orders = redis_state.get_todays_orders()
    
    # Group orders by product category
    production_list = {
        "custard": [],
        "delights": []
    }
    
    for order in orders:
        # Parse items from order
        try:
            for item in order["items"]:
                for category, products in PRODUCT_CATEGORIES.items():
                    if any(product in item['name'].lower() for product in products):
                        production_list[category].append({
                            "name": item['name'],
                            "quantity": item['quantity'],
                            "branch": order['branch']
                        })
        except Exception as e:
            logger.error(f"Error parsing order items for order {order.get('order_id')}: {str(e)}")
    
    # Send to Sochin (custard items)
    if production_list["custard"]:
        message = "🍳 *PRODUCTION LIST - SOCHIN*\n\n"
        for item in production_list["custard"]:
            message += f"• {item['name'].title()} x{item['quantity']} ({item['branch'].title()})\n"
        send_text_message(STAFF_CONTACTS["David"], message)
    
    # Send to Sagar (delights items)
    if production_list["delights"]:
        message = "🍰 *PRODUCTION LIST - SAGAR*\n\n"
        for item in production_list["delights"]:
            message += f"• {item['name'].title()} x{item['quantity']} ({item['branch'].title()})\n"
        send_text_message(STAFF_CONTACTS["David"], message)

def send_daily_delivery_list():
    """Send delivery list to Ashok at 7:00 AM using Redis data"""
    logger.info("Sending delivery list to Ashok from Redis")
    
    # Get orders directly from Redis (primary source)
    orders = redis_state.get_todays_orders()
    
    # Group orders by branch
    delivery_list = {}
    for order in orders:
        branch = order['branch']
        if branch not in delivery_list:
            delivery_list[branch] = []
        
        # Parse items
        try:
            for item in order["items"]:
                delivery_list[branch].append({
                    "name": item['name'],
                    "quantity": item['quantity']
                })
        except Exception as e:
            logger.error(f"Error parsing order items for order {order.get('order_id')}: {str(e)}")
    
    # Format message
    if delivery_list:
        message = "🚚 *DAILY DELIVERY LIST*\n\n"
        for branch, items in delivery_list.items():
            message += f"*{branch.title()}*\n"
            for item in items:
                message += f"• {item['name'].title()} x{item['quantity']}\n"
            message += "\n"
        
        send_text_message(STAFF_CONTACTS["David"], message)
    else:
        logger.info("No orders for delivery today")

def send_daily_reminder_to_branches():
    """Wrapper for sending daily reminder"""
    from services.whatsapp_service import send_daily_reminder
    send_daily_reminder()