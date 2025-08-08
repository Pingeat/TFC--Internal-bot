# # stateHandlers/redis_state.py
# import traceback
# import redis
# import json
# from config.credentials import REDIS_URL
# from config.settings import ORDER_STATUS
# from utils.logger import get_logger
# from datetime import datetime, timedelta, time

# logger = get_logger("redis_state")

# class RedisState:
#     def __init__(self):
#         try:
#             self.redis = redis.from_url(REDIS_URL)
#             self.redis.ping()
#             logger.info("Connected to Redis successfully")
#         except Exception as e:
#             logger.error(f"Failed to connect to Redis: {str(e)}")
#             raise

#     def get_user_state(self, user_id):
#         """Get user state from Redis"""
#         try:
#             state = self.redis.get(f"user:{user_id}:state")
#             if state:
#                 return json.loads(state)
#             return None
#         except Exception as e:
#             logger.error(f"Error getting user state for {user_id}: {str(e)}")
#             return None

#     def set_user_state(self, user_id, state):
#         """Set user state in Redis"""
#         try:
#             # Add timestamp for debugging
#             state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             self.redis.setex(f"user:{user_id}:state", 3600, json.dumps(state))  # 1 hour expiry
#             logger.debug(f"Set user state for {user_id}: {state}")
#             return True
#         except Exception as e:
#             logger.error(f"Error setting user state for {user_id}: {str(e)}")
#             return False

#     def clear_user_state(self, user_id):
#         """Clear user state from Redis"""
#         try:
#             self.redis.delete(f"user:{user_id}:state")
#             logger.debug(f"Cleared user state for {user_id}")
#             return True
#         except Exception as e:
#             logger.error(f"Error clearing user state for {user_id}: {str(e)}")
#             return False

#     def get_cart(self, user_id):
#         """Get user's cart from Redis"""
#         try:
#             cart = self.redis.get(f"user:{user_id}:cart")
#             if cart:
#                 cart_data = json.loads(cart)
#                 # Validate cart structure
#                 if "items" not in cart_data:
#                     cart_data["items"] = []
#                 if "branch" not in cart_data:
#                     cart_data["branch"] = None
#                 if "total" not in cart_data:
#                     cart_data["total"] = 0
#                 return cart_data
#             return {"items": [], "branch": None, "total": 0}
#         except Exception as e:
#             logger.error(f"Error getting cart for {user_id}: {str(e)}")
#             return {"items": [], "branch": None, "total": 0}

#     def add_to_cart(self, user_id, item, quantity, price=0):
#         """Add item to user's cart"""
#         try:
#             cart = self.get_cart(user_id)
            
#             # Validate branch is set
#             if not cart["branch"]:
#                 logger.warning(f"Attempt to add item to cart without branch for user {user_id}")
#                 return cart
            
#             # Check if item already in cart
#             item_found = False
#             for cart_item in cart["items"]:
#                 if cart_item["name"].lower() == item.lower():
#                     cart_item["quantity"] += quantity
#                     item_found = True
#                     break
            
#             if not item_found:
#                 cart["items"].append({
#                     "name": item,
#                     "quantity": quantity,
#                     "price": price
#                 })
            
#             # Update total
#             cart["total"] = sum(item["quantity"] * item["price"] for item in cart["items"])
            
#             # Set expiry to 2 hours (longer for ordering window)
#             self.redis.setex(f"user:{user_id}:cart", 7200, json.dumps(cart))
#             logger.debug(f"Added {quantity}x {item} to cart for {user_id}. Branch: {cart['branch']}")
#             return cart
#         except Exception as e:
#             logger.error(f"Error adding to cart for {user_id}: {str(e)}")
#             return self.get_cart(user_id)

#     def clear_cart(self, user_id):
#         """Clear user's cart"""
#         try:
#             self.redis.delete(f"user:{user_id}:cart")
#             logger.debug(f"Cleared cart for {user_id}")
#             return True
#         except Exception as e:
#             logger.error(f"Error clearing cart for {user_id}: {str(e)}")
#             return False

