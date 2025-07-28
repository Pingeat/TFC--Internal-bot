# # stateHandlers/redis_state.py
# import redis
# import json
# from datetime import datetime, timedelta
# from config.credentials import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
# from utils.logger import log_user_activity

# # Initialize Redis connection
# try:
#     r = redis.Redis(
#         host=REDIS_HOST,
#         port=REDIS_PORT,
#         db=REDIS_DB,
#         password=REDIS_PASSWORD,
#         decode_responses=True
#     )
#     # Test connection
#     r.ping()
#     print("[REDIS] Connected successfully")
# except Exception as e:
#     print(f"[REDIS] Connection error: {e}")

# # def get_user_state(user_id):
# #     """Get current state of user"""
# #     state_key = f"user:{user_id}:state"
# #     state_data = r.get(state_key)
# #     if state_data:
# #         try:
# #             return json.loads(state_data)
# #         except:
# #             return {}
# #     return {
# #         "step": "start",
# #         "branch": None,
# #         "cart": [],
# #         "total": 0,
# #         "order_id": None,
# #         "address": None,
# #         "latitude": None,
# #         "longitude": None,
# #         "last_interaction": datetime.now().isoformat()
# #     }

# def set_user_state(user_id, state):
#     """Set user state"""
#     state_key = f"user:{user_id}:state"
#     state["last_interaction"] = datetime.now().isoformat()
#     r.set(state_key, json.dumps(state))
#     r.expire(state_key, 3600)  # Expire after 1 hour of inactivity
#     log_user_activity(user_id, "state_updated", f"Step: {state.get('step')}")

# def delete_user_state(user_id):
#     """Delete user state"""
#     state_key = f"user:{user_id}:state"
#     r.delete(state_key)
#     log_user_activity(user_id, "state_deleted", "User state cleared")

# def get_user_cart(user_id):
#     """Get user's cart items"""
#     state = get_user_state(user_id)
#     return state.get("cart", [])

# def set_user_cart(user_id, cart, total=0):
#     """Set user's cart items"""
#     state = get_user_state(user_id)
#     state["cart"] = cart
#     state["total"] = total
#     set_user_state(user_id, state)
#     log_user_activity(user_id, "cart_updated", f"Items: {len(cart)}, Total: {total}")

# # def clear_user_cart(user_id):
# #     """Clear user's cart"""
# #     state = get_user_state(user_id)
# #     state["cart"] = []
# #     state["total"] = 0
# #     set_user_state(user_id, state)
# #     log_user_activity(user_id, "cart_cleared", "Cart emptied")

# # def add_to_cart(user_id, item, quantity, price=0):
# #     """Add item to cart"""
# #     state = get_user_state(user_id)
# #     cart = state.get("cart", [])
    
# #     # Check if item already in cart
# #     item_found = False
# #     for cart_item in cart:
# #         if cart_item["item"].lower() == item.lower():
# #             cart_item["quantity"] += quantity
# #             item_found = True
# #             break
    
# #     if not item_found:
# #         cart.append({
# #             "item": item,
# #             "quantity": quantity,
# #             "price": price
# #         })
    
# #     # Calculate total
# #     total = sum(item["quantity"] * item["price"] for item in cart)
    
# #     set_user_cart(user_id, cart, total)
# #     return cart

# # def remove_from_cart(user_id, item_name):
# #     """Remove item from cart"""
# #     state = get_user_state(user_id)
# #     cart = state.get("cart", [])
    
# #     # Filter out the item
# #     new_cart = [item for item in cart if item["item"].lower() != item_name.lower()]
    
# #     # Calculate total
# #     total = sum(item["quantity"] * item["price"] for item in new_cart)
    
# #     set_user_cart(user_id, new_cart, total)
# #     return new_cart

# def get_pending_orders():
#     """Get all pending orders (for today's cycle)"""
#     orders = []
#     for key in r.scan_iter("order:pending:*"):
#         order_data = r.get(key)
#         if order_data:
#             try:
#                 orders.append(json.loads(order_data))
#             except:
#                 continue
#     return orders

