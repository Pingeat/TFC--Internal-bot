# # handlers/message_handler.py
# import json
# import traceback
# from config.settings import BRANCHES, ORDER_STATUS, PAYMENT_BRANCHES, PRODUCT_CATALOG, PRODUCT_CATEGORIES, PRODUCT_PRICES, STAFF_CONTACTS
# from stateHandlers.redis_state import redis_state
# from services.whatsapp_service import (
#     send_branch_delivery_list,
#     send_branch_selection_message,
#     send_delivery_confirmation,
#     send_full_catalog,
#     send_cart_summary,
#     send_order_update_menu,
#     send_status_confirmation,
#     send_status_options,
#     send_text_message
# )
# from services.order_service import place_order, update_order_status
# from utils.logger import get_logger
# from datetime import datetime

# logger = get_logger("message_handler")

# def handle_incoming_message(data):
#     """Handle incoming WhatsApp messages with improved cart handling"""
#     logger.info("Received message data")
    
#     try:
#         for entry in data.get("entry", []):
#             for change in entry.get("changes", []):
#                 value = change.get("value", {})
#                 messages = value.get("messages", [])
#                 if not messages:
#                     continue
                
#                 msg = messages[0]
#                 sender = msg.get("from").lstrip('+')  # Normalize sender ID
#                 message_type = msg.get("type")
                
#                 # Log activity
#                 if message_type == "text":
#                     text = msg.get("text", {}).get("body", "").strip().lower()
#                     logger.info(f"Message received from {sender}: {text}")
                
#                 # Get current state
#                 current_state = redis_state.get_user_state(sender)
#                 logger.debug(f"Current state for {sender}: {current_state}")
                
#                 # Check if sender is staff
#                 staff_role = get_staff_role(sender)
                
#                 # INTERACTIVE MESSAGE HANDLING - FIXED TO HANDLE DIFFERENT STATES
#                 if message_type == "interactive":
#                     interactive_type = msg.get("interactive", {}).get("type")
#                     if interactive_type == "list_reply":
#                         # CRITICAL FIX: Handle list replies based on current state
#                         if staff_role and current_state and current_state.get("step") == "WAITING_FOR_ORDER_SELECTION":
#                             # Handle order selection for staff
#                             order_selection_id = msg.get("interactive", {}).get("list_reply", {}).get("id")
#                             handle_order_selection(sender, order_selection_id, current_state)
#                         elif staff_role and current_state and current_state.get("step") == "WAITING_FOR_STATUS_SELECTION":
#                             # Handle status selection for staff
#                             status_selection_id = msg.get("interactive", {}).get("list_reply", {}).get("id")
#                             handle_status_selection(sender, status_selection_id, current_state)
#                         else:
#                             # Handle branch selection for customers
#                             selected_branch = msg.get("interactive", {}).get("list_reply", {}).get("id")
#                             handle_branch_selection(sender, selected_branch, current_state)
#                     elif interactive_type == "button_reply":
#                         # Handle button responses (like cart actions)
#                         button_id = msg.get("interactive", {}).get("button_reply", {}).get("id")
#                         handle_button_response(sender, button_id, current_state)
#                     elif interactive_type == "catalog_message":
#                         # Handle catalog selection
#                         catalog_id = msg.get("interactive", {}).get("catalog_message", {}).get("catalog_id")
#                         product_retailer_id = msg.get("interactive", {}).get("catalog_message", {}).get("product_retailer_id")
#                         handle_catalog_selection(sender, product_retailer_id, current_state)
                
#                 # TEXT MESSAGE HANDLING
#                 elif message_type == "text":
#                     text = msg.get("text", {}).get("body", "").strip().lower()
#                     handle_text_message(sender, text, current_state)
                
#                 # ORDER MESSAGE HANDLING
#                 elif message_type == "order":
#                     items = msg.get("order", {}).get("product_items", [])
#                     handle_catalog_order(sender, items)
                
#                 # LOCATION MESSAGE HANDLING
#                 elif message_type == "location":
#                     # In a real implementation, you might use location for delivery
#                     # For internal system, we don't need this
#                     send_text_message(sender, "📍 Location received. For internal orders, please select your branch from the menu.")
        
#         return "OK", 200
#     except Exception as e:
#         logger.error(f"Message handler error: {str(e)}\n{traceback.format_exc()}")
#         return "Error processing message", 500

# def handle_text_message(sender, text, current_state):
#     """Handle text messages from users with proper state management"""
#     logger.info(f"Handling text message from {sender}: {text}")
    
#     # Check if sender is staff
#     staff_role = get_staff_role(sender)
    
#     # Handle staff commands
#     if staff_role:
#         if text == "/update" or text == "/status":
#             handle_staff_command(sender, "/update", current_state)
#             return
#         elif text == "/list" or text == "/orders":
#             handle_staff_command(sender, "/list", current_state)
#             return
#         elif text == "/delivery" or text == "/deliveries":
#             handle_delivery_command(sender, current_state)
#             return
#         elif text == "/complete" and staff_role == "supervisor":
#             handle_staff_command(sender, "/complete", current_state)
#             return
#         elif text == "/menu" or text == "/help":
#             handle_staff_command(sender, "/menu", current_state)
#             return
    