#     def set_branch(self, user_id, branch):
#         """Set user's selected branch with validation"""
#         try:
#             from config.settings import BRANCHES
            
#             # Validate branch
#             valid_branch = None
#             for b in BRANCHES:
#                 if b.lower() == branch.lower():
#                     valid_branch = b
#                     break
            
#             if not valid_branch:
#                 logger.error(f"Invalid branch selected by {user_id}: {branch}")
#                 return False
            
#             cart = self.get_cart(user_id)
#             cart["branch"] = valid_branch
#             self.redis.setex(f"user:{user_id}:cart", 7200, json.dumps(cart))
            
#             # Log branch selection
#             logger.info(f"Branch set for {user_id}: {valid_branch}")
#             return True
#         except Exception as e:
#             logger.error(f"Error setting branch for {user_id}: {str(e)}")
#             return False


#     def get_orders_by_branch(self, branch):
#         """Get all orders for a specific branch"""
#         try:
#             branch_orders = []
#             branch_key = f"orders:branch:{branch.lower()}"
            
#             # Get orders from branch-specific list
#             orders_str = self.redis.lrange(branch_key, 0, -1)
#             for order_str in orders_str:
#                 order = json.loads(order_str)
#                 # Only include today's orders
#                 order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
#                 if order_date.date() == datetime.now().date():
#                     branch_orders.append(order)
            
#             logger.info(f"Retrieved {len(branch_orders)} orders from Redis for branch {branch}")
#             return branch_orders
#         except Exception as e:
#             logger.error(f"Error getting orders for branch {branch}: {str(e)}")
#             return []
    
#     def create_order(self, order_data):
#         """Create a new order in Redis as primary data source"""
#         try:
#             # Add to main orders list
#             self.redis.rpush("orders:all", json.dumps(order_data))
#             # Add to branch-specific list
#             self.redis.rpush(f"orders:branch:{order_data['branch'].lower()}", json.dumps(order_data))
#             # Set as active for today
#             self.redis.setex(f"order:{order_data['order_id']}:active", 86400, "1")  # 24 hours
#             logger.info(f"Order {order_data['order_id']} created in Redis")
#             return True
#         except Exception as e:
#             logger.error(f"Error creating order in Redis: {str(e)}")
#             return False

#     def update_order(self, order_data):
#         """Update an existing order in Redis"""
#         try:
#             # Remove old order
#             old_order_json = json.dumps({"order_id": order_data["order_id"]}, sort_keys=True)
#             self.redis.lrem("orders:all", 0, old_order_json)
        
#             # Add updated order
#             self.redis.rpush("orders:all", json.dumps(order_data))
        
#             # Update branch-specific list
#             branch_list_key = f"orders:branch:{order_data['branch'].lower()}"
#             self.redis.lrem(branch_list_key, 0, old_order_json)
#             self.redis.rpush(branch_list_key, json.dumps(order_data))
        
#             logger.info(f"Order {order_data['order_id']} updated in Redis")
#             return True
#         except Exception as e:
#             logger.error(f"Error updating order in Redis: {str(e)}")
#             return False
    
#     # def get_todays_orders(self):
#     #     """Get all orders from 7:00 AM today to 7:00 AM tomorrow"""
#     #     try:
#     #         orders = []
#     #         all_orders = self.redis.lrange("orders:all", 0, -1)
        
#     #         # Define cutoff time (7:00 AM)
#     #         cutoff_hour = 7  # 7:00 AM
        
#     #         for order_str in all_orders:
#     #             try:
#     #                 order = json.loads(order_str)
#     #                 order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
                
#     #                 # Get current datetime
#     #                 now = datetime.now()
                
#     #                 # Calculate the reference date based on cutoff time
#     #                 if now.hour < cutoff_hour:
#     #                     # If current time is before 7:00 AM, reference date is yesterday
#     #                     reference_date = now.date() - timedelta(days=1)
#     #                 else:
#     #                     # If current time is 7:00 AM or later, reference date is today
#     #                     reference_date = now.date()
                