# def add_pending_order(order_id, order_data):
#     """Add a pending order to Redis"""
#     order_key = f"order:pending:{order_id}"
#     r.set(order_key, json.dumps(order_data))
#     # Set expiration to 24 hours
#     r.expire(order_key, 86400)
#     log_user_activity(order_data.get("customer_number", "system"), "order_pending", f"Order ID: {order_id}")

# def get_pending_order(order_id):
#     """Get a specific pending order"""
#     order_key = f"order:pending:{order_id}"
#     order_data = r.get(order_key)
#     if order_data:
#         try:
#             return json.loads(order_data)
#         except:
#             return None
#     return None

# def remove_pending_order(order_id):
#     """Remove a pending order from Redis"""
#     order_key = f"order:pending:{order_id}"
#     r.delete(order_key)
#     log_user_activity("system", "order_removed", f"Order ID: {order_id}")

# def get_active_orders():
#     """Get all active orders (for today)"""
#     orders = []
#     for key in r.scan_iter("order:active:*"):
#         order_data = r.get(key)
#         if order_data:
#             try:
#                 orders.append(json.loads(order_data))
#             except:
#                 continue
#     return orders

# def add_active_order(order_id, order_data):
#     """Add an active order to Redis"""
#     order_key = f"order:active:{order_id}"
#     r.set(order_key, json.dumps(order_data))
#     # Set expiration to 7 days
#     r.expire(order_key, 604800)
#     log_user_activity(order_data.get("customer_number", "system"), "order_active", f"Order ID: {order_id}")

# def get_order_status(order_id):
#     """Get order status"""
#     # Check active orders first
#     order_key = f"order:active:{order_id}"
#     order_data = r.get(order_key)
#     if order_data:
#         try:
#             return json.loads(order_data)
#         except:
#             pass
    
#     # Check pending orders
#     order_key = f"order:pending:{order_id}"
#     order_data = r.get(order_key)
#     if order_data:
#         try:
#             return json.loads(order_data)
#         except:
#             pass
    
#     return None

# def update_order_status(order_id, status, notes=None):
#     """Update order status"""
#     # First check if it's a pending order
#     order_key = f"order:pending:{order_id}"
#     order_data = r.get(order_key)
    
#     if order_data:
#         try:
#             order = json.loads(order_data)
#             order["status"] = status
#             if notes:
#                 order["notes"] = notes
#             r.set(order_key, json.dumps(order))
#             return order
#         except:
#             pass
    
#     # If not pending, check active orders   
#     order_key = f"order:active:{order_id}"
#     order_data = r.get(order_key)
    
#     if order_data:
#         try:
#             order = json.loads(order_data)
#             order["status"] = status
#             if notes:
#                 order["notes"] = notes
#             r.set(order_key, json.dumps(order))
#             return order
#         except:
#             pass
    
#     return None

# def get_user_last_order(user_id):
#     """Get user's last order"""
#     order_key = f"user:{user_id}:last_order"
#     order_data = r.get(order_key)
#     if order_data:
#         try:
#             return json.loads(order_data)
#         except:
#             pass
#     return None

# def set_user_last_order(user_id, order_id, order_data):
#     """Set user's last order"""
#     order_key = f"user:{user_id}:last_order"
#     r.set(order_key, json.dumps({
#         "order_id": order_id,
#         "order_data": order_data,
#         "timestamp": datetime.now().isoformat()
#     }))
#     r.expire(order_key, 604800)  # 7 days
#     log_user_activity(user_id, "last_order_updated", f"Order ID: {order_id}")









# def get_user_state(user_id):
#     state["total"] = total
    
#     set_user_state(user_id, state)
#     log_user_activity(user_id, "cart_updated", f"Items: {len(cart)}, Total: {total}")

# def clear_user_cart(user_id):
#     """Clear user's cart"""
#     state = get_user_state(user_id)
#     state["cart"] = []
#     state["total"] = 0
#     set_user_state(user_id, state)
#     log_user_activity(user_id, "cart_cleared", "Cart emptied")