#     # Reset to branch selection if state is invalid or missing
#     if not current_state or current_state.get("step") not in ["SELECT_BRANCH", "IN_CATALOG", "VIEWING_DELIVERY_LIST"]:
#         logger.info(f"Resetting state for {sender} - invalid or missing state: {current_state}")
#         redis_state.clear_user_state(sender)
#         send_branch_selection_message(sender)
#         redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#         return
    
#     # Check if it's a branch selection
#     if current_state.get("step") == "SELECT_BRANCH":
#         try:
#             branch_idx = int(text) - 1
#             if 0 <= branch_idx < len(BRANCHES):
#                 selected_branch = BRANCHES[branch_idx]
#                 redis_state.set_branch(sender, selected_branch)
#                 redis_state.set_user_state(sender, {"step": "IN_CATALOG"})
#                 send_full_catalog(sender, selected_branch)
#             else:
#                 send_text_message(sender, "❌ Invalid branch number. Please select a number between 1 and 8.")
#         except ValueError:
#             # Check for common greetings that should reset to branch selection
#             greetings = ["hi", "hello", "hey", "hii", "hiii", "namaste", "good morning", "good afternoon", "good evening"]
#             if text in greetings:
#                 logger.info(f"User {sender} sent greeting '{text}', resetting to branch selection")
#                 redis_state.clear_user_state(sender)
#                 send_branch_selection_message(sender)
#                 redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#             else:
#                 send_text_message(sender, "❌ Please enter a valid branch number (1-8).")
#         return
    
#     # Check if it's a catalog interaction
#     if current_state.get("step") == "IN_CATALOG":
#         # Check for cart commands
#         if text in ["cart", "view cart", "my cart"]:
#             send_cart_summary(sender)
#             return
            
#         # Check for checkout command
#         if text in ["checkout", "proceed", "place order", "2"]:
#             cart = redis_state.get_cart(sender)
#             if not cart["items"]:
#                 send_text_message(sender, "🛒 Your cart is empty. Please add items before checking out.")
#                 return
#             if cart["branch"]:
#                 success, message = place_order(sender, cart["branch"])
#                 send_text_message(sender, message)
#             else:
#                 # This should not happen, but handle it gracefully
#                 logger.error(f"User {sender} in catalog state but branch not set")
#                 redis_state.clear_user_state(sender)
#                 send_branch_selection_message(sender)
#                 redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#             return
            
#         # Check for clear cart command
#         if text in ["clear cart", "3"]:
#             redis_state.clear_cart(sender)
#             send_text_message(sender, "🗑️ Your cart has been cleared.")
#             return
            
#         # Check for continue shopping command
#         if text in ["continue shopping", "1"]:
#             send_full_catalog(sender, redis_state.get_cart(sender)["branch"])
#             return
            
#         # Check if it's a product name
#         product_found = False
#         for category, products in PRODUCT_CATEGORIES.items():
#             for product in products:
#                 if product in text or text in product:
#                     # Add to cart (quantity 1 by default)
#                     price = PRODUCT_PRICES.get(product, 100)
#                     redis_state.add_to_cart(sender, product, 1, price)
#                     send_text_message(sender, f"✅ Added {product.title()} to your cart! (Price: ₹{price})")
#                     product_found = True
#                     break
#             if product_found:
#                 break
                
#         if not product_found:
#             # Handle common greetings even in catalog state
#             greetings = ["hi", "hello", "hey"]
#             if any(greeting in text for greeting in greetings):
#                 logger.info(f"User {sender} sent greeting '{text}' in catalog state, resetting flow")
#                 redis_state.clear_user_state(sender)
#                 send_branch_selection_message(sender)
#                 redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#                 return
                
#             # Show helpful menu instead of just an error
#             message = "❌ I didn't understand that.\n\n"
#             message += "You can:\n"
#             message += "1. Type 'cart' to view your cart\n"
#             message += "2. Type 'checkout' to place your order\n"
#             message += "3. Type 'clear cart' to start over\n"
#             message += "4. Type 'continue shopping' to see the catalog again"
#             send_text_message(sender, message)
    
#     # Check if it's a delivery interaction
#     if current_state.get("step") == "VIEWING_DELIVERY_LIST":
#         # Reset to branch selection if they send a random message
#         logger.info(f"Resetting from delivery view for {sender} due to unrecognized command")
#         redis_state.clear_user_state(sender)
#         send_branch_selection_message(sender)
#         redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#         return
    
#     # This point should never be reached with the above structure
#     # But just in case, reset to branch selection
#     logger.warning(f"Unexpected state reached for {sender}")
#     redis_state.clear_user_state(sender)
#     send_branch_selection_message(sender)
#     redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})

# def handle_branch_selection(sender, selected_branch, current_state):
#     """Handle branch selection from interactive list"""
#     logger.info(f"Handling branch selection for {sender}: {selected_branch}")
    