#     #                 # Create a datetime object for the cutoff time of the reference date
#     #                 cutoff_datetime = datetime.combine(reference_date, time(hour=cutoff_hour))
                
#     #                 # Check if order is within the current cycle (from cutoff_datetime to cutoff_datetime + 24 hours)
#     #                 if cutoff_datetime <= order_date < cutoff_datetime + timedelta(hours=24):
#     #                     orders.append(order)
#     #             except (json.JSONDecodeError, KeyError, ValueError) as e:
#     #                 logger.error(f"Error parsing order: {str(e)}")
#     #                 continue
                
#     #         logger.info(f"Retrieved {len(orders)} orders from Redis for the current cycle")
#     #         return orders
#     #     except Exception as e:
#     #         logger.error(f"Error getting today's orders from Redis: {str(e)}")
#     #         return []
    
#     # def archive_completed_order(self, order_id):
#     #     """Move completed order to archive and remove from active lists"""
#     #     try:
#     #         # Find the order
#     #         order = None
#     #         all_orders = self.redis.lrange("orders:all", 0, -1)
        
#     #         for i, order_str in enumerate(all_orders):
#     #             try:
#     #                 o = json.loads(order_str)
#     #                 if o["order_id"] == order_id:
#     #                     order = o
#     #                     break
#     #             except json.JSONDecodeError:
#     #                 continue
        
#     #         if not order:
#     #             logger.warning(f"Order {order_id} not found for archiving")
#     #             return False
        
#     #         # Add to archive
#     #         self.redis.rpush("orders:archive", json.dumps(order))
        
#     #         # Remove from active lists
#     #         self.redis.lrem("orders:all", 0, json.dumps(order, sort_keys=True))
#     #         self.redis.lrem(f"orders:branch:{order['branch'].lower()}", 0, json.dumps(order, sort_keys=True))
        
#     #         logger.info(f"Order {order_id} archived successfully")
#     #         return True
#     #     except Exception as e:
#     #         logger.error(f"Error archiving order {order_id}: {str(e)}")
#     #         return False
    
#     def get_todays_orders(self):
#         """Get all orders from 7:00 AM today to 7:00 AM tomorrow"""
#         try:
#             orders = []
#             all_orders = self.redis.lrange("orders:all", 0, -1)
        
#             # Define cutoff time (7:00 AM)
#             cutoff_hour = 7  # 7:00 AM
        
#             for order_str in all_orders:
#                 try:
#                     order = json.loads(order_str)
#                     order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
                
#                     # Get current datetime
#                     now = datetime.now()
                
#                     # Calculate the reference date based on cutoff time
#                     if now.hour < cutoff_hour:
#                         # If current time is before 7:00 AM, reference date is yesterday
#                         reference_date = now.date() - timedelta(days=1)
#                     else:
#                         # If current time is 7:00 AM or later, reference date is today
#                         reference_date = now.date()
                
#                     # Create a datetime object for the cutoff time of the reference date
#                     cutoff_datetime = datetime.combine(reference_date, time(hour=cutoff_hour))
                
#                     # Check if order is within the current cycle (from cutoff_datetime to cutoff_datetime + 24 hours)
#                     if cutoff_datetime <= order_date < cutoff_datetime + timedelta(hours=24):
#                         orders.append(order)
#                 except (json.JSONDecodeError, KeyError, ValueError) as e:
#                     logger.error(f"Error parsing order: {str(e)}")
#                     continue
                
#             logger.info(f"Retrieved {len(orders)} orders from Redis for the current cycle")
#             return orders
#         except Exception as e:
#             logger.error(f"Error getting today's orders from Redis: {str(e)}")
#             return []
            
#     def archive_completed_order(self, order_id):
#         """Move completed order to archive and remove from active lists"""
#         try:
#             # LOCAL IMPORT TO AVOID CIRCULAR DEPENDENCY
#             from services.order_service import update_order_status
            
#             # Find the order
#             order = None
#             all_orders = self.redis.lrange("orders:all", 0, -1)
            