# def add_to_cart(user_id, item, quantity, price=0):
#     """Add item to cart with better validation and logging"""
#     state = get_user_state(user_id)
#     cart = state.get("cart", [])
    
#     # Ensure cart is a list
#     if not isinstance(cart, list):
#         cart = []
#         state["cart"] = cart
    
#     # Check if item already in cart
#     item_found = False
#     for cart_item in cart:
#         if cart_item["item"].lower() == item.lower():
#             log_user_activity(user_id, "cart_update", f"Updating existing item: {item} (quantity: {quantity})")
#             cart_item["quantity"] += quantity
#             item_found = True
#             break
    
#     if not item_found:
#         log_user_activity(user_id, "cart_update", f"Adding new item: {item} x{quantity}")
#         cart.append({
#             "item": item,
#             "quantity": quantity,
#             "price": price
#         })
    
#     # Calculate total
#     total = sum(item["quantity"] * item["price"] for item in cart)
    
#     set_user_cart(user_id, cart, total)
    
#     # Log final cart state
#     cart_items = ", ".join([f"{item['item']} x{item['quantity']}" for item in cart])
#     log_user_activity(user_id, "cart_final", f"Cart after add: {cart_items}, Total: {total}")
    
#     return cart

# def remove_from_cart(user_id, item_name):
#     """Remove item from cart with validation"""
#     state = get_user_state(user_id)
#     cart = state.get("cart", [])
    
#     # Filter out the item
#     new_cart = [item for item in cart if item["item"].lower() != item_name.lower()]
    
#     # Calculate total
#     total = sum(item["quantity"] * item["price"] for item in new_cart)
    
#     set_user_cart(user_id, new_cart, total)
#     return new_cart




# stateHandlers/redis_state.py
import redis
import json
from datetime import datetime, timedelta
from config.credentials import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
from utils.logger import log_user_activity

# Initialize Redis connection
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    # Test connection
    r.ping()
    print("[REDIS] Connected successfully")
except Exception as e:
    print(f"[REDIS] Connection error: {e}")

def get_user_state(user_id):
    """Get current state of user with robust validation and error handling"""
    state_key = f"user:{user_id}:state"
    state_data = r.get(state_key)
    
    # If no state data exists, return a fresh state
    if not state_data:
        fresh_state = {
            "step": "start",
            "branch": None,
            "cart": [],
            "total": 0,
            "order_id": None,
            "address": None,
            "latitude": None,
            "longitude": None,
            "last_interaction": datetime.now().isoformat()
        }
        log_user_activity(user_id, "state_initialized", "New user state created")
        return fresh_state
    
    # Try to parse the state data
    try:
        state = json.loads(state_data)
        
        # Validate and fix cart structure if needed
        if "cart" not in state or not isinstance(state["cart"], list):
            log_user_activity(user_id, "state_warning", "Invalid cart structure detected, resetting cart")
            state["cart"] = []
        
        # Ensure total is calculated correctly
        if "total" not in state or not isinstance(state["total"], (int, float)):
            state["total"] = sum(item["quantity"] * item["price"] for item in state["cart"])
        
        # Reset step if needed
        if "step" not in state:
            state["step"] = "start"
        
        # Update last interaction time
        state["last_interaction"] = datetime.now().isoformat()
        
        # Log for debugging
        cart_items = ", ".join([f"{item['item']} x{item['quantity']}" for item in state["cart"]]) if state["cart"] else "empty"
        log_user_activity(user_id, "state_retrieved", f"Step: {state['step']}, Cart: {cart_items}, Total: {state['total']}")
        
        return state
    except Exception as e:
        log_user_activity(user_id, "state_error", f"Error parsing state: {str(e)}, creating fresh state")
        print(f"[REDIS] Error parsing state for {user_id}: {e}")
        return {
            "step": "start",
            "branch": None,
            "cart": [],
            "total": 0,
            "order_id": None,
            "address": None,
            "latitude": None,
            "longitude": None,
            "last_interaction": datetime.now().isoformat()
        }