#     if current_state and current_state.get("step") == "SELECT_BRANCH":
#         # Check if the selected branch is valid
#         valid_branches = [b.lower() for b in BRANCHES]
#         if selected_branch.lower() in valid_branches:
#             # Find the exact branch name from our list (to maintain consistent casing)
#             selected_branch = next(b for b in BRANCHES if b.lower() == selected_branch.lower())
            
#             redis_state.set_branch(sender, selected_branch)
#             redis_state.set_user_state(sender, {"step": "IN_CATALOG"})
#             send_full_catalog(sender, selected_branch)
#         else:
#             send_text_message(sender, "❌ Invalid branch selection. Please try again.")
#     else:
#         # If we're not expecting a branch selection, send the branch selection menu again
#         send_branch_selection_message(sender)
#         redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})

# def handle_catalog_order(sender, items):
#     """Handle catalog orders (when user selects from WhatsApp catalog) with category awareness"""
#     logger.info(f"Handling catalog order from {sender}")
    
#     # Get user's current state
#     current_state = redis_state.get_user_state(sender)
#     logger.debug(f"[CATALOG ITEMS]: {items}")
    
#     # If branch is not selected, prompt for branch
#     cart = redis_state.get_cart(sender)
#     if not cart["branch"]:
#         send_branch_selection_message(sender)
#         redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#         return
    
#     # Add catalog items to cart
#     for item in items:
#         product_id = item.get("product_retailer_id", "")
#         quantity = int(item.get("quantity", 1))
        
#         # Get product info from catalog mapping
#         product_info = PRODUCT_CATALOG.get(product_id)
        
#         if product_info:
#             product_name = product_info["name"]
#             price = product_info["price"]
            
#             # Add to cart
#             redis_state.add_to_cart(sender, product_name, quantity, price)
#             logger.info(f"Added {quantity}x {product_name} (ID: {product_id}) to cart for {sender}")
#         else:
#             # Fallback to using ID as name (shouldn't happen with proper catalog setup)
#             logger.warning(f"Unknown product ID: {product_id} for sender {sender}")
#             product_name = product_id.replace("_", " ")
#             price = PRODUCT_PRICES.get(product_name.lower(), 100)
#             redis_state.add_to_cart(sender, product_name, quantity, price)
    
#     # Send cart summary
#     send_cart_summary(sender)
#     redis_state.set_user_state(sender, {"step": "IN_CATALOG"})

# def handle_catalog_selection(sender, product_retailer_id, current_state):
#     """Handle product selection from catalog"""
#     logger.info(f"Handling catalog selection for {sender}: {product_retailer_id}")
    
#     if not current_state or current_state.get("step") != "IN_CATALOG":
#         send_branch_selection_message(sender)
#         redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
#         return
    
#     # Get product info from catalog mapping
#     product_info = PRODUCT_CATALOG.get(product_retailer_id)
    
#     if product_info:
#         product_name = product_info["name"]
#         price = product_info["price"]
        
#         # Add to cart (quantity 1 by default)
#         redis_state.add_to_cart(sender, product_name, 1, price)
#         send_text_message(sender, f"✅ Added {product_name} to your cart! (Price: ₹{price})")
#         logger.info(f"Added 1x {product_name} (ID: {product_retailer_id}) to cart for {sender}")
#     else:
#         logger.warning(f"Unknown product ID selected: {product_retailer_id} for sender {sender}")
#         send_text_message(sender, "❌ Product not found. Please try again.")

# def handle_staff_command(sender, command, current_state):
#     """Handle staff commands for order management"""
#     logger.info(f"Handling staff command from {sender}: {command}")
    
#     # Check if sender is staff
#     staff_role = get_staff_role(sender)
#     if not staff_role:
#         logger.warning(f"Non-staff user tried to access staff commands: {sender}")
#         send_text_message(sender, "❌ You don't have permission to perform this action.")
#         return
    
#     # Handle command
#     if command == "/update" or (current_state and current_state.get("step") == "WAITING_FOR_ORDER_SELECTION"):
#         logger.info(f"Staff {staff_role} requesting order update")
#         redis_state.set_user_state(sender, {
#             "step": "WAITING_FOR_ORDER_SELECTION",
#             "staff_role": staff_role
#         })
#         send_order_update_menu(sender)
    
#     elif command == "/list":
#         # Show active orders
#         orders = redis_state.get_todays_orders()
#         # Filter out completed orders
#         active_orders = [o for o in orders if o["status"] != ORDER_STATUS["COMPLETED"]]
        
#         if not active_orders:
#             send_text_message(sender, "✅ All orders have been completed for today!")
#             return
        
#         message = "📋 *ACTIVE ORDERS*\n\n"
#         for order in active_orders:
#             message += f"• #{order['order_id']} - {order['branch'].title()} ({order['status']})\n"
#             message += f"  {len(order['items'])} items | {order['total']} total\n\n"
        
#         send_text_message(sender, message)
    