#             for i, order_str in enumerate(all_orders):
#                 try:
#                     o = json.loads(order_str)
#                     if o["order_id"] == order_id:
#                         order = o
#                         break
#                 except json.JSONDecodeError:
#                     continue
            
#             if not order:
#                 logger.warning(f"Order {order_id} not found for archiving")
#                 return False
            
#             # Add to archive
#             self.redis.rpush("orders:archive", json.dumps(order))
            
#             # Remove from active lists
#             self.redis.lrem("orders:all", 0, json.dumps(order, sort_keys=True))
#             self.redis.lrem(f"orders:branch:{order['branch'].lower()}", 0, json.dumps(order, sort_keys=True))
            
#             logger.info(f"Order {order_id} archived successfully")
#             return True
#         except Exception as e:
#             logger.error(f"Error archiving order {order_id}: {str(e)}\n{traceback.format_exc()}")
#             return False

# def mark_order_delivered(self, order_id):
#     """Mark an order as delivered and remove from ready list"""
#     try:
#         # LOCAL IMPORT TO AVOID CIRCULAR DEPENDENCY
#         from services.order_service import update_order_status
        
#         # Update order status
#         success = update_order_status(order_id, ORDER_STATUS["DELIVERED"])
#         if success:
#             logger.info(f"Marked order {order_id} as delivered")
#             return True
#         else:
#             logger.error(f"Failed to mark order {order_id} as delivered")
#             return False
#     except Exception as e:
#         logger.error(f"Error marking order {order_id} as delivered: {str(e)}")
#         return False

# def clear_ready_for_branch(self, branch):
#     """Clear all ready items for a branch after delivery confirmation"""
#     try:
#         # This would be called after delivery is confirmed for a branch
#         logger.info(f"Cleared ready items for branch {branch}")
#         return True
#     except Exception as e:
#         logger.error(f"Error clearing ready items for branch {branch}: {str(e)}")
#         return False

# # Initialize Redis state handler
# redis_state = RedisState()











# # stateHandlers/redis_state.py
# import redis
# import json
# from config.credentials import REDIS_URL
# from utils.logger import get_logger
# from datetime import datetime, timedelta, time

# logger = get_logger("redis_state")

# class RedisState:
#     def __init__(self):
#         try:
#             self.redis = redis.from_url(REDIS_URL)
#             self.redis.ping()
#             logger.info("Connected to Redis successfully")
#         except Exception as e:
#             logger.error(f"Failed to connect to Redis: {str(e)}")
#             raise

#     def get_user_state(self, user_id):
#         """Get user state from Redis"""
#         try:
#             state = self.redis.get(f"user:{user_id}:state")
#             if state:
#                 return json.loads(state)
#             return None
#         except Exception as e:
#             logger.error(f"Error getting user state for {user_id}: {str(e)}")
#             return None

#     def set_user_state(self, user_id, state):
#         """Set user state in Redis"""
#         try:
#             # Add timestamp for debugging
#             state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             self.redis.setex(f"user:{user_id}:state", 3600, json.dumps(state))  # 1 hour expiry
#             logger.debug(f"Set user state for {user_id}: {state}")
#             return True
#         except Exception as e:
#             logger.error(f"Error setting user state for {user_id}: {str(e)}")
#             return False

#     def clear_user_state(self, user_id):
#         """Clear user state from Redis"""
#         try:
#             self.redis.delete(f"user:{user_id}:state")
#             logger.debug(f"Cleared user state for {user_id}")
#             return True
#         except Exception as e:
#             logger.error(f"Error clearing user state for {user_id}: {str(e)}")
#             return False

#     def get_cart(self, user_id):
#         """Get user's cart from Redis"""
#         try:
#             cart = self.redis.get(f"user:{user_id}:cart")
#             if cart:
#                 cart_data = json.loads(cart)
#                 # Validate cart structure
#                 if "items" not in cart:
#                     cart_data["items"] = []
#                 if "branch" not in cart:
#                     cart_data["branch"] = None
#                 if "total" not in cart:
#                     cart_data["total"] = 0
#                 return cart_data
#             return {"items": [], "branch": None, "total": 0}
#         except Exception as e:
#             logger.error(f"Error getting cart for {user_id}: {str(e)}")
#             return {"items": [], "branch": None, "total": 0}