def set_user_state(user_id, state):
    """Set user state with validation and error handling"""
    state_key = f"user:{user_id}:state"
    
    # Make sure cart is always a list
    if "cart" not in state or not isinstance(state["cart"], list):
        state["cart"] = []
    
    # Ensure total is calculated correctly
    if "total" not in state or not isinstance(state["total"], (int, float)):
        state["total"] = sum(item["quantity"] * item["price"] for item in state["cart"])
    
    # Update timestamp
    state["last_interaction"] = datetime.now().isoformat()
    
    # Log cart contents for debugging
    cart_items = ", ".join([f"{item['item']} x{item['quantity']}" for item in state["cart"]]) if state["cart"] else "empty"
    log_user_activity(user_id, "state_updated", f"Step: {state.get('step', 'unknown')}, Cart: {cart_items}, Total: {state['total']}")
    
    try:
        r.set(state_key, json.dumps(state))
        r.expire(state_key, 3600)  # Expire after 1 hour of inactivity
    except Exception as e:
        log_user_activity(user_id, "state_error", f"Failed to save state: {str(e)}")
        print(f"[REDIS] Error saving state for {user_id}: {e}")

def delete_user_state(user_id):
    """Delete user state with proper cleanup"""
    state_key = f"user:{user_id}:state"
    try:
        # Get current state for logging
        current_state = get_user_state(user_id)
        cart_items = ", ".join([f"{item['item']} x{item['quantity']}" for item in current_state["cart"]]) if current_state["cart"] else "empty"
        
        # Delete the state
        r.delete(state_key)
        
        # Log the deletion
        log_user_activity(user_id, "state_deleted", f"Cart contents: {cart_items}")
        print(f"[REDIS] State deleted for user {user_id}")
    except Exception as e:
        log_user_activity(user_id, "state_error", f"Failed to delete state: {str(e)}")
        print(f"[REDIS] Error deleting state for {user_id}: {e}")

def get_user_cart(user_id):
    """Get user's cart items with guaranteed valid structure"""
    state = get_user_state(user_id)
    cart = state.get("cart", [])
    
    # Ensure cart is always a list
    if not isinstance(cart, list):
        cart = []
        state["cart"] = cart
        set_user_state(user_id, state)
        log_user_activity(user_id, "cart_warning", "Cart was not a list, reset to empty list")
    
    # Log cart contents
    cart_items = ", ".join([f"{item['item']} x{item['quantity']}" for item in cart]) if cart else "empty"
    log_user_activity(user_id, "cart_retrieved", f"Cart contents: {cart_items}")
    
    return cart

def set_user_cart(user_id, cart, total=0):
    """Set user's cart items with validation and recalculation"""
    # Validate cart structure
    if not isinstance(cart, list):
        log_user_activity(user_id, "cart_error", "Invalid cart structure - not a list")
        cart = []
    
    # Calculate total if not provided
    if total == 0 and cart:
        total = sum(item["quantity"] * item["price"] for item in cart)
    
    state = get_user_state(user_id)
    state["cart"] = cart
    state["total"] = total
    
    set_user_state(user_id, state)
    log_user_activity(user_id, "cart_updated", f"Items: {len(cart)}, Total: {total}")

def clear_user_cart(user_id):
    """Clear user's cart with proper validation"""
    state = get_user_state(user_id)
    state["cart"] = []
    state["total"] = 0
    set_user_state(user_id, state)
    log_user_activity(user_id, "cart_cleared", "Cart emptied")

