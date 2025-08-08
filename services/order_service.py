# services/order_service.py
import uuid
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.logger import get_logger
from utils.csv_utils import append_to_csv, read_csv
from config.settings import ORDERS_CSV, ORDER_STATUS, PAYMENT_BRANCHES, BRANCHES
from stateHandlers.redis_state import redis_state
from services.whatsapp_service import (
    send_order_confirmation,
    notify_supervisor,
    send_payment_link,
    send_text_message
)
import csv

from utils.time_utils import get_current_ist

logger = get_logger("order_service")
IST = ZoneInfo("Asia/Kolkata")

def generate_order_id():
    """Generate a unique order ID"""
    return f"FCT{get_current_ist().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"

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
    
    # Determine initial status
    initial_status = ORDER_STATUS["PAID"] if not payment_required else ORDER_STATUS["PENDING"]
    
    # Prepare order data (with items as list, not JSON string)
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "branch": branch,
        "items": cart["items"],  # Store as Python list
        "total": cart["total"],
        "status": initial_status,
        "order_date": get_current_ist().strftime("%Y-%m-%d %H:%M:%S"),
        "payment_required": payment_required,
        "payment_status": "PAID" if not payment_required else "PENDING"
    }
    
    # Save to Redis FIRST (primary data source)
    if not redis_state.create_order(order_data):
        logger.error(f"Failed to save order {order_id} to Redis")
        return False, "Failed to save order. Please try again."
    
    # Save to CSV as backup
    try:
        # Format for CSV (needs string representation of items)
        csv_order_data = {
            "order_id": order_id,
            "user_id": user_id,
            "branch": branch,
            "items": json.dumps(cart["items"]),
            "total": cart["total"],
            "status": initial_status,
            "order_date": get_current_ist().strftime("%Y-%m-%d %H:%M:%S"),
            "payment_required": str(payment_required),
            "payment_status": "PAID" if not payment_required else "PENDING"
        }
        append_to_csv(ORDERS_CSV, csv_order_data)
        logger.info(f"Order {order_id} saved to CSV as backup")
    except Exception as e:
        logger.error(f"Failed to save order {order_id} to CSV: {str(e)}")
        # Continue since Redis has the order
    
    # Notify supervisor
    notify_supervisor(order_id, branch, cart["items"])
    
    # Clear cart
    redis_state.clear_cart(user_id)
    
    # Handle payment if required
    if payment_required:
        # Send payment link
        send_payment_link(user_id, order_id, cart["total"])
        return True, f"Order #{order_id} placed successfully! Please complete payment to confirm your order."
    else:
        # Send order confirmation WITH ORDER ITEMS
        send_order_confirmation(user_id, order_id, branch, cart["items"], cart["total"])
        return True, f"Order #{order_id} placed successfully! Your order is being processed."