#     def add_to_cart(self, user_id, item, quantity, price=0):
#         """Add item to user's cart"""
#         try:
#             cart = self.get_cart(user_id)
            
#             # Validate branch is set
#             if not cart["branch"]:
#                 logger.warning(f"Attempt to add item to cart without branch for user {user_id}")
#                 return cart
            
#             # Check if item already in cart
#             item_found = False
#             for cart_item in cart["items"]:
#                 if cart_item["name"].lower() == item.lower():
#                     cart_item["quantity"] += quantity
#                     item_found = True
#                     break
            
#             if not item_found:
#                 cart["items"].append({
#                     "name": item,
#                     "quantity": quantity,
#                     "price": price
#                 })
            
#             # Update total
#             cart["total"] = sum(item["quantity"] * item["price"] for item in cart["items"])
            
#             # Set expiry to 2 hours (longer for ordering window)
#             self.redis.setex(f"user:{user_id}:cart", 7200, json.dumps(cart))
#             logger.debug(f"Added {quantity}x {item} to cart for {user_id}. Branch: {cart['branch']}")
#             return cart
#         except Exception as e:
#             logger.error(f"Error adding to cart for {user_id}: {str(e)}")
#             return self.get_cart(user_id)

#     def clear_cart(self, user_id):
#         """Clear user's cart"""
#         try:
#             self.redis.delete(f"user:{user_id}:cart")
#             logger.debug(f"Cleared cart for {user_id}")
#             return True
#         except Exception as e:
#             logger.error(f"Error clearing cart for {user_id}: {str(e)}")
#             return False

#     def set_branch(self, user_id, branch):
#         """Set user's selected branch with validation"""
#         try:
#             from config.settings import BRANCHES
            
#             # Validate branch
#             valid_branch = None
#             for b in BRANCHES:
#                 if b.lower() == branch.lower():
#                     valid_branch = b
#                     break
            
#             if not valid_branch:
#                 logger.error(f"Invalid branch selected by {user_id}: {branch}")
#                 return False
            
#             cart = self.get_cart(user_id)
#             cart["branch"] = valid_branch
#             self.redis.setex(f"user:{user_id}:cart", 7200, json.dumps(cart))
            
#             # Log branch selection
#             logger.info(f"Branch set for {user_id}: {valid_branch}")
#             return True
#         except Exception as e:
#             logger.error(f"Error setting branch for {user_id}: {str(e)}")
#             return False

#     def create_order(self, order_data):
#         """Create a new order in Redis as primary data source"""
#         try:
#             # Add to main orders list
#             self.redis.rpush("orders:all", json.dumps(order_data))
#             # Add to branch-specific list
#             self.redis.rpush(f"orders:branch:{order_data['branch'].lower()}", json.dumps(order_data))
#             # Set as active for today
#             self.redis.setex(f"order:{order_data['order_id']}:active", 86400, "1")  # 24 hours
#             logger.info(f"Order {order_data['order_id']} created in Redis")
#             return True
#         except Exception as e:
#             logger.error(f"Error creating order in Redis: {str(e)}")
#             return False

#     def get_todays_orders(self):
#         """Get all orders from 7:00 AM today to 7:00 AM tomorrow"""
#         try:
#             orders = []
#             all_orders = self.redis.lrange("orders:all", 0, -1)
        
#             # Define cutoff time (7:00 AM)
#             cutoff_hour = 7  # 7:00 AM
        
#             for order_str in all_orders:
#                 try:
#                     order = json.loads(order_str)
#                     order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
                
#                     # Get current datetime
#                     now = datetime.now()
                