#     elif command == "/complete" and staff_role == "supervisor":
#         # Mark day as completed
#         orders = redis_state.get_todays_orders()
#         all_delivered = all(o["status"] == ORDER_STATUS["DELIVERED"] for o in orders)
        
#         if all_delivered:
#             for order in orders:
#                 update_order_status(order["order_id"], ORDER_STATUS["COMPLETED"])
#             send_text_message(sender, "✅ *DAY COMPLETED*\n\nAll orders marked as completed.")
#         else:
#             send_text_message(sender, "❌ Cannot complete day - not all orders are delivered.")
    
#     else:
#         # Show staff menu
#         message = "🛠️ *STAFF MENU*\n\n"
#         message += "Available commands:\n"
#         message += "/update - Update order status\n"
#         message += "/list - View all active orders\n"
        
#         if staff_role == "supervisor":
#             message += "/complete - Mark day as completed\n"
        
#         send_text_message(sender, message)

# def handle_order_selection(sender, selection_id, current_state):
#     """Handle order selection for status update with better error handling"""
#     logger.info(f"Handling order selection for {sender}: {selection_id}")
    
#     # Extract order ID from selection (format: "ORDER:{order_id}")
#     if not selection_id.startswith("ORDER:"):
#         logger.warning(f"Invalid selection format: {selection_id}")
#         send_text_message(sender, "❌ Invalid selection. Please try again.")
#         # Reset to order selection menu
#         redis_state.set_user_state(sender, {
#             "step": "WAITING_FOR_ORDER_SELECTION",
#             "staff_role": current_state.get("staff_role", "unknown")
#         })
#         send_order_update_menu(sender)
#         return
    
#     order_id = selection_id[6:]  # Remove "ORDER:" prefix
#     staff_role = current_state.get("staff_role", "unknown")
    
#     # Get order details
#     order = None
#     for o in redis_state.get_todays_orders():
#         if o["order_id"] == order_id:
#             order = o
#             break
    
#     if not order:
#         send_text_message(sender, f"❌ Order #{order_id} not found.")
#         # Reset to order selection menu
#         redis_state.set_user_state(sender, {
#             "step": "WAITING_FOR_ORDER_SELECTION",
#             "staff_role": staff_role
#         })
#         send_order_update_menu(sender)
#         return
    
#     # Store selected order in state
#     redis_state.set_user_state(sender, {
#         "step": "WAITING_FOR_STATUS_SELECTION",
#         "selected_order": order_id,
#         "staff_role": staff_role
#     })
    
#     logger.info(f"Staff {staff_role} selected order {order_id} (status: {order['status']})")
    
#     # Send status options
#     send_status_options(sender, order_id, order["status"], staff_role)

# def handle_status_selection(sender, selection_id, current_state):
#     """Handle status selection for order update with better error handling"""
#     logger.info(f"Handling status selection for {sender}: {selection_id}")
    
#     # Extract status from selection (format: "STATUS:{status}")
#     if not selection_id.startswith("STATUS:"):
#         logger.warning(f"Invalid status selection format: {selection_id}")
#         send_text_message(sender, "❌ Invalid selection. Please try again.")
#         # Reset to order selection menu
#         redis_state.set_user_state(sender, {
#             "step": "WAITING_FOR_ORDER_SELECTION",
#             "staff_role": current_state.get("staff_role", "unknown")
#         })
#         send_order_update_menu(sender)
#         return
    
#     new_status = selection_id[7:]  # Remove "STATUS:" prefix
    
#     if not current_state or not current_state.get("selected_order"):
#         send_text_message(sender, "❌ No order selected. Please select an order first.")
#         redis_state.set_user_state(sender, {
#             "step": "WAITING_FOR_ORDER_SELECTION",
#             "staff_role": current_state.get("staff_role", "unknown")
#         })
#         send_order_update_menu(sender)
#         return
    
#     order_id = current_state["selected_order"]
#     staff_role = current_state["staff_role"]
    
#     logger.info(f"Staff {staff_role} attempting to update order {order_id} to {new_status}")
    
#     # Update status
#     success = update_order_status(order_id, new_status)
    
#     if success:
#         # Store in state for confirmation
#         redis_state.set_user_state(sender, {
#             "step": "STATUS_UPDATE_CONFIRMATION",
#             "last_updated_order": order_id,
#             "last_status": new_status,
#             "staff_role": staff_role
#         })
#         send_status_confirmation(sender, order_id, new_status)
#     else:
#         send_text_message(sender, f"❌ Failed to update status for order #{order_id}")
#         redis_state.set_user_state(sender, {
#             "step": "WAITING_FOR_ORDER_SELECTION",
#             "staff_role": staff_role
#         })
#         send_order_update_menu(sender)


# def get_staff_role(sender):
#     """Determine staff role based on sender number"""
#     for role, number in STAFF_CONTACTS.items():
#         if sender == number.lstrip('+'):
#             return role
#     return None

# def handle_delivery_command(sender, current_state):
#     """Handle delivery command from delivery staff"""
#     logger.info(f"Handling delivery command for {sender}")
    
