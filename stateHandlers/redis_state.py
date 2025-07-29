# stateHandlers/redis_state.py
import redis
import json
from config.credentials import REDIS_URL
from utils.logger import get_logger
from datetime import datetime

logger = get_logger("redis_state")

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
        """Get user state from Redis"""
        try:
            state = self.redis.get(f"user:{user_id}:state")
            if state:
                return json.loads(state)
            return None
        except Exception as e:
            logger.error(f"Error getting user state for {user_id}: {str(e)}")
            return None

    def set_user_state(self, user_id, state):
        """Set user state in Redis"""
        try:
            # Add timestamp for debugging
            state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        """Get user's cart from Redis"""
        try:
            cart = self.redis.get(f"user:{user_id}:cart")
            if cart:
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

    def create_order(self, user_id, order_id):
        """Create a new order from cart and move to orders store"""
        try:
            from config.settings import ORDER_STATUS, PAYMENT_BRANCHES
            from config.settings import BRANCHES
            
            cart = self.get_cart(user_id)
            if not cart["items"]:
                logger.warning(f"Attempt to create order with empty cart for {user_id}")
                return False
            
            # Validate branch
            if not cart["branch"] or cart["branch"].lower() not in [b.lower() for b in BRANCHES]:
                logger.error(f"Invalid branch in cart for {user_id}: {cart['branch']}")
                return False
            
            # Check if payment is required
            payment_required = cart["branch"].lower() in [b.lower() for b in PAYMENT_BRANCHES]
            
            # Create order data
            order_data = {
                "order_id": order_id,
                "user_id": user_id,
                "branch": cart["branch"],
                "items": cart["items"],
                "total": cart["total"],
                "status": ORDER_STATUS["PENDING"],
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "payment_required": payment_required,
                "payment_status": "PENDING" if payment_required else "PAID"
            }
            
            # Store in Redis orders list
            self.redis.rpush("orders:all", json.dumps(order_data))
            
            # Store in branch-specific list
            self.redis.rpush(f"orders:branch:{cart['branch'].lower()}", json.dumps(order_data))
            
            # Set order as active (for today's cycle)
            self.redis.setex(f"order:{order_id}:active", 86400, "1")  # 24 hours
            
            logger.info(f"Order created in Redis: {order_id} for branch {cart['branch']}")
            return order_data
        except Exception as e:
            logger.error(f"Error creating order in Redis: {str(e)}")
            return False

    def get_todays_orders(self):
        """Get all active orders from Redis"""
        try:
            orders = []
            # Get all order IDs that are active today
            order_keys = self.redis.keys("order:*:active")
            
            for key in order_keys:
                order_id = key.decode().split(":")[1]
                # Get the full order data (simplified for demo - in reality would need to fetch from orders list)
                order_data_str = self.redis.get(f"order:{order_id}:data")
                if order_data_str:
                    orders.append(json.loads(order_data_str))
            
            # If no Redis orders, try getting from the orders list
            if not orders:
                all_orders = self.redis.lrange("orders:all", 0, -1)
                for order_str in all_orders:
                    order = json.loads(order_str)
                    # Only include today's orders
                    order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
                    if order_date.date() == datetime.now().date():
                        orders.append(order)
            
            logger.info(f"Retrieved {len(orders)} orders from Redis for today")
            return orders
        except Exception as e:
            logger.error(f"Error getting today's orders from Redis: {str(e)}")
            return []

    def get_orders_by_branch(self, branch):
        """Get all orders for a specific branch"""
        try:
            branch_orders = []
            branch_key = f"orders:branch:{branch.lower()}"
            
            # Get orders from branch-specific list
            orders_str = self.redis.lrange(branch_key, 0, -1)
            for order_str in orders_str:
                order = json.loads(order_str)
                # Only include today's orders
                order_date = datetime.strptime(order["order_date"], "%Y-%m-%d %H:%M:%S")
                if order_date.date() == datetime.now().date():
                    branch_orders.append(order)
            
            logger.info(f"Retrieved {len(branch_orders)} orders from Redis for branch {branch}")
            return branch_orders
        except Exception as e:
            logger.error(f"Error getting orders for branch {branch}: {str(e)}")
            return []

# Initialize Redis state handler
redis_state = RedisState()