#                     # Calculate the reference date based on cutoff time
#                     if now.hour < cutoff_hour:
#                         # If current time is before 7:00 AM, reference date is yesterday
#                         reference_date = now.date() - timedelta(days=1)
#                     else:
#                         # If current time is 7:00 AM or later, reference date is today
#                         reference_date = now.date()
                
#                     # Create a datetime object for the cutoff time of the reference date
#                     cutoff_datetime = datetime.combine(reference_date, time(hour=cutoff_hour))
                
#                     # Check if order is within the current cycle (from cutoff_datetime to cutoff_datetime + 24 hours)
#                     if cutoff_datetime <= order_date < cutoff_datetime + timedelta(hours=24):
#                         orders.append(order)
#                 except (json.JSONDecodeError, KeyError, ValueError) as e:
#                     logger.error(f"Error parsing order: {str(e)}")
#                     continue
                
#             logger.info(f"Retrieved {len(orders)} orders from Redis for the current cycle")
#             return orders
#         except Exception as e:
#             logger.error(f"Error getting today's orders from Redis: {str(e)}")
#             return []

#     def archive_completed_order(self, order_id):
#         """Move completed order to archive and remove from active lists"""
#         try:
#             # Find the order
#             order = None
#             all_orders = self.redis.lrange("orders:all", 0, -1)
            
#             for i, order_str in enumerate(all_orders):
#                 try:
#                     o = json.loads(order_str)
#                     if o["order_id"] == order_id:
#                         order = o
#                         break
#                 except json.JSONDecodeError:
#                     continue
            
#             if not order:
#                 logger.warning(f"Order {order_id} not found for archiving")
#                 return False
            
#             # Add to archive
#             self.redis.rpush("orders:archive", json.dumps(order))
            
#             # Remove from active lists
#             self.redis.lrem("orders:all", 0, json.dumps(order, sort_keys=True))
#             self.redis.lrem(f"orders:branch:{order['branch'].lower()}", 0, json.dumps(order, sort_keys=True))
            
#             logger.info(f"Order {order_id} archived successfully")
#             return True
#         except Exception as e:
#             logger.error(f"Error archiving order {order_id}: {str(e)}")
#             return False

# # Initialize Redis state handler
# redis_state = RedisState()








# stateHandlers/redis_state.py
from zoneinfo import ZoneInfo
import redis
import json
from config.credentials import REDIS_URL
from utils.logger import get_logger
from datetime import datetime, timedelta, time

from utils.time_utils import get_current_ist