#     # Verify this is delivery staff
#     staff_role = get_staff_role(sender)
#     if staff_role not in ["delivery", "supervisor"]:
#         send_text_message(sender, "❌ You don't have permission to access delivery features.")
#         return
    
#     # Set state for delivery flow
#     redis_state.set_user_state(sender, {
#         "step": "VIEWING_DELIVERY_LIST",
#         "staff_role": staff_role
#     })
    
#     # Send branch-based delivery list
#     send_branch_delivery_list(sender)

# def handle_delivery_confirmation(sender, branch_key, current_state):
#     """Handle delivery confirmation for a branch"""
#     logger.info(f"Handling delivery confirmation for {sender} - branch: {branch_key}")
    
#     # Verify this is delivery staff
#     staff_role = get_staff_role(sender)
#     if staff_role not in ["delivery", "supervisor"]:
#         send_text_message(sender, "❌ You don't have permission to confirm deliveries.")
#         return
    
#     # Get branch name
#     branch = next((b for b in BRANCHES if b.lower() == branch_key), branch_key)
    
#     # Mark all READY orders for this branch as DELIVERED
#     all_orders = redis_state.redis.lrange("orders:all", 0, -1)
#     delivered_count = 0
#     total_items = 0
    
#     for order_str in all_orders:
#         try:
#             order = json.loads(order_str)
#             if order["status"] == ORDER_STATUS["READY"] and order["branch"].lower() == branch_key:
#                 # Count items
#                 items_count = sum(item["quantity"] for item in order["items"])
#                 total_items += items_count
                
#                 # Mark order as delivered
#                 if update_order_status(order["order_id"], ORDER_STATUS["DELIVERED"]):
#                     delivered_count += 1
#         except (json.JSONDecodeError, KeyError, ValueError) as e:
#             logger.error(f"Error processing order for delivery confirmation: {str(e)}")
#             continue
    
#     if delivered_count > 0:
#         logger.info(f"Marked {delivered_count} orders ({total_items} items) as delivered for branch {branch}")
        
#         # Store in state for confirmation
#         redis_state.set_user_state(sender, {
#             "step": "DELIVERY_CONFIRMATION",
#             "last_branch": branch,
#             "orders_delivered": delivered_count,
#             "items_delivered": total_items
#         })
        
#         # Send confirmation
#         send_delivery_confirmation(sender, branch, total_items)
#     else:
#         send_text_message(sender, f"❌ No READY orders found for branch {branch.title()}.")

# def handle_button_response(sender, button_id, current_state):
#     """Handle button responses from user with proper staff/customer differentiation"""
#     logger.info(f"Handling button response for {sender}: {button_id}")
    
#     # Get staff role (if applicable)
#     staff_role = get_staff_role(sender)
    
#     # Handle delivery staff commands
#     if staff_role in ["delivery", "supervisor"] and button_id.startswith("DELIVERED:"):
#         branch_key = button_id.split(":")[1]
#         handle_delivery_confirmation(sender, branch_key, current_state)
#         return
#     elif staff_role in ["delivery", "supervisor"] and button_id == "confirm_another":
#         handle_delivery_command(sender, current_state)
#         return
#     elif staff_role in ["delivery", "supervisor"] and button_id == "main_menu":
#         redis_state.clear_user_state(sender)
#         # Show staff menu
#         handle_staff_command(sender, "/menu", None)
#         return
    
#     # Staff status update flow (for non-delivery staff actions)
#     if staff_role:
#         if current_state and current_state.get("step") == "WAITING_FOR_ORDER_SELECTION":
#             logger.info("Processing order selection for staff")
#             handle_order_selection(sender, button_id, current_state)
#             return
        
#         elif current_state and current_state.get("step") == "WAITING_FOR_STATUS_SELECTION":
#             logger.info("Processing status selection for staff")
#             handle_status_selection(sender, button_id, current_state)
#             return
        
#         elif current_state and current_state.get("step") == "STATUS_UPDATE_CONFIRMATION":
#             logger.info("Processing status confirmation for staff")
#             if button_id == "update_another":
#                 redis_state.set_user_state(sender, {
#                     "step": "WAITING_FOR_ORDER_SELECTION",
#                     "staff_role": staff_role
#                 })
#                 send_order_update_menu(sender)
#             elif button_id == "main_menu":
#                 redis_state.clear_user_state(sender)
#                 # Show staff menu
#                 handle_staff_command(sender, "/menu", None)
#             return
    