def add_to_cart(user_id, item, quantity, price=0):
    """Add item to cart with robust validation and logging"""
    state = get_user_state(user_id)
    cart = state.get("cart", [])
    
    # Ensure cart is a list
    if not isinstance(cart, list):
        log_user_activity(user_id, "cart_warning", "Cart was not a list, resetting to empty list")
        cart = []
        state["cart"] = cart
    
    # Validate input
    try:
        quantity = int(quantity)
        if quantity <= 0:
            log_user_activity(user_id, "cart_error", f"Invalid quantity: {quantity}")
            return cart
        price = float(price)
    except (ValueError, TypeError) as e:
        log_user_activity(user_id, "cart_error", f"Invalid input: {str(e)}")
        return cart
    
    # Check if item already in cart
    item_found = False
    for cart_item in cart:
        if cart_item["item"].lower() == item.lower():
            log_user_activity(user_id, "cart_update", f"Updating existing item: {item} (quantity: {quantity})")
            cart_item["quantity"] += quantity
            item_found = True
            break
    
    if not item_found:
        log_user_activity(user_id, "cart_update", f"Adding new item: {item} x{quantity} @ Rs. {price}")
        cart.append({
            "item": item,
            "quantity": quantity,
            "price": price
        })
    
    # Calculate total
    total = sum(item["quantity"] * item["price"] for item in cart)
    
    # Update and save
    set_user_cart(user_id, cart, total)
    
    # Log final cart state
    cart_items = ", ".join([f"{item['item']} x{item['quantity']}" for item in cart])
    log_user_activity(user_id, "cart_final", f"Cart after add: {cart_items}, Total: {total}")
    
    return cart

def remove_from_cart(user_id, item_name):
    """Remove item from cart with validation"""
    state = get_user_state(user_id)
    cart = state.get("cart", [])
    
    # Ensure cart is a list
    if not isinstance(cart, list):
        cart = []
        state["cart"] = cart
    
    # Filter out the item (case-insensitive)
    new_cart = [item for item in cart if item["item"].lower() != item_name.lower()]
    
    # Calculate total
    total = sum(item["quantity"] * item["price"] for item in new_cart)
    
    set_user_cart(user_id, new_cart, total)
    
    # Log the removal
    if len(cart) > len(new_cart):
        log_user_activity(user_id, "cart_removed", f"Removed {item_name} from cart")
    else:
        log_user_activity(user_id, "cart_warning", f"Item {item_name} not found in cart")
    
    return new_cart

def get_pending_orders():
    """Get all pending orders (for today's cycle)"""
    orders = []
    try:
        for key in r.scan_iter("order:pending:*"):
            order_data = r.get(key)
            if order_data:
                try:
                    orders.append(json.loads(order_data))
                except Exception as e:
                    log_user_activity("system", "order_error", f"Error parsing pending order {key}: {str(e)}")
        return orders
    except Exception as e:
        log_user_activity("system", "redis_error", f"Error getting pending orders: {str(e)}")
        return []

def add_pending_order(order_id, order_data):
    """Add a pending order to Redis"""
    order_key = f"order:pending:{order_id}"
    try:
        r.set(order_key, json.dumps(order_data))
        r.expire(order_key, 86400)  # Set expiration to 24 hours
        log_user_activity(order_data.get("customer_number", "system"), "order_pending", f"Order ID: {order_id}")
        print(f"[REDIS] Added pending order: {order_id}")
    except Exception as e:
        log_user_activity("system", "order_error", f"Failed to add pending order {order_id}: {str(e)}")
        print(f"[REDIS] Error adding pending order {order_id}: {e}")

def get_pending_order(order_id):
    """Get a specific pending order"""
    order_key = f"order:pending:{order_id}"
    try:
        order_data = r.get(order_key)
        if order_data:
            return json.loads(order_data)
        return None
    except Exception as e:
        log_user_activity("system", "order_error", f"Error getting pending order {order_id}: {str(e)}")
        return None

def remove_pending_order(order_id):
    """Remove a pending order from Redis"""
    order_key = f"order:pending:{order_id}"
    try:
        r.delete(order_key)
        log_user_activity("system", "order_removed", f"Order ID: {order_id}")
        print(f"[REDIS] Removed pending order: {order_id}")
    except Exception as e:
        log_user_activity("system", "order_error", f"Failed to remove pending order {order_id}: {str(e)}")