logger = get_logger("redis_state")
IST = ZoneInfo("Asia/Kolkata")
class RedisState:
    def __init__(self):
        try:
            self.redis = redis.from_url(REDIS_URL)
            self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    def get_user_state(self, user_id):
        """Get user state from Redis with proper byte handling"""
        try:
            state = self.redis.get(f"user:{user_id}:state")
            if state:
                # Decode if state is bytes
                if isinstance(state, bytes):
                    state = state.decode('utf-8')
                return json.loads(state)
            return None
        except Exception as e:
            logger.error(f"Error getting user state for {user_id}: {str(e)}")
            return None

    def set_user_state(self, user_id, state):
        """Set user state in Redis"""
        try:
            # Add timestamp for debugging
            state["last_updated"] = get_current_ist().strftime("%Y-%m-%d %H:%M:%S")
            self.redis.setex(f"user:{user_id}:state", 3600, json.dumps(state))  # 1 hour expiry
            logger.debug(f"Set user state for {user_id}: {state}")
            return True
        except Exception as e:
            logger.error(f"Error setting user state for {user_id}: {str(e)}")
            return False

    def clear_user_state(self, user_id):
        """Clear user state from Redis"""
        try:
            self.redis.delete(f"user:{user_id}:state")
            logger.debug(f"Cleared user state for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing user state for {user_id}: {str(e)}")
            return False

    def get_cart(self, user_id):
        """Get user's cart from Redis with proper byte handling"""
        try:
            cart = self.redis.get(f"user:{user_id}:cart")
            if cart:
                # Decode if cart is bytes
                if isinstance(cart, bytes):
                    cart = cart.decode('utf-8')
                cart_data = json.loads(cart)
                # Validate cart structure
                if "items" not in cart_data:
                    cart_data["items"] = []
                if "branch" not in cart_data:
                    cart_data["branch"] = None
                if "total" not in cart_data:
                    cart_data["total"] = 0
                return cart_data
            return {"items": [], "branch": None, "total": 0}
        except Exception as e:
            logger.error(f"Error getting cart for {user_id}: {str(e)}")
            return {"items": [], "branch": None, "total": 0}

    def add_to_cart(self, user_id, item, quantity, price=0):
        """Add item to user's cart"""
        try:
            cart = self.get_cart(user_id)
            
            # Validate branch is set
            if not cart["branch"]:
                logger.warning(f"Attempt to add item to cart without branch for user {user_id}")
                return cart
            
            # Check if item already in cart
            item_found = False
            for cart_item in cart["items"]:
                if cart_item["name"].lower() == item.lower():
                    cart_item["quantity"] += quantity
                    item_found = True
                    break
            
            if not item_found:
                cart["items"].append({
                    "name": item,
                    "quantity": quantity,
                    "price": price
                })
            
            # Update total
            cart["total"] = sum(item["quantity"] * item["price"] for item in cart["items"])
            
            # Set expiry to 2 hours (longer for ordering window)
            self.redis.setex(f"user:{user_id}:cart", 7200, json.dumps(cart))
            logger.debug(f"Added {quantity}x {item} to cart for {user_id}. Branch: {cart['branch']}")
            return cart
        except Exception as e:
            logger.error(f"Error adding to cart for {user_id}: {str(e)}")
            return self.get_cart(user_id)

    def clear_cart(self, user_id):
        """Clear user's cart"""
        try:
            self.redis.delete(f"user:{user_id}:cart")
            logger.debug(f"Cleared cart for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing cart for {user_id}: {str(e)}")
            return False

    def set_branch(self, user_id, branch):
        """Set user's selected branch with validation"""
        try:
            from config.settings import BRANCHES
            
            # Validate branch
            valid_branch = None
            for b in BRANCHES:
                if b.lower() == branch.lower():
                    valid_branch = b
                    break
            
            if not valid_branch:
                logger.error(f"Invalid branch selected by {user_id}: {branch}")
                return False
            
            cart = self.get_cart(user_id)
            cart["branch"] = valid_branch
            self.redis.setex(f"user:{user_id}:cart", 7200, json.dumps(cart))
            
            # Log branch selection
            logger.info(f"Branch set for {user_id}: {valid_branch}")
            return True
        except Exception as e:
            logger.error(f"Error setting branch for {user_id}: {str(e)}")
            return False

    def create_order(self, order_data):
        """Create a new order in Redis as primary data source"""
        try:
            # Add to main orders list
            self.redis.rpush("orders:all", json.dumps(order_data))
            # Add to branch-specific list
            self.redis.rpush(f"orders:branch:{order_data['branch'].lower()}", json.dumps(order_data))
            # Set as active for today
            self.redis.setex(f"order:{order_data['order_id']}:active", 86400, "1")  # 24 hours
            logger.info(f"Order {order_data['order_id']} created in Redis")
            return True
        except Exception as e:
            logger.error(f"Error creating order in Redis: {str(e)}")
            return False

    # def get_todays_orders(self):
    #     """Get all orders from 7:00 AM today to 7:00 AM tomorrow"""
    #     try:
    #         orders = []
    #         all_orders = self.redis.lrange("orders:all", 0, -1)
        
    #         # Define cutoff time (7:00 AM)
    #         cutoff_hour = 7  # 7:00 AM
        
    #         for order_str in all_orders:
    #             try:
    #                 # Decode if order_str is bytes
    #                 if isinstance(order_str, bytes):
    #                     order_str = order_str.decode('utf-8')
                    
    #                 order = json.loads(order_str)
    #                 order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
                
    #                 # Get current datetime
    #                 now = datetime.now()
                
    #                 # Calculate the reference date based on cutoff time
    #                 if now.hour < cutoff_hour:
    #                     # If current time is before 7:00 AM, reference date is yesterday
    #                     reference_date = now.date() - timedelta(days=1)
    #                 else:
    #                     # If current time is 7:00 AM or later, reference date is today
    #                     reference_date = now.date()
                
    #                 # Create a datetime object for the cutoff time of the reference date
    #                 cutoff_datetime = datetime.combine(reference_date, time(hour=cutoff_hour))
                
    #                 # Check if order is within the current cycle (from cutoff_datetime to cutoff_datetime + 24 hours)
    #                 if cutoff_datetime <= order_date < cutoff_datetime + timedelta(hours=24):
    #                     orders.append(order)
    #             except (json.JSONDecodeError, KeyError, ValueError) as e:
    #                 logger.error(f"Error parsing order: {str(e)}")
    #                 continue
                
    #         logger.info(f"Retrieved {len(orders)} orders from Redis for the current cycle")
    #         return orders
    #     except Exception as e:
    #         logger.error(f"Error getting today's orders from Redis: {str(e)}")
    #         return []
    
    def get_todays_orders(self):
        """Get all orders from 7:00 AM today to 7:00 AM tomorrow"""
        try:
            orders = []
            all_orders = self.redis.lrange("orders:all", 0, -1)
    
            # Define cutoff time (7:00 AM)
            cutoff_hour = 7  # 7:00 AM
    
            for order_str in all_orders:
                try:
                    # Decode if order_str is bytes
                    if isinstance(order_str, bytes):
                        order_str = order_str.decode('utf-8')
                
                    order = json.loads(order_str)
                    order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
            
                    # Get current datetime
                    now = get_current_ist()
            
                    # Calculate the reference date based on cutoff time
                    if now.hour < cutoff_hour:
                        # If current time is before 7:00 AM, reference date is yesterday
                        reference_date = now.date() - timedelta(days=1)
                    else:
                        # If current time is 7:00 AM or later, reference date is today
                        reference_date = now.date()
            
                    # Create a datetime object for the cutoff time of the reference date
                    cutoff_datetime = datetime.combine(reference_date, time(hour=cutoff_hour))
            
                    # Check if order is within the current cycle (from cutoff_datetime to cutoff_datetime + 24 hours)
                    if cutoff_datetime <= order_date < cutoff_datetime + timedelta(hours=24):
                        orders.append(order)
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.error(f"Error parsing order: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(orders)} orders from Redis for the current cycle")
            return orders
        except Exception as e:
            logger.error(f"Error getting today's orders from Redis: {str(e)}")
            return []

    def archive_completed_order(self, order_id):
        """Move completed order to archive and remove from active lists"""
        try:
            # Find the order
            order = None
            all_orders = self.redis.lrange("orders:all", 0, -1)
            
            for i, order_str in enumerate(all_orders):
                try:
                    # Decode if order_str is bytes
                    if isinstance(order_str, bytes):
                        order_str = order_str.decode('utf-8')
                    
                    o = json.loads(order_str)
                    if o["order_id"] == order_id:
                        order = o
                        break
                except json.JSONDecodeError:
                    continue
            
            if not order:
                logger.warning(f"Order {order_id} not found for archiving")
                return False
            
            # Add to archive
            self.redis.rpush("orders:archive", json.dumps(order))
            
            # Remove from active lists
            # First decode the original order string for comparison
            original_order_str = json.dumps(order, sort_keys=True)
            if isinstance(all_orders[i], bytes):
                all_orders[i] = all_orders[i].decode('utf-8')
                
            self.redis.lrem("orders:all", 0, all_orders[i])
            self.redis.lrem(f"orders:branch:{order['branch'].lower()}", 0, all_orders[i])
            
            logger.info(f"Order {order_id} archived successfully")
            return True
        except Exception as e:
            logger.error(f"Error archiving order {order_id}: {str(e)}")
            return False

# Initialize Redis state handler
redis_state = RedisState()