#     # Customer cart flow
#     logger.info("Processing button response for customer")
#     if current_state and current_state.get("step") == "IN_CATALOG":
#         if button_id == "view_cart" or button_id == "cart":
#             send_cart_summary(sender)
#         elif button_id == "checkout":
#             cart = redis_state.get_cart(sender)
#             if not cart["items"]:
#                 send_text_message(sender, "🛒 Your cart is empty. Please add items before checking out.")
#                 return
#             if cart["branch"]:
#                 success, message = place_order(sender, cart["branch"])
#                 send_text_message(sender, message)
#             else:
#                 send_text_message(sender, "❌ Branch not selected. Please start over.")
#         elif button_id == "clear_cart":
#             redis_state.clear_cart(sender)
#             send_text_message(sender, "🗑️ Your cart has been cleared.")
#         elif button_id == "continue_shopping":
#             send_full_catalog(sender, redis_state.get_cart(sender)["branch"])
#     else:
#         # If we're not in the catalog step, send the branch selection
#         send_branch_selection_message(sender)
#         redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})














# handlers/message_handler.py
import json
import traceback
from config.settings import BRANCHES, PAYMENT_BRANCHES, PRODUCT_CATEGORIES, PRODUCT_CATALOG, PRODUCT_PRICES, ORDER_STATUS, STAFF_CONTACTS
from stateHandlers.redis_state import redis_state
from services.whatsapp_service import (
    send_branch_selection_message,
    send_full_catalog,
    send_cart_summary,
    send_text_message,
    send_branch_delivery_instructions,
    send_delivery_status,
    send_delivery_confirmation
)
from services.order_service import (
    place_order,
    update_branch_status
)
from utils.logger import get_logger
from datetime import datetime

logger = get_logger("message_handler")

def get_staff_role(sender):
    """Determine staff role based on sender number"""
    for role, number in STAFF_CONTACTS.items():
        if sender == number.lstrip('+'):
            return role
    return None

def handle_incoming_message(data):
    """Handle incoming WhatsApp messages with improved cart handling"""
    logger.info("Received message data")
    
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    continue
                
                msg = messages[0]
                sender = msg.get("from").lstrip('+')  # Normalize sender ID
                message_type = msg.get("type")
                
                # Log activity
                if message_type == "text":
                    text = msg.get("text", {}).get("body", "").strip().lower()
                    logger.info(f"Message received from {sender}: {text}")
                
                # Get current state
                current_state = redis_state.get_user_state(sender)
                logger.debug(f"Current state for {sender}: {current_state}")
                
                # INTERACTIVE MESSAGE HANDLING
                if message_type == "interactive":
                    interactive_type = msg.get("interactive", {}).get("type")
                    if interactive_type == "list_reply":
                        # Handle branch selection from list
                        selected_branch = msg.get("interactive", {}).get("list_reply", {}).get("id")
                        handle_branch_selection(sender, selected_branch, current_state)
                    elif interactive_type == "button_reply":
                        # Handle button responses (like cart actions)
                        button_id = msg.get("interactive", {}).get("button_reply", {}).get("id")
                        handle_button_response(sender, button_id, current_state)
                    elif interactive_type == "catalog_message":
                        # Handle catalog selection
                        catalog_id = msg.get("interactive", {}).get("catalog_message", {}).get("catalog_id")
                        product_retailer_id = msg.get("interactive", {}).get("catalog_message", {}).get("product_retailer_id")
                        handle_catalog_selection(sender, product_retailer_id, current_state)
                
                # TEXT MESSAGE HANDLING
                elif message_type == "text":
                    text = msg.get("text", {}).get("body", "").strip().lower()
                    handle_text_message(sender, text, current_state)
                
                # ORDER MESSAGE HANDLING
                elif message_type == "order":
                    items = msg.get("order", {}).get("product_items", [])
                    handle_catalog_order(sender, items)
                
                # LOCATION MESSAGE HANDLING
                elif message_type == "location":
                    # In a real implementation, you might use location for delivery
                    # For internal system, we don't need this
                    send_text_message(sender, "📍 Location received. For internal orders, please select your branch from the menu.")
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Message handler error: {str(e)}\n{traceback.format_exc()}")
        return "Error processing message", 500

def handle_branch_selection(sender, selected_branch, current_state):
    """Handle branch selection from interactive list"""
    logger.info(f"Handling branch selection for {sender}: {selected_branch}")
    
    # Validate branch
    valid_branch = None
    for b in BRANCHES:
        if b.lower() == selected_branch.lower():
            valid_branch = b
            break
    
    if not valid_branch:
        logger.error(f"Invalid branch selected by {sender}: {selected_branch}")
        send_text_message(sender, "❌ Invalid branch selection. Please try again.")
        send_branch_selection_message(sender)
        return
    
    # Set branch in cart
    cart = redis_state.get_cart(sender)
    cart["branch"] = valid_branch
    redis_state.redis.setex(f"user:{sender}:cart", 7200, json.dumps(cart))
    
    # Send catalog
    send_full_catalog(sender, valid_branch)
    redis_state.set_user_state(sender, {"step": "IN_CATALOG"})
    
    logger.info(f"Branch set for {sender}: {valid_branch}")