def get_active_orders():
    """Get all active orders (for today)"""
    orders = []
    try:
        for key in r.scan_iter("order:active:*"):
            order_data = r.get(key)
            if order_data:
                try:
                    orders.append(json.loads(order_data))
                except Exception as e:
                    log_user_activity("system", "order_error", f"Error parsing active order {key}: {str(e)}")
        return orders
    except Exception as e:
        log_user_activity("system", "redis_error", f"Error getting active orders: {str(e)}")
        return []

def add_active_order(order_id, order_data):
    """Add an active order to Redis"""
    order_key = f"order:active:{order_id}"
    try:
        r.set(order_key, json.dumps(order_data))
        r.expire(order_key, 604800)  # Set expiration to 7 days
        log_user_activity(order_data.get("customer_number", "system"), "order_active", f"Order ID: {order_id}")
        print(f"[REDIS] Added active order: {order_id}")
    except Exception as e:
        log_user_activity("system", "order_error", f"Failed to add active order {order_id}: {str(e)}")
        print(f"[REDIS] Error adding active order {order_id}: {e}")

def get_order_status(order_id):
    """Get order status with fallback to pending orders"""
    # Check active orders first
    order_key = f"order:active:{order_id}"
    try:
        order_data = r.get(order_key)
        if order_data:
            return json.loads(order_data)
    except Exception as e:
        log_user_activity("system", "order_error", f"Error parsing active order {order_id}: {str(e)}")
    
    # Check pending orders
    order_key = f"order:pending:{order_id}"
    try:
        order_data = r.get(order_key)
        if order_data:
            return json.loads(order_data)
    except Exception as e:
        log_user_activity("system", "order_error", f"Error parsing pending order {order_id}: {str(e)}")
    
    log_user_activity("system", "order_not_found", f"Order ID: {order_id} not found")
    return None

def update_order_status(order_id, status, notes=None):
    """Update order status with proper error handling"""
    # First check if it's a pending order
    order_key = f"order:pending:{order_id}"
    order_data = r.get(order_key)
    
    if order_data:
        try:
            order = json.loads(order_data)
            order["status"] = status
            if notes:
                order["notes"] = notes
            r.set(order_key, json.dumps(order))
            log_user_activity("system", "order_status_updated", f"Order ID: {order_id}, Status: {status}")
            return order
        except Exception as e:
            log_user_activity("system", "order_error", f"Error updating pending order {order_id}: {str(e)}")
    
    # If not pending, check active orders
    order_key = f"order:active:{order_id}"
    order_data = r.get(order_key)
    
    if order_data:
        try:
            order = json.loads(order_data)
            order["status"] = status
            if notes:
                order["notes"] = notes
            r.set(order_key, json.dumps(order))
            log_user_activity("system", "order_status_updated", f"Order ID: {order_id}, Status: {status}")
            return order
        except Exception as e:
            log_user_activity("system", "order_error", f"Error updating active order {order_id}: {str(e)}")
    
    log_user_activity("system", "order_not_found", f"Order ID: {order_id} not found for status update")
    return None

def get_user_last_order(user_id):
    """Get user's last order with error handling"""
    order_key = f"user:{user_id}:last_order"
    try:
        order_data = r.get(order_key)
        if order_data:
            return json.loads(order_data)
        return None
    except Exception as e:
        log_user_activity(user_id, "order_error", f"Error getting last order: {str(e)}")
        return None

def set_user_last_order(user_id, order_id, order_data):
    """Set user's last order with proper logging"""
    order_key = f"user:{user_id}:last_order"
    try:
        r.set(order_key, json.dumps({
            "order_id": order_id,
            "order_data": order_data,
            "timestamp": datetime.now().isoformat()
        }))
        r.expire(order_key, 604800)  # 7 days
        log_user_activity(user_id, "last_order_updated", f"Order ID: {order_id}")
        print(f"[REDIS] Set last order for user {user_id}: {order_id}")
    except Exception as e:
        log_user_activity(user_id, "order_error", f"Failed to set last order {order_id}: {str(e)}")
        print(f"[REDIS] Error setting last order for {user_id}: {e}")