def update_branch_status(branch, status):
    """Update status for all orders of a branch that can be updated to the new status"""
    logger.info(f"Updating status for all {branch} orders to {status}")
    
    # Get all orders
    all_orders = redis_state.redis.lrange("orders:all", 0, -1)
    updated_count = 0
    orders_to_update = []
    
    # Define valid status transitions
    valid_transitions = {
        ORDER_STATUS["READY"]: [ORDER_STATUS["PENDING"], ORDER_STATUS["PAID"]],
        ORDER_STATUS["DELIVERED"]: [ORDER_STATUS["READY"]],
        ORDER_STATUS["COMPLETED"]: [ORDER_STATUS["DELIVERED"]]
    }
    
    # Get valid previous statuses for this transition
    valid_previous_statuses = valid_transitions.get(status, [])
    
    # First pass: identify orders to update
    for order_str in all_orders:
        try:
            # Decode if order_str is bytes
            if isinstance(order_str, bytes):
                order_str = order_str.decode('utf-8')
                
            order = json.loads(order_str)
            
            # Check if this order is for the specified branch and has a valid previous status
            if order["branch"].lower() == branch.lower() and order["status"] in valid_previous_statuses:
                orders_to_update.append((order, order_str))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error processing order: {str(e)}")
            continue
    
    # Second pass: update orders (outside the iteration)
    for order, original_order_str in orders_to_update:
        try:
            # Update the order
            updated_order = {
                **order,
                "status": status,
                "updated_at": get_current_ist().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Update in Redis
            updated_order_json = json.dumps(updated_order, sort_keys=True)
            
            # Remove the old order from main list
            redis_state.redis.lrem("orders:all", 0, original_order_str)
            # Add the updated order to the main list
            redis_state.redis.rpush("orders:all", updated_order_json)
            
            # Remove the old order from branch-specific list
            branch_list_key = f"orders:branch:{order['branch'].lower()}"
            redis_state.redis.lrem(branch_list_key, 0, original_order_str)
            # Add the updated order to the branch-specific list
            redis_state.redis.rpush(branch_list_key, updated_order_json)
            
            # Update in CSV as backup
            try:
                # Format for CSV
                csv_order_data = {
                    "order_id": order["order_id"],
                    "user_id": order["user_id"],
                    "branch": order["branch"],
                    "items": json.dumps(order["items"]),
                    "total": order["total"],
                    "status": status,
                    "order_date": order["order_date"],
                    "payment_required": str(order["payment_required"]),
                    "payment_status": order["payment_status"],
                    "updated_at": get_current_ist().strftime("%Y-%m-%d %H:%M:%S")
                }
                update_order_in_csv(order["order_id"], csv_order_data)
            except Exception as e:
                logger.error(f"Failed to update CSV for order {order['order_id']}: {str(e)}")
            
            # Send notifications
            if status == ORDER_STATUS["READY"]:
                # Notify customer that order is ready
                send_text_message(order["user_id"], f"📦 Your order #{order['order_id']} is ready for delivery!")
            elif status == ORDER_STATUS["DELIVERED"]:
                # Notify customer that order has been delivered
                send_text_message(order["user_id"], f"✅ Your order #{order['order_id']} has been delivered successfully!")
            elif status == ORDER_STATUS["COMPLETED"]:
                # Archive the order
                redis_state.archive_completed_order(order["order_id"])
                logger.info(f"Order {order['order_id']} archived after completion")
            
            updated_count += 1
        except Exception as e:
            logger.error(f"Error updating order {order.get('order_id')}: {str(e)}")
            continue
    
    logger.info(f"Updated {updated_count} orders for branch {branch} to status {status}")
    return updated_count

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
                    "updated_at": order_data.get("updated_at", get_current_ist().strftime("%Y-%m-%d %H:%M:%S"))
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
                "updated_at": order_data.get("updated_at", get_current_ist().strftime("%Y-%m-%d %H:%M:%S"))
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

def confirm_order(whatsapp_number, payment_method, order_id, paid=False):
    """Confirm order after payment"""
    logger.info(f"Confirming order {order_id} for {whatsapp_number}")
    
    # Find the order
    orders = redis_state.redis.lrange("orders:all", 0, -1)
    order = None
    
    for order_str in orders:
        try:
            o = json.loads(order_str)
            if o["order_id"] == order_id:
                order = o
                break
        except json.JSONDecodeError:
            continue
    
    if not order:
        logger.error(f"Order {order_id} not found")
        return False
    
    if paid:
        # Update order status to PAID
        updated_order = {
            **order,
            "status": ORDER_STATUS["PAID"],
            "payment_status": "PAID",
            "updated_at": get_current_ist().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Update in Redis
        order_json = json.dumps(order, sort_keys=True)
        updated_order_json = json.dumps(updated_order, sort_keys=True)
        
        # Remove the old order
        redis_state.redis.lrem("orders:all", 0, order_json)
        # Add the updated order
        redis_state.redis.rpush("orders:all", updated_order_json)
        
        # Update branch-specific list
        branch_list_key = f"orders:branch:{order['branch'].lower()}"
        redis_state.redis.lrem(branch_list_key, 0, order_json)
        redis_state.redis.rpush(branch_list_key, updated_order_json)
        
        # Send order confirmation
        send_order_confirmation(whatsapp_number, order_id, order["branch"], order["items"], order["total"])
        
        # Notify supervisor
        notify_supervisor(order_id, order["branch"], order["items"])
        
        logger.info(f"Order {order_id} confirmed and payment marked as paid")
        return True
    
    logger.warning(f"Order {order_id} confirmation failed - payment not completed")
    return False