def handle_button_response(sender, button_id, current_state):
    """Handle button responses from user"""
    logger.info(f"Handling button response for {sender}: {button_id}")
    
    # Check if sender is staff
    staff_role = get_staff_role(sender)
    
    # Customer cart flow
    if not staff_role:
        if current_state and current_state.get("step") == "IN_CATALOG":
            if button_id == "view_cart" or button_id == "cart":
                send_cart_summary(sender)
            elif button_id == "checkout":
                cart = redis_state.get_cart(sender)
                if not cart["items"]:
                    send_text_message(sender, "🛒 Your cart is empty. Please add items before checking out.")
                    return
                if cart["branch"]:
                    success, message = place_order(sender, cart["branch"])
                    send_text_message(sender, message)
                else:
                    send_text_message(sender, "❌ Branch not selected. Please start over.")
            elif button_id == "clear_cart":
                redis_state.clear_cart(sender)
                send_text_message(sender, "🗑️ Your cart has been cleared.")
            elif button_id == "continue_shopping":
                send_full_catalog(sender, redis_state.get_cart(sender)["branch"])
        else:
            # If we're not in the catalog step, send the branch selection
            send_branch_selection_message(sender)
            redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
    else:
        # Staff might still use some button responses
        if current_state and current_state.get("step") == "IN_CATALOG":
            if button_id == "view_cart" or button_id == "cart":
                send_cart_summary(sender)
            elif button_id == "checkout":
                cart = redis_state.get_cart(sender)
                if not cart["items"]:
                    send_text_message(sender, "🛒 Your cart is empty. Please add items before checking out.")
                    return
                if cart["branch"]:
                    success, message = place_order(sender, cart["branch"])
                    send_text_message(sender, message)
                else:
                    send_text_message(sender, "❌ Branch not selected. Please start over.")
            elif button_id == "clear_cart":
                redis_state.clear_cart(sender)
                send_text_message(sender, "🗑️ Your cart has been cleared.")
            elif button_id == "continue_shopping":
                send_full_catalog(sender, redis_state.get_cart(sender)["branch"])

def handle_text_message(sender, text, current_state):
    """Handle text messages from users with simple command system"""
    logger.info(f"Handling text message from {sender}: {text}")
    
    # Check if sender is staff
    staff_role = get_staff_role(sender)
    
    # Handle staff commands
    if staff_role:
        # Handle delivery commands - simple text format like "delivered kondapur"
        if "ready" in text or "delivered" in text or "completed" in text:
            update_branch_status_from_command(sender, text)
            return
        elif text == "/status" or text == "/list":
            send_delivery_status(sender)
            return
        elif text == "/help" or text == "/commands":
            send_branch_delivery_instructions(sender)
            return
    
    # Reset to branch selection if state is invalid or missing
    if not current_state or current_state.get("step") not in ["SELECT_BRANCH", "IN_CATALOG"]:
        logger.info(f"Resetting state for {sender} - invalid or missing state: {current_state}")
        redis_state.clear_user_state(sender)
        send_branch_selection_message(sender)
        redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
        return
    
    # Check if it's a branch selection
    if current_state.get("step") == "SELECT_BRANCH":
        try:
            branch_idx = int(text) - 1
            if 0 <= branch_idx < len(BRANCHES):
                selected_branch = BRANCHES[branch_idx]
                redis_state.set_branch(sender, selected_branch)
                redis_state.set_user_state(sender, {"step": "IN_CATALOG"})
                send_full_catalog(sender, selected_branch)
            else:
                send_text_message(sender, "❌ Invalid branch number. Please select a number between 1 and 8.")
        except ValueError:
            # Check for common greetings that should reset to branch selection
            greetings = ["hi", "hello", "hey", "hii", "hiii", "namaste", "good morning", "good afternoon", "good evening"]
            if text in greetings:
                logger.info(f"User {sender} sent greeting '{text}', resetting to branch selection")
                redis_state.clear_user_state(sender)
                send_branch_selection_message(sender)
                redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
            else:
                send_text_message(sender, "❌ Please enter a valid branch number (1-8).")
        return
    
    # Check if it's a catalog interaction
    if current_state.get("step") == "IN_CATALOG":
        # Check for cart commands
        if text in ["cart", "view cart", "my cart"]:
            send_cart_summary(sender)
            return
            
        # Check for checkout command
        if text in ["checkout", "proceed", "place order", "2"]:
            cart = redis_state.get_cart(sender)
            if not cart["items"]:
                send_text_message(sender, "🛒 Your cart is empty. Please add items before checking out.")
                return
            if cart["branch"]:
                success, message = place_order(sender, cart["branch"])
                send_text_message(sender, message)
            else:
                # This should not happen, but handle it gracefully
                logger.error(f"User {sender} in catalog state but branch not set")
                redis_state.clear_user_state(sender)
                send_branch_selection_message(sender)
                redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
            return
            
        # Check for clear cart command
        if text in ["clear cart", "3"]:
            redis_state.clear_cart(sender)
            send_text_message(sender, "🗑️ Your cart has been cleared.")
            return
            
        # Check for continue shopping command
        if text in ["continue shopping", "1"]:
            send_full_catalog(sender, redis_state.get_cart(sender)["branch"])
            return
            
        # Check if it's a product name
        product_found = False
        for category, products in PRODUCT_CATEGORIES.items():
            for product in products:
                if product in text or text in product:
                    # Add to cart (quantity 1 by default)
                    price = PRODUCT_PRICES.get(product, 100)
                    redis_state.add_to_cart(sender, product, 1, price)
                    send_text_message(sender, f"✅ Added {product.title()} to your cart! (Price: ₹{price})")
                    product_found = True
                    break
            if product_found:
                break
                
        if not product_found:
            # Handle common greetings even in catalog state
            greetings = ["hi", "hello", "hey"]
            if any(greeting in text for greeting in greetings):
                logger.info(f"User {sender} sent greeting '{text}' in catalog state, resetting flow")
                redis_state.clear_user_state(sender)
                send_branch_selection_message(sender)
                redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
                return
                
            # Show helpful menu instead of just an error
            message = "❌ I didn't understand that.\n\n"
            message += "You can:\n"
            message += "1. Type 'cart' to view your cart\n"
            message += "2. Type 'checkout' to place your order\n"
            message += "3. Type 'clear cart' to start over\n"
            message += "4. Type 'continue shopping' to see the catalog again"
            send_text_message(sender, message)
    
    # This point should never be reached with the above structure
    # But just in case, reset to branch selection
    logger.warning(f"Unexpected state reached for {sender}")
    redis_state.clear_user_state(sender)
    send_branch_selection_message(sender)
    redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})

def update_branch_status_from_command(sender, command):
    """Process simple branch status update commands"""
    logger.info(f"Processing branch status command: {command}")
    
    # Normalize command
    command = command.lower().strip()
    
    # Determine status and branch
    status = None
    branch = None
    
    if "ready" in command:
        status = ORDER_STATUS["READY"]
    elif "delivered" in command:
        status = ORDER_STATUS["DELIVERED"]
    elif "completed" in command:
        status = ORDER_STATUS["COMPLETED"]
    
    # Find branch name in command
    for b in BRANCHES:
        if b.lower() in command:
            branch = b
            break
    
    if not status or not branch:
        send_text_message(sender, "❌ Invalid command format. Use: [Status] [Branch]\nExample: \"Delivered Kondapur\"")
        send_branch_delivery_instructions(sender)
        return
    
    # Update branch status
    count = update_branch_status(branch, status)
    
    if count > 0:
        send_delivery_confirmation(sender, branch, status, count)
        logger.info(f"Updated {count} orders for {branch} to {status}")
    else:
        send_text_message(sender, f"❌ No orders found for {branch} in the previous status.")

def handle_catalog_order(sender, items):
    """Handle catalog orders (when user selects from WhatsApp catalog)"""
    logger.info(f"Handling catalog order from {sender}")
    
    # Get user's current state
    current_state = redis_state.get_user_state(sender)
    logger.debug(f"[CATALOG ITEMS]: {items}")
    
    # If branch is not selected, prompt for branch
    cart = redis_state.get_cart(sender)
    if not cart["branch"]:
        send_branch_selection_message(sender)
        redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
        return
    
    # Add catalog items to cart
    for item in items:
        product_id = item.get("product_retailer_id", "")
        quantity = int(item.get("quantity", 1))
        
        # Get product info from catalog mapping
        product_info = PRODUCT_CATALOG.get(product_id)
        
        if product_info:
            product_name = product_info["name"]
            price = product_info["price"]
            
            # Add to cart
            redis_state.add_to_cart(sender, product_name, quantity, price)
            logger.info(f"Added {quantity}x {product_name} (ID: {product_id}) to cart for {sender}")
        else:
            # Fallback to using ID as name (shouldn't happen with proper catalog setup)
            logger.warning(f"Unknown product ID: {product_id} for sender {sender}")
            product_name = product_id.replace("_", " ")
            price = PRODUCT_PRICES.get(product_name.lower(), 100)
            redis_state.add_to_cart(sender, product_name, quantity, price)
    
    # Send cart summary
    send_cart_summary(sender)
    redis_state.set_user_state(sender, {"step": "IN_CATALOG"})

def handle_catalog_selection(sender, product_retailer_id, current_state):
    """Handle product selection from catalog"""
    logger.info(f"Handling catalog selection for {sender}: {product_retailer_id}")
    
    if not current_state or current_state.get("step") != "IN_CATALOG":
        send_branch_selection_message(sender)
        redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})
        return
    
    # Get product info from catalog mapping
    product_info = PRODUCT_CATALOG.get(product_retailer_id)
    
    if product_info:
        product_name = product_info["name"]
        price = product_info["price"]
        
        # Add to cart (quantity 1 by default)
        redis_state.add_to_cart(sender, product_name, 1, price)
        send_text_message(sender, f"✅ Added {product_name} to your cart! (Price: ₹{price})")
        logger.info(f"Added 1x {product_name} (ID: {product_retailer_id}) to cart for {sender}")
    else:
        logger.warning(f"Unknown product ID selected: {product_retailer_id} for sender {sender}")
        send_text_message(sender, "❌ Product not found. Please try again.")