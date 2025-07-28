# # ##message_handler

# # import csv
# # from config.credentials import GOOGLE_MAPS_API_KEY
# # # from handlers.discount_handler import get_branch_discount
# # # from handlers.feedback_handler import save_feedback, schedule_feedback
# # # from handlers.marketing_handler import handle_marketing_message
# # from services.whatsapp_service import (
# #     send_text_message, send_greeting_template,
# #     send_delivery_takeaway_template,
# #     send_payment_option_template,
# #     send_pay_online_template,
# #     send_full_catalog, send_kitchen_branch_alert_template
# # )
# # import googlemaps
# # # from services.order_service import confirm_order, generate_order_id, log_order_to_csv, update_cart_interaction
# # from utils.logger import log_user_activity
# # # from utils.location_utils import get_branch_from_location
# # # from utils.operational_hours_utils import handle_off_hour_message, is_store_open
# # # from utils.payment_utils import generate_payment_link
# # from config.settings import ADMIN_NUMBERS, BRANCH_BLOCKED_USERS, BRANCH_STATUS, BRANCH_DISCOUNTS, ORDERS_CSV
# # # from stateHandlers.redis_state import add_pending_order, get_active_orders, get_pending_order, get_pending_orders, get_user_cart, remove_pending_order, set_user_cart, delete_user_cart, get_user_state, set_user_state, delete_user_state
# # # from handlers.randomMessage_handler import matching

# # gmaps = googlemaps.Client(GOOGLE_MAPS_API_KEY)
# # quick_reply_ratings = {"5- outstanding": "5", "4- excellent": "4", "3 – good": "3", "2 – average": "2", "1 – poor": "1"}



# # # Handle Incoming Messages
# # def handle_incoming_message(data):
# #     print("[MESSAGE HANDLER] Received data:", data)
# #     try:
# #         for entry in data.get("entry", []):
# #             for change in entry.get("changes", []):
# #                 value = change.get("value", {})
# #                 messages = value.get("messages", [])
# #                 if not messages:
# #                     continue
# #                 msg = messages[0]
# #                 sender = msg.get("from").lstrip('+')  # Normalize sender ID
# #                 message_type = msg.get("type")
                
# #                 # print("[SENDER]: ", sender)
# #                 # # Update cart interaction time
# #                 # update_cart_interaction(sender)
                
# #                 # # Check Store Operational Hours
# #                 # if not is_store_open():
# #                 #     handle_off_hour_message(sender)
# #                 #     return "Closed hours", 200
# #                 # # Log activity
# #                 # if message_type == "text":
# #                 #     text = msg.get("text", {}).get("body", "").strip().lower()
# #                 #     log_user_activity(sender, "message_received", text)

# #                 # # Get current state
# #                 # current_state = get_user_state(sender)
# #                 # print("[PRINTING CURRENT STATE OF THE USER]: ", current_state)

# #                 # TEXT MESSAGE HANDLING
# #                 if message_type == "text":
# #                     text = msg.get("text", {}).get("body", "").strip().lower()
# #                     if text in ["hi", "hello", "hey", "menu"]:
# #                         handle_greeting(sender)
# #                 #     elif any(text.startswith(k) for k in ["ready", "preparing", "ontheway", "delivered", "cancelled"]):
# #                 #         handle_update_order_status(sender, text)
# #                 #     elif text in ["status", "check status", "my order"]:
# #                 #         handle_check_status(sender)
# #                 #     elif any(text.startswith(cmd) for cmd in ["open", "close"]):
# #                 #         handle_open_close(sender, text)
# #                 #     elif "discount" in text:
# #                 #         handle_discount(sender, text)
# #                 #     elif current_state.get("step") == "awaiting_address":
# #                 #         handle_address_input(sender, text)
# #                 #     elif current_state.get("step") == "post_order_choice":
# #                 #         handle_post_order_choice(sender, text)
# #                 #     elif current_state.get("step") == "awaiting_location":
# #                 #         handle_location_by_text(sender, text)
# #                 #     # Marketing message command
# #                 #     elif text.startswith("message customer"):
# #                 #         if not is_admin(sender):
# #                 #             send_text_message(sender, "⚠️ This feature is only available to admins.")
# #                 #             return "OK", 200
                
# #                 #         handle_marketing_message(sender, text)
# #                 #         return "OK", 200
# #                 #     else:
# #                 #         matching(sender,text)    
# #                 #     return "OK", 200

# #                 # # LOCATION MESSAGE HANDLING
# #                 # elif message_type == "location":
# #                 #     latitude = msg.get("location", {}).get("latitude")
# #                 #     longitude = msg.get("location", {}).get("longitude")
# #                 #     handle_location(sender, latitude, longitude)

# #                 # ORDER MESSAGE HANDLING
# #                 elif message_type == "order":
# #                     # items = msg.get("order", {}).get("product_items", [])
# #                     send_text_message(sender, "Thanks for order")
# #                     # handle_order_message(sender, items)

# #                 # # BUTTON CLICK HANDLING
# #                 # elif message_type == "button":
# #                 #     button_text = msg.get("button", {}).get("text", "").strip().lower()
# #                 #     log_user_activity(sender, "button_clicked", button_text)
# #                 #     handle_button_click(sender, button_text)

# #         return "OK", 200

# #     except Exception as e:
# #         import traceback
# #         print("[ERROR] Message handler error:\n", traceback.format_exc())
# #         return "OK", 200
    
    
    
# #     # Handle Greeting
# # def handle_greeting(sender):
# #     send_text_message(sender, "Thanks for order")
# #     send_greeting_template(sender)














# # handlers/message_handler.py
# import csv
# from config.credentials import GOOGLE_MAPS_API_KEY
# from config.settings import BRANCHES, PAYMENT_BRANCHES, PRODUCT_CATEGORIES, CUT_OFF_HOUR
# from services.whatsapp_service import (
#     send_text_message, send_interactive_list_message,
#     send_interactive_button_message, send_order_confirmation
# )
# import googlemaps
# from stateHandlers.redis_state import (
#     get_user_state, set_user_state, delete_user_state,
#     get_user_cart, add_to_cart, remove_from_cart,
#     clear_user_cart, get_pending_order
# )
# from services.order_service import process_order, update_order_status_internal
# from utils.logger import log_user_activity
# from datetime import datetime, timedelta
# import re

# gmaps = googlemaps.Client(GOOGLE_MAPS_API_KEY)

# # Product catalog
# PRODUCT_CATALOG = {
#     "custard": [
#         {"name": "Custard Can", "price": 200},
#         {"name": "Mango Custard", "price": 150},
#         {"name": "Oatmeal", "price": 100},
#         {"name": "Less Sugar Custards", "price": 180}
#     ],
#     "delights": [
#         {"name": "Apricot Delight", "price": 120},
#         {"name": "Strawberry Delight", "price": 120},
#         {"name": "Blueberry Delight", "price": 130}
#     ],
#     "fruits": [
#         {"name": "Banana", "price": 50, "unit": "kg"},
#         {"name": "Apple", "price": 80, "unit": "kg"}
#     ],
#     "others": [
#         {"name": "Hand Gloves", "price": 50, "unit": "pack"}
#     ]
# }

# def is_store_open():
#     """Check if store is within operational hours"""
#     now = datetime.now()
#     # Always open for internal system
#     return True

# def handle_greeting(sender):
#     """Handle greeting messages"""
#     log_user_activity(sender, "greeting_received", "User greeted the bot")
    
#     # Reset user state
#     set_user_state(sender, {
#         "step": "select_branch",
#         "branch": None,
#         "cart": [],
#         "total": 0
#     })
    
#     # Send branch selection menu
#     sections = [{
#         "title": "Select Branch",
#         "rows": [
#             {"id": f"branch_{branch}", "title": branch.title(), "description": ""}
#             for branch in BRANCHES
#         ]
#     }]
    
#     send_interactive_list_message(
#         sender,
#         "🍴 Central Kitchen Ordering",
#         "Welcome to the Central Kitchen Ordering System!\n\nPlease select your branch:",
#         "Select your branch from the list",
#         "Choose Branch",
#         sections
#     )

# def handle_branch_selection(sender, branch):
#     """Handle branch selection"""
#     log_user_activity(sender, "branch_selected", f"Branch: {branch}")
    
#     # Update user state with selected branch
#     state = get_user_state(sender)
#     state["step"] = "browse_menu"
#     state["branch"] = branch
#     set_user_state(sender, state)
    
#     # Send menu categories
#     sections = [{
#         "title": "Menu Categories",
#         "rows": [
#             {"id": "category_custard", "title": "Custard Products", "description": "Custard cans, mango custard, oatmeal"},
#             {"id": "category_delights", "title": "Delights", "description": "Apricot, strawberry, blueberry"},
#             {"id": "category_fruits", "title": "Fruits", "description": "Banana, apple"},
#             {"id": "category_others", "title": "Other Items", "description": "Hand gloves, etc."}
#         ]
#     }]
    
#     send_interactive_list_message(
#         sender,
#         "🍽️ Menu Categories",
#         f"You've selected *{branch.title()}* branch.\n\nPlease choose a menu category:",
#         "Select a category to view items",
#         "Browse Menu",
#         sections
#     )

# def handle_menu_category(sender, category):
#     """Handle menu category selection"""
#     log_user_activity(sender, "category_selected", f"Category: {category}")
    
#     # Extract category name from the button ID
#     category_name = category.replace("category_", "")
    
#     # Get products for this category
#     products = PRODUCT_CATALOG.get(category_name, [])
    
#     if not products:
#         send_text_message(sender, "❌ Sorry, no products found in this category.")
#         return
    
#     # Create product list
#     sections = [{
#         "title": f"{category_name.title()} Items",
#         "rows": [
#             {
#                 "id": f"product_{product['name'].lower().replace(' ', '_')}",
#                 "title": f"{product['name']} - Rs. {product['price']}",
#                 "description": f"Price per {product.get('unit', 'unit')}" if 'unit' in product else ""
#             }
#             for product in products
#         ]
#     }]
    
#     send_interactive_list_message(
#         sender,
#         f"🛒 {category_name.title()} Menu",
#         f"Here are the available {category_name} items:",
#         "Select an item to add to your cart",
#         "Add to Cart",
#         sections
#     )

# def handle_product_selection(sender, product_name):
#     """Handle product selection"""
#     log_user_activity(sender, "product_selected", f"Product: {product_name}")
    
#     # Clean product name
#     product_name = product_name.replace("product_", "").replace("_", " ").title()
    
#     # Find the product in catalog
#     selected_product = None
#     for category, products in PRODUCT_CATALOG.items():
#         for product in products:
#             if product["name"].lower() == product_name.lower():
#                 selected_product = product
#                 break
#         if selected_product:
#             break
    
#     if not selected_product:
#         send_text_message(sender, "❌ Sorry, this product is no longer available.")
#         return
    
#     # Update user state to request quantity
#     state = get_user_state(sender)
#     state["step"] = "enter_quantity"
#     state["selected_product"] = selected_product
#     set_user_state(sender, state)
    
#     # Ask for quantity
#     prompt = f"🔢 *{selected_product['name']}*\n\nPrice: Rs. {selected_product['price']}"
#     if 'unit' in selected_product:
#         prompt += f" per {selected_product['unit']}"
#     prompt += "\n\nPlease enter the quantity:"
    
#     send_text_message(sender, prompt)

# def handle_quantity_input(sender, quantity_str, state):
#     """Handle quantity input"""
#     try:
#         quantity = int(quantity_str)
#         if quantity <= 0:
#             raise ValueError("Quantity must be positive")
#     except ValueError as e:
#         send_text_message(sender, f"❌ Invalid quantity. {str(e)}\n\nPlease enter a valid number:")
#         return
    
#     # Get selected product from state
#     selected_product = state.get("selected_product")
#     if not selected_product:
#         send_text_message(sender, "❌ Error: No product selected. Please start over.")
#         delete_user_state(sender)
#         return
    
#     # Add to cart
#     cart = add_to_cart(
#         sender,
#         selected_product["name"],
#         quantity,
#         selected_product["price"]
#     )
    
#     # Format cart summary
#     cart_summary = "🛒 *Your Cart*\n\n"
#     for item in cart:
#         item_total = item["quantity"] * item["price"]
#         cart_summary += f"- {item['item']} x{item['quantity']}"
#         if 'unit' in selected_product:
#             cart_summary += f" ({selected_product['unit']})"
#         cart_summary += f": Rs. {item_total}\n"
    
#     # Calculate total
#     total = sum(item["quantity"] * item["price"] for item in cart)
#     cart_summary += f"\n*Total:* Rs. {total}"
    
#     # Send cart summary with options
#     buttons = ["Continue Shopping", "View Cart", "Place Order"]
#     send_interactive_button_message(
#         sender,
#         cart_summary,
#         buttons
#     )
    
#     # Update user state
#     state["step"] = "cart_options"
#     set_user_state(sender, state)

# def handle_cart_options(sender, option, state):
#     """Handle cart options"""
#     log_user_activity(sender, "cart_option_selected", f"Option: {option}")
    
#     if option == "continue shopping":
#         # Show menu categories again
#         sections = [{
#             "title": "Menu Categories",
#             "rows": [
#                 {"id": "category_custard", "title": "Custard Products", "description": "Custard cans, mango custard, oatmeal"},
#                 {"id": "category_delights", "title": "Delights", "description": "Apricot, strawberry, blueberry"},
#                 {"id": "category_fruits", "title": "Fruits", "description": "Banana, apple"},
#                 {"id": "category_others", "title": "Other Items", "description": "Hand gloves, etc."}
#             ]
#         }]
        
#         send_interactive_list_message(
#             sender,
#             "🍽️ Menu Categories",
#             "Please choose a menu category:",
#             "Select a category to view items",
#             "Browse Menu",
#             sections
#         )
        
#         state["step"] = "browse_menu"
#         set_user_state(sender, state)
    
#     elif option == "view cart":
#         # Show cart contents
#         cart = get_user_cart(sender)
#         if not cart:
#             send_text_message(sender, "🛒 Your cart is empty.")
#             return
        
#         cart_summary = "🛒 *Your Cart*\n\n"
#         for item in cart:
#             item_total = item["quantity"] * item["price"]
#             cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
        
#         # Calculate total
#         total = sum(item["quantity"] * item["price"] for item in cart)
#         cart_summary += f"\n*Total:* Rs. {total}"
        
#         # Send cart with options to modify
#         buttons = ["Continue Shopping", "Clear Cart", "Place Order"]
#         send_interactive_button_message(
#             sender,
#             cart_summary,
#             buttons
#         )
        
#         state["step"] = "cart_options"
#         set_user_state(sender, state)
    
#     elif option == "clear cart":
#         # Clear the cart
#         clear_user_cart(sender)
#         send_text_message(sender, "✅ Your cart has been cleared.")
        
#         # Show menu categories again
#         sections = [{
#             "title": "Menu Categories",
#             "rows": [
#                 {"id": "category_custard", "title": "Custard Products", "description": "Custard cans, mango custard, oatmeal"},
#                 {"id": "category_delights", "title": "Delights", "description": "Apricot, strawberry, blueberry"},
#                 {"id": "category_fruits", "title": "Fruits", "description": "Banana, apple"},
#                 {"id": "category_others", "title": "Other Items", "description": "Hand gloves, etc."}
#             ]
#         }]
        
#         send_interactive_list_message(
#             sender,
#             "🍽️ Menu Categories",
#             "Your cart is now empty. Please choose a menu category:",
#             "Select a category to view items",
#             "Browse Menu",
#             sections
#         )
        
#         state["step"] = "browse_menu"
#         set_user_state(sender, state)
    
#     elif option == "place order":
#         # Process the order
#         branch = state.get("branch")
#         if not branch:
#             send_text_message(sender, "❌ Error: No branch selected. Please start over.")
#             delete_user_state(sender)
#             return
        
#         success, response = process_order(sender, branch)
        
#         if success:
#             send_text_message(sender, f"✅ Order #{response} placed successfully!")
#             # Clear user state after order placement
#             delete_user_state(sender)
#         else:
#             send_text_message(sender, response)

# def handle_status_check(sender):
#     """Handle order status check"""
#     log_user_activity(sender, "status_check_requested", "User checked order status")
    
#     # In a real implementation, you would fetch user's orders
#     # For now, we'll prompt for order ID
#     send_text_message(sender, "🔍 Please enter your order ID to check status (e.g., FCT0123):")
    
#     # Update user state
#     state = get_user_state(sender)
#     state["step"] = "enter_order_id"
#     set_user_state(sender, state)

# def handle_order_id_input(sender, order_id, state):
#     """Handle order ID input for status check"""
#     log_user_activity(sender, "order_id_entered", f"Order ID: {order_id}")
    
#     # Clean order ID
#     order_id = order_id.upper().replace("#", "")
    
#     # In a real implementation, you would validate and fetch the order
#     # For demo, we'll assume it exists
#     from services.order_service import get_order_status
#     order_status = get_order_status(order_id)
    
#     if order_status and order_status.get("customer_number") == sender:
#         status_msg = f"📋 *Order Status*\n\nOrder ID: #{order_id}\nBranch: {order_status['branch'].title()}\nStatus: {order_status['status'].title()}"
        
#         if "notes" in order_status:
#             status_msg += f"\n\n*Notes:* {order_status['notes']}"
        
#         send_text_message(sender, status_msg)
#     else:
#         send_text_message(sender, "❌ Order not found or you don't have permission to view this order.")
    
#     # Reset state
#     state["step"] = "start"
#     set_user_state(sender, state)

# def handle_status_update(sender, status_command):
#     """Handle status update commands from staff"""
#     log_user_activity(sender, "status_update_requested", f"Command: {status_command}")
    
#     # Parse command: "ready #FCT0123" or "delivered #FCT0123"
#     parts = status_command.split()
#     if len(parts) < 2:
#         send_text_message(sender, "❌ Invalid command format. Use: [status] [order_id]")
#         return
    
#     status = parts[0].lower()
#     order_id = parts[1].replace("#", "").upper()
    
#     # Validate status
#     valid_statuses = ["ready", "delivered", "cancelled"]
#     if status not in valid_statuses:
#         send_text_message(sender, f"❌ Invalid status. Valid statuses: {', '.join(valid_statuses)}")
#         return
    
#     # Update order status
#     from services.order_service import update_order_status_internal
#     success = update_order_status_internal(order_id, status)
    
#     if success:
#         send_text_message(sender, f"✅ Order #{order_id} status updated to '{status}'.")
#     else:
#         send_text_message(sender, f"❌ Failed to update order #{order_id} status.")

# def handle_day_completion(sender):
#     """Handle day completion command from Krishna"""
#     log_user_activity(sender, "day_completion_requested", "User marked day as completed")
    
#     # In a real implementation, you would check if all orders are delivered
#     # For now, we'll just send a confirmation
#     send_text_message(sender, "✅ Day marked as completed. All orders have been processed.")
    
#     # You might also want to trigger end-of-day processes
#     from services.order_service import send_daily_delivery_list, send_production_lists
#     send_daily_delivery_list()
#     send_production_lists()

# def handle_incoming_message(data):
#     """Handle incoming WhatsApp messages"""
#     print("[MESSAGE HANDLER] Received data:", data)
#     log_user_activity("system", "message_received", "New message received")
    
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
#                     log_user_activity(sender, "message_received", text)
                
#                 # Get current state
#                 current_state = get_user_state(sender)
#                 print("[CURRENT STATE]: ", current_state)
                
#                 # TEXT MESSAGE HANDLING
#                 if message_type == "text":
#                     text = msg.get("text", {}).get("body", "").strip().lower()
                    
#                     # Greeting messages
#                     if text in ["hi", "hello", "hey", "menu", "start"]:
#                         handle_greeting(sender)
                    
#                     # Status check
#                     elif text in ["status", "check status", "my order"]:
#                         handle_status_check(sender)
                    
#                     # Day completion (for Krishna)
#                     elif text == "day completed" and sender == "919391727848":  # Krishna's number
#                         handle_day_completion(sender)
                    
#                     # Status update commands (for kitchen staff)
#                     elif any(text.startswith(status) for status in ["ready", "delivered", "cancelled"]):
#                         handle_status_update(sender, text)
                    
#                     # Handle based on current step
#                     elif current_state.get("step") == "select_branch":
#                         # Extract branch from the message
#                         for branch in BRANCHES:
#                             if branch in text:
#                                 handle_branch_selection(sender, branch)
#                                 break
                    
#                     elif current_state.get("step") == "browse_menu":
#                         # Handle category selection
#                         if "custard" in text:
#                             handle_menu_category(sender, "category_custard")
#                         elif "delight" in text:
#                             handle_menu_category(sender, "category_delights")
#                         elif "fruit" in text:
#                             handle_menu_category(sender, "category_fruits")
#                         elif "other" in text or "glove" in text:
#                             handle_menu_category(sender, "category_others")
                    
#                     elif current_state.get("step") == "enter_quantity":
#                         handle_quantity_input(sender, text, current_state)
                    
#                     elif current_state.get("step") == "cart_options":
#                         # Map button text to internal options
#                         option_map = {
#                             "continue shopping": "continue shopping",
#                             "view cart": "view cart",
#                             "clear cart": "clear cart",
#                             "place order": "place order"
#                         }
                        
#                         for btn_text, option in option_map.items():
#                             if btn_text in text:
#                                 handle_cart_options(sender, option, current_state)
#                                 break
                    
#                     elif current_state.get("step") == "enter_order_id":
#                         handle_order_id_input(sender, text, current_state)
                    
#                     else:
#                         # Default response for unrecognized messages
#                         send_text_message(sender, "I didn't understand that. Reply with 'menu' to start ordering or 'status' to check your order.")
                
#                 # INTERACTIVE MESSAGE HANDLING (list selections)
#                 elif message_type == "interactive":
#                     interactive_type = msg.get("interactive", {}).get("type")
                    
#                     if interactive_type == "list_reply":
#                         selected_id = msg.get("interactive", {}).get("list_reply", {}).get("id", "")
                        
#                         if selected_id.startswith("branch_"):
#                             branch = selected_id.replace("branch_", "")
#                             handle_branch_selection(sender, branch)
                        
#                         elif selected_id.startswith("category_"):
#                             handle_menu_category(sender, selected_id)
                        
#                         elif selected_id.startswith("product_"):
#                             handle_product_selection(sender, selected_id)
                    
#                     elif interactive_type == "button_reply":
#                         selected_id = msg.get("interactive", {}).get("button_reply", {}).get("id", "")
                        
#                         if selected_id.startswith("btn_"):
#                             # Get the button index
#                             btn_idx = int(selected_id.replace("btn_", ""))
                            
#                             # Map to cart options
#                             cart_options = ["continue shopping", "view cart", "place order"]
#                             if btn_idx < len(cart_options):
#                                 handle_cart_options(sender, cart_options[btn_idx], current_state)
                
#                 # ORDER MESSAGE HANDLING
#                 elif message_type == "order":
#                     # This would handle actual WhatsApp order messages
#                     # For our system, we're using the interactive flow instead
#                     send_text_message(sender, "Thanks for your order! Please use the menu to place your order.")
                
#                 # LOCATION MESSAGE HANDLING
#                 elif message_type == "location":
#                     # In a real implementation, you might use location for delivery
#                     # For internal system, we don't need this
#                     send_text_message(sender, "📍 Location received. For internal orders, please select your branch from the menu.")
        
#         return "OK", 200
#     except Exception as e:
#         import traceback
#         print("[ERROR] Message handler error:\n", traceback.format_exc())
#         log_user_activity("system", "error", f"Message handler error: {str(e)}")
#         return "Error processing message", 500




# # handlers/message_handler.py
# import csv
# from config.credentials import GOOGLE_MAPS_API_KEY
# from config.settings import BRANCHES, PAYMENT_BRANCHES, CUT_OFF_HOUR
# from services.whatsapp_service import (
#     send_text_message, send_interactive_list_message,
#     send_interactive_button_message, send_order_confirmation
# )
# from stateHandlers.redis_state import (
#     get_user_state, set_user_state, delete_user_state,
#     get_user_cart, add_to_cart, remove_from_cart,
#     clear_user_cart, get_pending_order
# )
# from services.order_service import process_order, update_order_status_internal
# from utils.logger import log_user_activity
# from datetime import datetime, timedelta
# import re

# # Product catalog based on your exact product list
# PRODUCT_CATALOG = {
#     "fruits": [
#         {"id": 1, "name": "Apple 1kg", "price": 100},
#         {"id": 2, "name": "Avacado 1pc", "price": 200},
#         {"id": 7, "name": "Pineapple", "price": 60},
#         {"id": 8, "name": "Papaya 1psc", "price": 70},
#         {"id": 10, "name": "Watermelon 1pc", "price": 60},
#         {"id": 18, "name": "Muskmelon 1psc", "price": 50},
#         {"id": 16, "name": "Cashew 1kg", "price": 52},
#         {"id": 22, "name": "Kiwi 3psc", "price": 90},
#         {"id": 30, "name": "Walnut 250g", "price": 200}
#     ],
#     "custard_products": [
#         {"id": 14, "name": "Custard - 1 can", "price": 40, "description": "Thick and Creamy Custard"},
#         {"id": 24, "name": "Fruit Custard", "price": 760},
#         {"id": 27, "name": "Mangoo custard - 1 kg", "price": 780}
#     ],
#     "packaging_supplies": [
#         {"id": 6, "name": "Paper bowl for fruit bowl 350ML", "price": 100},
#         {"id": 9, "name": "Glass jars reg 72 pcs with caps", "price": 80},
#         {"id": 15, "name": "Sandwich packing box (pack of 50)", "price": 51},
#         {"id": 19, "name": "Glass jar caps pack of 50", "price": 67},
#         {"id": 20, "name": "Fork 14cm", "price": 68},
#         {"id": 11, "name": "Head Cap Pack Of 100", "price": 90},
#         {"id": 17, "name": "Waste cloth pack of 5", "price": 43},
#         {"id": 12, "name": "Party pack boxes", "price": 300},
#         {"id": 28, "name": "Family pack container", "price": 540},
#         {"id": 29, "name": "Caps", "price": 300},
#         {"id": 31, "name": "Custard post cards", "price": 220},
#         {"id": 32, "name": "Glass jars mini 80 pcs", "price": 230}
#     ],
#     "food_items": [
#         {"id": 3, "name": "Choco chips packet", "price": 300},
#         {"id": 13, "name": "Mayonnaise 1Kg", "price": 20},
#         {"id": 25, "name": "Honey 1kg", "price": 900},
#         {"id": 21, "name": "Oreo biscuit", "price": 69},
#         {"id": 23, "name": "Ice pops (pack of 20)", "price": 100}
#     ],
#     "other_supplies": [
#         {"id": 4, "name": "Tissues (10 pack)", "price": 400},
#         {"id": 5, "name": "Sandwich kit (all vegetables)", "price": 500}
#     ]
# }

# # Category display names for user-friendly presentation
# CATEGORY_DISPLAY_NAMES = {
#     "fruits": "Fruits",
#     "custard_products": "Custard Products",
#     "packaging_supplies": "Packaging Supplies",
#     "food_items": "Food Items",
#     "other_supplies": "Other Supplies"
# }

# def is_store_open():
#     """Check if store is within operational hours"""
#     now = datetime.now()
#     # Always open for internal system
#     return True

# def handle_greeting(sender):
#     """Handle greeting messages and catalog-initiated orders"""
#     log_user_activity(sender, "greeting_received", "User greeted the bot or initiated from catalog")
    
#     # Get current state
#     state = get_user_state(sender)
    
#     # Check if there are pending catalog items to process
#     pending_catalog_items = state.get("pending_catalog_items", [])
    
#     # Reset user state but keep pending catalog items
#     new_state = {
#         "step": "select_branch",
#         "branch": None,
#         "cart": [],
#         "total": 0
#     }
    
#     if pending_catalog_items:
#         new_state["pending_catalog_items"] = pending_catalog_items
    
#     set_user_state(sender, new_state)
    
#     # Send branch selection menu
#     sections = [{
#         "title": "Select Branch",
#         "rows": [
#             {"id": f"branch_{branch}", "title": branch.title(), "description": ""}
#             for branch in BRANCHES
#         ]
#     }]
    
#     send_interactive_list_message(
#         sender,
#         "🍴 Central Kitchen Ordering",
#         "Welcome to the Central Kitchen Ordering System!\n\nPlease select your branch:",
#         "Select your branch from the list",
#         "Choose Branch",
#         sections
#     )

# def handle_branch_selection(sender, branch):
#     """Handle branch selection and process any pending catalog items"""
#     log_user_activity(sender, "branch_selected", f"Branch: {branch}")
    
#     # Update user state with selected branch
#     state = get_user_state(sender)
#     state["step"] = "browse_menu"
#     state["branch"] = branch
    
#     # Check if there are pending catalog items to add
#     pending_catalog_items = state.get("pending_catalog_items", [])
#     if pending_catalog_items:
#         # Add the pending catalog items to cart
#         for item in pending_catalog_items:
#             product_id = item.get("product_retailer_id")
#             # Find the product in our catalog
#             product = None
#             for category, products in PRODUCT_CATALOG.items():
#                 for p in products:
#                     if str(p["id"]) == product_id:
#                         product = p
#                         break
#                 if product:
#                     break
            
#             if product:
#                 add_to_cart(sender, product["name"], item["quantity"], product["price"])
        
#         # Clear pending items
#         if "pending_catalog_items" in state:
#             del state["pending_catalog_items"]
        
#         # Show cart summary after adding items
#         cart = get_user_cart(sender)
#         cart_summary = "🛒 *Your Cart*\n\n"
#         for item in cart:
#             item_total = item["quantity"] * item["price"]
#             cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
        
#         # Calculate total
#         total = sum(item["quantity"] * item["price"] for item in cart)
#         cart_summary += f"\n*Total:* Rs. {total}"
        
#         # Send cart summary with options
#         buttons = ["Continue Shopping", "View Cart", "Place Order"]
#         send_interactive_button_message(
#             sender,
#             cart_summary,
#             buttons
#         )
        
#         state["step"] = "cart_options"
#         set_user_state(sender, state)
#         return
    
#     # If no pending catalog items, send menu categories
#     sections = [{
#         "title": "Menu Categories",
#         "rows": [
#             {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#             for cat in PRODUCT_CATALOG.keys()
#         ]
#     }]
    
#     send_interactive_list_message(
#         sender,
#         "🍽️ Menu Categories",
#         f"You've selected *{branch.title()}* branch.\n\nPlease choose a menu category:",
#         "Select a category to view items",
#         "Browse Menu",
#         sections
#     )
    
#     set_user_state(sender, state)

# def handle_menu_category(sender, category):
#     """Handle menu category selection"""
#     log_user_activity(sender, "category_selected", f"Category: {category}")
    
#     # Extract category name from the button ID
#     category_name = category.replace("category_", "")
    
#     # Get products for this category
#     products = PRODUCT_CATALOG.get(category_name, [])
    
#     if not products:
#         send_text_message(sender, "❌ Sorry, no products found in this category.")
#         # Send back to category selection
#         sections = [{
#             "title": "Menu Categories",
#             "rows": [
#                 {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                 for cat in PRODUCT_CATALOG.keys()
#             ]
#         }]
        
#         send_interactive_list_message(
#             sender,
#             "🍽️ Menu Categories",
#             "Please choose a menu category:",
#             "Select a category to view items",
#             "Browse Menu",
#             sections
#         )
#         return
    
#     # Create product list
#     sections = [{
#         "title": f"{CATEGORY_DISPLAY_NAMES.get(category_name, category_name).title()} Items",
#         "rows": [
#             {
#                 "id": f"product_{product['id']}",
#                 "title": f"{product['name']} - Rs. {product['price']}",
#                 "description": product.get('description', '')[:50]  # Limit description length
#             }
#             for product in products
#         ]
#     }]
    
#     send_interactive_list_message(
#         sender,
#         f"🛒 {CATEGORY_DISPLAY_NAMES.get(category_name, category_name).title()} Menu",
#         f"Here are the available items in {CATEGORY_DISPLAY_NAMES.get(category_name, category_name).lower()}:",
#         "Select an item to add to your cart",
#         "Add to Cart",
#         sections
#     )

# def handle_product_selection(sender, product_id):
#     """Handle product selection"""
#     log_user_activity(sender, "product_selected", f"Product ID: {product_id}")
    
#     # Find the product in catalog
#     selected_product = None
#     for category, products in PRODUCT_CATALOG.items():
#         for product in products:
#             if str(product["id"]) == product_id:
#                 selected_product = product
#                 break
#         if selected_product:
#             break
    
#     if not selected_product:
#         send_text_message(sender, "❌ Sorry, this product is no longer available.")
#         # Return to category selection
#         sections = [{
#             "title": "Menu Categories",
#             "rows": [
#                 {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                 for cat in PRODUCT_CATALOG.keys()
#             ]
#         }]
        
#         send_interactive_list_message(
#             sender,
#             "🍽️ Menu Categories",
#             "Please choose a menu category:",
#             "Select a category to view items",
#             "Browse Menu",
#             sections
#         )
#         return
    
#     # Update user state to request quantity
#     state = get_user_state(sender)
#     state["step"] = "enter_quantity"
#     state["selected_product"] = selected_product
#     set_user_state(sender, state)
    
#     # Ask for quantity
#     prompt = f"🔢 *{selected_product['name']}*\n\nPrice: Rs. {selected_product['price']}"
#     if 'description' in selected_product:
#         prompt += f"\n\n{selected_product['description']}"
#     prompt += "\n\nPlease enter the quantity:"
    
#     send_text_message(sender, prompt)

# def handle_quantity_input(sender, quantity_str, state):
#     """Handle quantity input"""
#     try:
#         quantity = int(quantity_str)
#         if quantity <= 0:
#             raise ValueError("Quantity must be positive")
#     except ValueError as e:
#         send_text_message(sender, f"❌ Invalid quantity. {str(e)}\n\nPlease enter a valid number:")
#         return
    
#     # Get selected product from state
#     selected_product = state.get("selected_product")
#     if not selected_product:
#         send_text_message(sender, "❌ Error: No product selected. Please start over.")
#         delete_user_state(sender)
#         return
    
#     # Add to cart
#     cart = add_to_cart(
#         sender,
#         selected_product["name"],
#         quantity,
#         selected_product["price"]
#     )
    
#     # Format cart summary
#     cart_summary = "🛒 *Your Cart*\n\n"
#     for item in cart:
#         item_total = item["quantity"] * item["price"]
#         cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
    
#     # Calculate total
#     total = sum(item["quantity"] * item["price"] for item in cart)
#     cart_summary += f"\n*Total:* Rs. {total}"
    
#     # Send cart summary with options
#     buttons = ["Continue Shopping", "View Cart", "Place Order"]
#     send_interactive_button_message(
#         sender,
#         cart_summary,
#         buttons
#     )
    
#     # Update user state
#     state["step"] = "cart_options"
#     set_user_state(sender, state)

# def handle_cart_options(sender, option, state):
#     """Handle cart options"""
#     log_user_activity(sender, "cart_option_selected", f"Option: {option}")
    
#     if option == "continue shopping":
#         # Show menu categories again
#         sections = [{
#             "title": "Menu Categories",
#             "rows": [
#                 {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                 for cat in PRODUCT_CATALOG.keys()
#             ]
#         }]
        
#         send_interactive_list_message(
#             sender,
#             "🍽️ Menu Categories",
#             "Please choose a menu category:",
#             "Select a category to view items",
#             "Browse Menu",
#             sections
#         )
        
#         state["step"] = "browse_menu"
#         set_user_state(sender, state)
    
#     elif option == "view cart":
#         # Show cart contents
#         cart = get_user_cart(sender)
#         if not cart:
#             send_text_message(sender, "🛒 Your cart is empty.")
#             # Return to menu
#             sections = [{
#                 "title": "Menu Categories",
#                 "rows": [
#                     {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                     for cat in PRODUCT_CATALOG.keys()
#                 ]
#             }]
            
#             send_interactive_list_message(
#                 sender,
#                 "🍽️ Menu Categories",
#                 "Please choose a menu category:",
#                 "Select a category to view items",
#                 "Browse Menu",
#                 sections
#             )
#             state["step"] = "browse_menu"
#             set_user_state(sender, state)
#             return
        
#         cart_summary = "🛒 *Your Cart*\n\n"
#         for item in cart:
#             item_total = item["quantity"] * item["price"]
#             cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
        
#         # Calculate total
#         total = sum(item["quantity"] * item["price"] for item in cart)
#         cart_summary += f"\n*Total:* Rs. {total}"
        
#         # Send cart with options to modify
#         buttons = ["Continue Shopping", "Clear Cart", "Place Order"]
#         send_interactive_button_message(
#             sender,
#             cart_summary,
#             buttons
#         )
        
#         state["step"] = "cart_options"
#         set_user_state(sender, state)
    
#     elif option == "clear cart":
#         # Clear the cart
#         clear_user_cart(sender)
#         send_text_message(sender, "✅ Your cart has been cleared.")
        
#         # Show menu categories again
#         sections = [{
#             "title": "Menu Categories",
#             "rows": [
#                 {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                 for cat in PRODUCT_CATALOG.keys()
#             ]
#         }]
        
#         send_interactive_list_message(
#             sender,
#             "🍽️ Menu Categories",
#             "Your cart is now empty. Please choose a menu category:",
#             "Select a category to view items",
#             "Browse Menu",
#             sections
#         )
        
#         state["step"] = "browse_menu"
#         set_user_state(sender, state)
    
#     elif option == "place order":
#         # Process the order
#         branch = state.get("branch")
#         if not branch:
#             send_text_message(sender, "❌ Error: No branch selected. Please start over.")
#             delete_user_state(sender)
#             return
        
#         success, response = process_order(sender, branch)
        
#         if success:
#             send_text_message(sender, f"✅ Order #{response} placed successfully!")
#             # Clear user state after order placement
#             delete_user_state(sender)
#         else:
#             send_text_message(sender, response)

# def handle_status_check(sender):
#     """Handle order status check"""
#     log_user_activity(sender, "status_check_requested", "User checked order status")
    
#     # In a real implementation, you would fetch user's orders
#     # For now, we'll prompt for order ID
#     send_text_message(sender, "🔍 Please enter your order ID to check status (e.g., FCT0123):")
    
#     # Update user state
#     state = get_user_state(sender)
#     state["step"] = "enter_order_id"
#     set_user_state(sender, state)

# def handle_order_id_input(sender, order_id, state):
#     """Handle order ID input for status check"""
#     log_user_activity(sender, "order_id_entered", f"Order ID: {order_id}")
    
#     # Clean order ID
#     order_id = order_id.upper().replace("#", "")
    
#     # In a real implementation, you would validate and fetch the order
#     # For demo, we'll assume it exists
#     from services.order_service import get_order_status
#     order_status = get_order_status(order_id)
    
#     if order_status and order_status.get("customer_number") == sender:
#         status_msg = f"📋 *Order Status*\n\nOrder ID: #{order_id}\nBranch: {order_status['branch'].title()}\nStatus: {order_status['status'].title()}"
        
#         if "notes" in order_status:
#             status_msg += f"\n\n*Notes:* {order_status['notes']}"
        
#         send_text_message(sender, status_msg)
#     else:
#         send_text_message(sender, "❌ Order not found or you don't have permission to view this order.")
    
#     # Reset state
#     state["step"] = "start"
#     set_user_state(sender, state)

# def handle_status_update(sender, status_command):
#     """Handle status update commands from staff"""
#     log_user_activity(sender, "status_update_requested", f"Command: {status_command}")
    
#     # Parse command: "ready #FCT0123" or "delivered #FCT0123"
#     parts = status_command.split()
#     if len(parts) < 2:
#         send_text_message(sender, "❌ Invalid command format. Use: [status] [order_id]")
#         return
    
#     status = parts[0].lower()
#     order_id = parts[1].replace("#", "").upper()
    
#     # Validate status
#     valid_statuses = ["ready", "delivered", "cancelled"]
#     if status not in valid_statuses:
#         send_text_message(sender, f"❌ Invalid status. Valid statuses: {', '.join(valid_statuses)}")
#         return
    
#     # Update order status
#     from services.order_service import update_order_status_internal
#     success = update_order_status_internal(order_id, status)
    
#     if success:
#         send_text_message(sender, f"✅ Order #{order_id} status updated to '{status}'.")
#     else:
#         send_text_message(sender, f"❌ Failed to update order #{order_id} status.")

# def handle_day_completion(sender):
#     """Handle day completion command from Krishna"""
#     log_user_activity(sender, "day_completion_requested", "User marked day as completed")
    
#     # In a real implementation, you would check if all orders are delivered
#     # For now, we'll just send a confirmation
#     send_text_message(sender, "✅ Day marked as completed. All orders have been processed.")
    
#     # You might also want to trigger end-of-day processes
#     from services.order_service import send_daily_delivery_list, send_production_lists
#     send_daily_delivery_list()
#     send_production_lists()

# def handle_catalog_order(sender, items):
#     """Handle orders placed directly from WhatsApp catalog"""
#     log_user_activity(sender, "catalog_order_received", f"Received {len(items)} items from catalog")
    
#     # Get current state
#     state = get_user_state(sender)
    
#     # Store catalog items for later processing
#     state["pending_catalog_items"] = items
#     set_user_state(sender, state)
    
#     # Start the ordering process
#     handle_greeting(sender)

# def handle_incoming_message(data):
#     """Handle incoming WhatsApp messages"""
#     print("[MESSAGE HANDLER] Received data:", data)
#     log_user_activity("system", "message_received", "New message received")
    
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
#                     log_user_activity(sender, "message_received", text)
                
#                 # Get current state
#                 current_state = get_user_state(sender)
#                 print("[CURRENT STATE]: ", current_state)
                
#                 # TEXT MESSAGE HANDLING
#                 if message_type == "text":
#                     text = msg.get("text", {}).get("body", "").strip().lower()
                    
#                     # Greeting messages
#                     if text in ["hi", "hello", "hey", "menu", "start"]:
#                         handle_greeting(sender)
                    
#                     # Status check
#                     elif text in ["status", "check status", "my order"]:
#                         handle_status_check(sender)
                    
#                     # Day completion (for Krishna)
#                     elif text == "day completed" and sender == "919391727848":  # Krishna's number
#                         handle_day_completion(sender)
                    
#                     # Status update commands (for kitchen staff)
#                     elif any(text.startswith(status) for status in ["ready", "delivered", "cancelled"]):
#                         handle_status_update(sender, text)
                    
#                     # Handle based on current step
#                     elif current_state.get("step") == "select_branch":
#                         # Extract branch from the message
#                         for branch in BRANCHES:
#                             if branch in text:
#                                 handle_branch_selection(sender, branch)
#                                 break
#                         else:
#                             # If no branch matched, send branch selection again
#                             handle_greeting(sender)
                    
#                     elif current_state.get("step") == "browse_menu":
#                         # Handle category selection
#                         if "custard" in text or "custard products" in text:
#                             handle_menu_category(sender, "category_custard_products")
#                         elif "delight" in text or "fruit" in text or "mango" in text:
#                             handle_menu_category(sender, "category_custard_products")
#                         elif "packaging" in text or "jar" in text or "bowl" in text or "cap" in text:
#                             handle_menu_category(sender, "category_packaging_supplies")
#                         elif "food" in text or "choco" in text or "honey" in text or "oreo" in text:
#                             handle_menu_category(sender, "category_food_items")
#                         elif "tissue" in text or "sandwich kit" in text:
#                             handle_menu_category(sender, "category_other_supplies")
#                         else:
#                             # If no category matched, send category selection again
#                             sections = [{
#                                 "title": "Menu Categories",
#                                 "rows": [
#                                     {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                                     for cat in PRODUCT_CATALOG.keys()
#                                 ]
#                             }]
                            
#                             send_interactive_list_message(
#                                 sender,
#                                 "🍽️ Menu Categories",
#                                 "Please choose a menu category:",
#                                 "Select a category to view items",
#                                 "Browse Menu",
#                                 sections
#                             )
                    
#                     elif current_state.get("step") == "enter_quantity":
#                         handle_quantity_input(sender, text, current_state)
                    
#                     elif current_state.get("step") == "cart_options":
#                         # Map button text to internal options
#                         option_map = {
#                             "continue shopping": "continue shopping",
#                             "view cart": "view cart",
#                             "clear cart": "clear cart",
#                             "place order": "place order"
#                         }
                        
#                         for btn_text, option in option_map.items():
#                             if btn_text in text:
#                                 handle_cart_options(sender, option, current_state)
#                                 break
#                         else:
#                             # If no option matched, show cart options again
#                             cart = get_user_cart(sender)
#                             if not cart:
#                                 send_text_message(sender, "🛒 Your cart is empty.")
#                                 # Return to menu
#                                 sections = [{
#                                     "title": "Menu Categories",
#                                     "rows": [
#                                         {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
#                                         for cat in PRODUCT_CATALOG.keys()
#                                     ]
#                                 }]
                                
#                                 send_interactive_list_message(
#                                     sender,
#                                     "🍽️ Menu Categories",
#                                     "Please choose a menu category:",
#                                     "Select a category to view items",
#                                     "Browse Menu",
#                                     sections
#                                 )
#                                 current_state["step"] = "browse_menu"
#                                 set_user_state(sender, current_state)
#                             else:
#                                 cart_summary = "🛒 *Your Cart*\n\n"
#                                 for item in cart:
#                                     item_total = item["quantity"] * item["price"]
#                                     cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
                                
#                                 # Calculate total
#                                 total = sum(item["quantity"] * item["price"] for item in cart)
#                                 cart_summary += f"\n*Total:* Rs. {total}"
                                
#                                 # Send cart with options to modify
#                                 buttons = ["Continue Shopping", "Clear Cart", "Place Order"]
#                                 send_interactive_button_message(
#                                     sender,
#                                     cart_summary,
#                                     buttons
#                                 )
                    
#                     elif current_state.get("step") == "enter_order_id":
#                         handle_order_id_input(sender, text, current_state)
                    
#                     else:
#                         # Default response for unrecognized messages
#                         send_text_message(sender, "I didn't understand that. Reply with 'menu' to start ordering or 'status' to check your order.")
                
#                 # INTERACTIVE MESSAGE HANDLING (list selections)
#                 elif message_type == "interactive":
#                     interactive_type = msg.get("interactive", {}).get("type")
                    
#                     if interactive_type == "list_reply":
#                         selected_id = msg.get("interactive", {}).get("list_reply", {}).get("id", "")
                        
#                         if selected_id.startswith("branch_"):
#                             branch = selected_id.replace("branch_", "")
#                             handle_branch_selection(sender, branch)
                        
#                         elif selected_id.startswith("category_"):
#                             handle_menu_category(sender, selected_id)
                        
#                         elif selected_id.startswith("product_"):
#                             handle_product_selection(sender, selected_id)
                    
#                     elif interactive_type == "button_reply":
#                         selected_id = msg.get("interactive", {}).get("button_reply", {}).get("id", "")
                        
#                         if selected_id.startswith("btn_"):
#                             # Get the button index
#                             btn_idx = int(selected_id.replace("btn_", ""))
                            
#                             # Map to cart options
#                             cart_options = ["continue shopping", "view cart", "place order"]
#                             if btn_idx < len(cart_options):
#                                 handle_cart_options(sender, cart_options[btn_idx], current_state)
                
#                 # ORDER MESSAGE HANDLING - This is the critical fix!
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
#         import traceback
#         print("[ERROR] Message handler error:\n", traceback.format_exc())
#         log_user_activity("system", "error", f"Message handler error: {str(e)}")
#         return "Error processing message", 500










# handlers/message_handler.py
import csv
from config.credentials import GOOGLE_MAPS_API_KEY
from config.settings import BRANCHES, PAYMENT_BRANCHES, CUT_OFF_HOUR
from services.whatsapp_service import (
    send_text_message, send_interactive_list_message,
    send_interactive_button_message, send_order_confirmation
)
from stateHandlers.redis_state import (
    get_user_state, set_user_state, delete_user_state,
    get_user_cart, add_to_cart, remove_from_cart,
    clear_user_cart, get_pending_order
)
from services.order_service import process_order, update_order_status_internal
from utils.logger import log_user_activity
from datetime import datetime, timedelta
import re

# Product catalog based on your exact product list
PRODUCT_CATALOG = {
    "fruits": [
        {"id": 1, "name": "Apple 1kg", "price": 100},
        {"id": 2, "name": "Avacado 1pc", "price": 200},
        {"id": 7, "name": "Pineapple", "price": 60},
        {"id": 8, "name": "Papaya 1psc", "price": 70},
        {"id": 10, "name": "Watermelon 1pc", "price": 60},
        {"id": 18, "name": "Muskmelon 1psc", "price": 50},
        {"id": 16, "name": "Cashew 1kg", "price": 52},
        {"id": 22, "name": "Kiwi 3psc", "price": 90},
        {"id": 30, "name": "Walnut 250g", "price": 200}
    ],
    "custard_products": [
        {"id": 14, "name": "Custard - 1 can", "price": 40, "description": "Thick and Creamy Custard"},
        {"id": 24, "name": "Fruit Custard", "price": 760},
        {"id": 27, "name": "Mangoo custard - 1 kg", "price": 780}
    ],
    "packaging_supplies": [
        {"id": 6, "name": "Paper bowl for fruit bowl 350ML", "price": 100},
        {"id": 9, "name": "Glass jars reg 72 pcs with caps", "price": 80},
        {"id": 15, "name": "Sandwich packing box (pack of 50)", "price": 51},
        {"id": 19, "name": "Glass jar caps pack of 50", "price": 67},
        {"id": 20, "name": "Fork 14cm", "price": 68},
        {"id": 11, "name": "Head Cap Pack Of 100", "price": 90},
        {"id": 17, "name": "Waste cloth pack of 5", "price": 43},
        {"id": 12, "name": "Party pack boxes", "price": 300},
        {"id": 28, "name": "Family pack container", "price": 540},
        {"id": 29, "name": "Caps", "price": 300},
        {"id": 31, "name": "Custard post cards", "price": 220},
        {"id": 32, "name": "Glass jars mini 80 pcs", "price": 230}
    ],
    "food_items": [
        {"id": 3, "name": "Choco chips packet", "price": 300},
        {"id": 13, "name": "Mayonnaise 1Kg", "price": 20},
        {"id": 25, "name": "Honey 1kg", "price": 900},
        {"id": 21, "name": "Oreo biscuit", "price": 69},
        {"id": 23, "name": "Ice pops (pack of 20)", "price": 100}
    ],
    "other_supplies": [
        {"id": 4, "name": "Tissues (10 pack)", "price": 400},
        {"id": 5, "name": "Sandwich kit (all vegetables)", "price": 500}
    ]
}

# Category display names for user-friendly presentation
CATEGORY_DISPLAY_NAMES = {
    "fruits": "Fruits",
    "custard_products": "Custard Products",
    "packaging_supplies": "Packaging Supplies",
    "food_items": "Food Items",
    "other_supplies": "Other Supplies"
}

def is_store_open():
    """Check if store is within operational hours"""
    now = datetime.now()
    # Always open for internal system
    return True

def handle_greeting(sender):
    """Handle greeting messages and catalog-initiated orders"""
    log_user_activity(sender, "greeting_received", "User greeted the bot or initiated from catalog")
    
    # Get current state
    state = get_user_state(sender)
    
    # Check if there are pending catalog items to process
    pending_catalog_items = state.get("pending_catalog_items", [])
    
    # Reset user state but keep pending catalog items
    new_state = {
        "step": "select_branch",
        "branch": None,
        "cart": [],
        "total": 0
    }
    
    if pending_catalog_items:
        new_state["pending_catalog_items"] = pending_catalog_items
    
    set_user_state(sender, new_state)
    
    # Send branch selection menu
    sections = [{
        "title": "Select Branch",
        "rows": [
            {"id": f"branch_{branch}", "title": branch.title(), "description": ""}
            for branch in BRANCHES
        ]
    }]
    
    send_interactive_list_message(
        sender,
        "🍴 Central Kitchen Ordering",
        "Welcome to the Central Kitchen Ordering System!\n\nPlease select your branch:",
        "Select your branch from the list",
        "Choose Branch",
        sections
    )

def handle_branch_selection(sender, branch):
    """Handle branch selection and process any pending catalog items"""
    log_user_activity(sender, "branch_selected", f"Branch: {branch}")
    
    # Update user state with selected branch
    state = get_user_state(sender)
    state["step"] = "browse_menu"
    state["branch"] = branch
    
    # Check if there are pending catalog items to add
    pending_catalog_items = state.get("pending_catalog_items", [])
    if pending_catalog_items:
        log_user_activity(sender, "catalog_processing", f"Processing {len(pending_catalog_items)} catalog items")
        
        # Add the pending catalog items to cart
        added_items = 0
        for item in pending_catalog_items:
            product_retailer_id = item.get("product_retailer_id", "")
            # FIX: Clean the ID - remove decimal part if present (convert "10.00" to "10")
            clean_id = product_retailer_id.split('.')[0]
            
            log_user_activity(sender, "catalog_item", f"Processing item ID: {product_retailer_id} -> {clean_id}")
            
            # Find the product in our catalog
            product = None
            for category, products in PRODUCT_CATALOG.items():
                for p in products:
                    if str(p["id"]) == clean_id:
                        product = p
                        break
                if product:
                    break
            
            if product:
                log_user_activity(sender, "catalog_add", f"Adding {product['name']} x{item['quantity']}")
                add_to_cart(sender, product["name"], item["quantity"], product["price"])
                added_items += 1
            else:
                log_user_activity(sender, "catalog_error", f"Product not found: {product_retailer_id}")
        
        # Clear pending items
        if "pending_catalog_items" in state:
            del state["pending_catalog_items"]
            set_user_state(sender, state)
        
        # Show cart summary after adding items
        cart = get_user_cart(sender)
        if not cart:
            log_user_activity(sender, "cart_error", f"No items added from catalog (tried {len(pending_catalog_items)} items)")
            # FIX: Don't show "empty cart" message - instead show menu
            sections = [{
                "title": "Menu Categories",
                "rows": [
                    {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                    for cat in PRODUCT_CATALOG.keys()
                ]
            }]
            
            send_interactive_list_message(
                sender,
                "🍽️ Menu Categories",
                "No matching products found. Please choose a menu category:",
                "Select a category to view items",
                "Browse Menu",
                sections
            )
            state["step"] = "browse_menu"
            set_user_state(sender, state)
            return
        else:
            log_user_activity(sender, "cart_success", f"Added {added_items} items to cart")
            cart_summary = "🛒 *Your Cart*\n\n"
            for item in cart:
                item_total = item["quantity"] * item["price"]
                cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
            
            # Calculate total
            total = sum(item["quantity"] * item["price"] for item in cart)
            cart_summary += f"\n*Total:* Rs. {total}"
            
            # Send cart summary with options
            buttons = ["Continue Shopping", "View Cart", "Place Order"]
            send_interactive_button_message(
                sender,
                cart_summary,
                buttons
            )
            
            state["step"] = "cart_options"
            set_user_state(sender, state)
            return
    
    # If no pending catalog items, send menu categories
    sections = [{
        "title": "Menu Categories",
        "rows": [
            {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
            for cat in PRODUCT_CATALOG.keys()
        ]
    }]
    
    send_interactive_list_message(
        sender,
        "🍽️ Menu Categories",
        f"You've selected *{branch.title()}* branch.\n\nPlease choose a menu category:",
        "Select a category to view items",
        "Browse Menu",
        sections
    )
    
    set_user_state(sender, state)

def handle_menu_category(sender, category):
    """Handle menu category selection with WhatsApp row limit fix"""
    log_user_activity(sender, "category_selected", f"Category: {category}")
    
    # Extract category name from the button ID
    category_name = category.replace("category_", "")
    
    # Get products for this category
    products = PRODUCT_CATALOG.get(category_name, [])
    
    if not products:
        send_text_message(sender, "❌ Sorry, no products found in this category.")
        # Send back to category selection
        sections = [{
            "title": "Menu Categories",
            "rows": [
                {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                for cat in PRODUCT_CATALOG.keys()
            ]
        }]
        
        send_interactive_list_message(
            sender,
            "🍽️ Menu Categories",
            "Please choose a menu category:",
            "Select a category to view items",
            "Browse Menu",
            sections
        )
        return
    
    # FIX: WhatsApp only allows max 10 rows per section
    # Split large categories into multiple sections
    sections = []
    max_rows_per_section = 10
    
    for i in range(0, len(products), max_rows_per_section):
        chunk = products[i:i + max_rows_per_section]
        section_title = f"{CATEGORY_DISPLAY_NAMES.get(category_name, category_name).title()} Items"
        if i > 0:
            section_title += f" (Part {i//max_rows_per_section + 1})"
            
        section = {
            "title": section_title,
            "rows": [
                {
                    "id": f"product_{product['id']}",
                    "title": f"{product['name']} - Rs. {product['price']}",
                    "description": product.get('description', '')[:50]  # Limit description length
                }
                for product in chunk
            ]
        }
        sections.append(section)
    
    # Send interactive message with potentially multiple sections
    send_interactive_list_message(
        sender,
        f"🛒 {CATEGORY_DISPLAY_NAMES.get(category_name, category_name).title()} Menu",
        f"Here are the available items in {CATEGORY_DISPLAY_NAMES.get(category_name, category_name).lower()}:",
        "Select an item to add to your cart",
        "Add to Cart",
        sections
    )

def handle_product_selection(sender, product_id):
    """Handle product selection"""
    log_user_activity(sender, "product_selected", f"Product ID: {product_id}")
    
    # Find the product in catalog
    selected_product = None
    for category, products in PRODUCT_CATALOG.items():
        for product in products:
            if str(product["id"]) == product_id:
                selected_product = product
                break
        if selected_product:
            break
    
    if not selected_product:
        send_text_message(sender, "❌ Sorry, this product is no longer available.")
        # Return to category selection
        sections = [{
            "title": "Menu Categories",
            "rows": [
                {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                for cat in PRODUCT_CATALOG.keys()
            ]
        }]
        
        send_interactive_list_message(
            sender,
            "🍽️ Menu Categories",
            "Please choose a menu category:",
            "Select a category to view items",
            "Browse Menu",
            sections
        )
        return
    
    # Update user state to request quantity
    state = get_user_state(sender)
    state["step"] = "enter_quantity"
    state["selected_product"] = selected_product
    set_user_state(sender, state)
    
    # Ask for quantity
    prompt = f"🔢 *{selected_product['name']}*\n\nPrice: Rs. {selected_product['price']}"
    if 'description' in selected_product:
        prompt += f"\n\n{selected_product['description']}"
    prompt += "\n\nPlease enter the quantity:"
    
    send_text_message(sender, prompt)

def handle_quantity_input(sender, quantity_str, state):
    """Handle quantity input with better cart handling"""
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    except ValueError as e:
        send_text_message(sender, f"❌ Invalid quantity. {str(e)}\n\nPlease enter a valid number:")
        return
    
    # Get selected product from state
    selected_product = state.get("selected_product")
    if not selected_product:
        send_text_message(sender, "❌ Error: No product selected. Please start over.")
        delete_user_state(sender)
        return
    
    # Add to cart
    cart = add_to_cart(
        sender,
        selected_product["name"],
        quantity,
        selected_product["price"]
    )
    
    # Verify cart was updated
    current_cart = get_user_cart(sender)
    log_user_activity(sender, "cart_verification", f"Cart after add: {current_cart}")
    
    # Format cart summary
    cart_summary = "🛒 *Your Cart*\n\n"
    for item in current_cart:
        item_total = item["quantity"] * item["price"]
        cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
    
    # Calculate total
    total = sum(item["quantity"] * item["price"] for item in current_cart)
    cart_summary += f"\n*Total:* Rs. {total}"
    
    # Send cart summary with options
    buttons = ["Continue Shopping", "View Cart", "Place Order"]
    send_interactive_button_message(
        sender,
        cart_summary,
        buttons
    )
    
    # Update user state
    state["step"] = "cart_options"
    set_user_state(sender, state)

def handle_cart_options(sender, option, state):
    """Handle cart options with better cart handling"""
    log_user_activity(sender, "cart_option_selected", f"Option: {option}")
    
    # Always get fresh cart data
    cart = get_user_cart(sender)
    
    if option == "continue shopping":
        # Show menu categories again
        sections = [{
            "title": "Menu Categories",
            "rows": [
                {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                for cat in PRODUCT_CATALOG.keys()
            ]
        }]
        
        send_interactive_list_message(
            sender,
            "🍽️ Menu Categories",
            "Please choose a menu category:",
            "Select a category to view items",
            "Browse Menu",
            sections
        )
        
        state["step"] = "browse_menu"
        set_user_state(sender, state)
    
    elif option == "view cart":
        # Show cart contents
        if not cart:
            send_text_message(sender, "🛒 Your cart is empty.")
            # Return to menu
            sections = [{
                "title": "Menu Categories",
                "rows": [
                    {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                    for cat in PRODUCT_CATALOG.keys()
                ]
            }]
            
            send_interactive_list_message(
                sender,
                "🍽️ Menu Categories",
                "Please choose a menu category:",
                "Select a category to view items",
                "Browse Menu",
                sections
            )
            state["step"] = "browse_menu"
            set_user_state(sender, state)
            return
        
        cart_summary = "🛒 *Your Cart*\n\n"
        for item in cart:
            item_total = item["quantity"] * item["price"]
            cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
        
        # Calculate total
        total = sum(item["quantity"] * item["price"] for item in cart)
        cart_summary += f"\n*Total:* Rs. {total}"
        
        # Send cart with options to modify
        buttons = ["Continue Shopping", "Clear Cart", "Place Order"]
        send_interactive_button_message(
            sender,
            cart_summary,
            buttons
        )
        
        state["step"] = "cart_options"
        set_user_state(sender, state)
    
    elif option == "clear cart":
        # Clear the cart
        clear_user_cart(sender)
        send_text_message(sender, "✅ Your cart has been cleared.")
        
        # Show menu categories again
        sections = [{
            "title": "Menu Categories",
            "rows": [
                {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                for cat in PRODUCT_CATALOG.keys()
            ]
        }]
        
        send_interactive_list_message(
            sender,
            "🍽️ Menu Categories",
            "Your cart is now empty. Please choose a menu category:",
            "Select a category to view items",
            "Browse Menu",
            sections
        )
        
        state["step"] = "browse_menu"
        set_user_state(sender, state)
    
    elif option == "place order":
        # Process the order
        branch = state.get("branch")
        if not branch:
            send_text_message(sender, "❌ Error: No branch selected. Please start over.")
            delete_user_state(sender)
            return
        
        # Get fresh cart data before processing order
        cart = get_user_cart(sender)
        if not cart:
            send_text_message(sender, "❌ Your cart is empty. Please add items before placing an order.")
            # Return to menu
            sections = [{
                "title": "Menu Categories",
                "rows": [
                    {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                    for cat in PRODUCT_CATALOG.keys()
                ]
            }]
            
            send_interactive_list_message(
                sender,
                "🍽️ Menu Categories",
                "Please choose a menu category:",
                "Select a category to view items",
                "Browse Menu",
                sections
            )
            state["step"] = "browse_menu"
            set_user_state(sender, state)
            return
        
        success, response = process_order(sender, branch)
        
        if success:
            send_text_message(sender, f"✅ Order #{response} placed successfully!")
            # Clear user state after order placement
            delete_user_state(sender)
        else:
            send_text_message(sender, response)

def handle_status_check(sender):
    """Handle order status check"""
    log_user_activity(sender, "status_check_requested", "User checked order status")
    
    # In a real implementation, you would fetch user's orders
    # For now, we'll prompt for order ID
    send_text_message(sender, "🔍 Please enter your order ID to check status (e.g., FCT0123):")
    
    # Update user state
    state = get_user_state(sender)
    state["step"] = "enter_order_id"
    set_user_state(sender, state)

def handle_order_id_input(sender, order_id, state):
    """Handle order ID input for status check"""
    log_user_activity(sender, "order_id_entered", f"Order ID: {order_id}")
    
    # Clean order ID
    order_id = order_id.upper().replace("#", "")
    
    # In a real implementation, you would validate and fetch the order
    # For demo, we'll assume it exists
    from services.order_service import get_order_status
    order_status = get_order_status(order_id)
    
    if order_status and order_status.get("customer_number") == sender:
        status_msg = f"📋 *Order Status*\n\nOrder ID: #{order_id}\nBranch: {order_status['branch'].title()}\nStatus: {order_status['status'].title()}"
        
        if "notes" in order_status:
            status_msg += f"\n\n*Notes:* {order_status['notes']}"
        
        send_text_message(sender, status_msg)
    else:
        send_text_message(sender, "❌ Order not found or you don't have permission to view this order.")
    
    # Reset state
    state["step"] = "start"
    set_user_state(sender, state)

def handle_status_update(sender, status_command):
    """Handle status update commands from staff"""
    log_user_activity(sender, "status_update_requested", f"Command: {status_command}")
    
    # Parse command: "ready #FCT0123" or "delivered #FCT0123"
    parts = status_command.split()
    if len(parts) < 2:
        send_text_message(sender, "❌ Invalid command format. Use: [status] [order_id]")
        return
    
    status = parts[0].lower()
    order_id = parts[1].replace("#", "").upper()
    
    # Validate status
    valid_statuses = ["ready", "delivered", "cancelled"]
    if status not in valid_statuses:
        send_text_message(sender, f"❌ Invalid status. Valid statuses: {', '.join(valid_statuses)}")
        return
    
    # Update order status
    from services.order_service import update_order_status_internal
    success = update_order_status_internal(order_id, status)
    
    if success:
        send_text_message(sender, f"✅ Order #{order_id} status updated to '{status}'.")
    else:
        send_text_message(sender, f"❌ Failed to update order #{order_id} status.")

def handle_day_completion(sender):
    """Handle day completion command from Krishna"""
    log_user_activity(sender, "day_completion_requested", "User marked day as completed")
    
    # In a real implementation, you would check if all orders are delivered
    # For now, we'll just send a confirmation
    send_text_message(sender, "✅ Day marked as completed. All orders have been processed.")
    
    # You might also want to trigger end-of-day processes
    from services.order_service import send_daily_delivery_list, send_production_lists
    send_daily_delivery_list()
    send_production_lists()

def handle_catalog_order(sender, items):
    """Handle orders placed directly from WhatsApp catalog"""
    log_user_activity(sender, "catalog_order_received", f"Received {len(items)} items from catalog")
    
    # Get current state
    state = get_user_state(sender)
    
    # Store catalog items for later processing
    state["pending_catalog_items"] = items
    set_user_state(sender, state)
    
    # Start the ordering process
    handle_greeting(sender)

def handle_incoming_message(data):
    """Handle incoming WhatsApp messages with improved cart handling"""
    print("[MESSAGE HANDLER] Received ", data)
    log_user_activity("system", "message_received", "New message received")
    
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
                    log_user_activity(sender, "message_received", text)
                
                # Get current state
                current_state = get_user_state(sender)
                print("[CURRENT STATE]: ", current_state)
                
                # TEXT MESSAGE HANDLING
                if message_type == "text":
                    text = msg.get("text", {}).get("body", "").strip().lower()
                    
                    # Greeting messages
                    if text in ["hi", "hello", "hey", "menu", "start"]:
                        handle_greeting(sender)
                    
                    # Status check
                    elif text in ["status", "check status", "my order"]:
                        handle_status_check(sender)
                    
                    # Day completion (for Krishna)
                    elif text == "day completed" and sender == "919391727848":  # Krishna's number
                        handle_day_completion(sender)
                    
                    # Status update commands (for kitchen staff)
                    elif any(text.startswith(status) for status in ["ready", "delivered", "cancelled"]):
                        handle_status_update(sender, text)
                    
                    # Handle based on current step
                    elif current_state.get("step") == "select_branch":
                        # Extract branch from the message
                        for branch in BRANCHES:
                            if branch in text:
                                handle_branch_selection(sender, branch)
                                break
                        else:
                            # If no branch matched, send branch selection again
                            handle_greeting(sender)
                    
                    elif current_state.get("step") == "browse_menu":
                        # Handle category selection
                        if "custard" in text or "custard products" in text:
                            handle_menu_category(sender, "category_custard_products")
                        elif "delight" in text or "fruit" in text or "mango" in text:
                            handle_menu_category(sender, "category_custard_products")
                        elif "packaging" in text or "jar" in text or "bowl" in text or "cap" in text:
                            handle_menu_category(sender, "category_packaging_supplies")
                        elif "food" in text or "choco" in text or "honey" in text or "oreo" in text:
                            handle_menu_category(sender, "category_food_items")
                        elif "tissue" in text or "sandwich kit" in text:
                            handle_menu_category(sender, "category_other_supplies")
                        else:
                            # If no category matched, send category selection again
                            sections = [{
                                "title": "Menu Categories",
                                "rows": [
                                    {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                                    for cat in PRODUCT_CATALOG.keys()
                                ]
                            }]
                            
                            send_interactive_list_message(
                                sender,
                                "🍽️ Menu Categories",
                                "Please choose a menu category:",
                                "Select a category to view items",
                                "Browse Menu",
                                sections
                            )
                    
                    elif current_state.get("step") == "enter_quantity":
                        handle_quantity_input(sender, text, current_state)
                    
                    elif current_state.get("step") == "cart_options":
                        # Map button text to internal options
                        option_map = {
                            "continue shopping": "continue shopping",
                            "view cart": "view cart",
                            "clear cart": "clear cart",
                            "place order": "place order"
                        }
                        
                        for btn_text, option in option_map.items():
                            if btn_text in text:
                                handle_cart_options(sender, option, current_state)
                                break
                        else:
                            # If no option matched, show cart options again
                            cart = get_user_cart(sender)
                            if not cart:
                                send_text_message(sender, "🛒 Your cart is empty.")
                                # Return to menu
                                sections = [{
                                    "title": "Menu Categories",
                                    "rows": [
                                        {"id": f"category_{cat}", "title": CATEGORY_DISPLAY_NAMES[cat], "description": ""}
                                        for cat in PRODUCT_CATALOG.keys()
                                    ]
                                }]
                                
                                send_interactive_list_message(
                                    sender,
                                    "🍽️ Menu Categories",
                                    "Please choose a menu category:",
                                    "Select a category to view items",
                                    "Browse Menu",
                                    sections
                                )
                                current_state["step"] = "browse_menu"
                                set_user_state(sender, current_state)
                            else:
                                cart_summary = "🛒 *Your Cart*\n\n"
                                for item in cart:
                                    item_total = item["quantity"] * item["price"]
                                    cart_summary += f"- {item['item']} x{item['quantity']}: Rs. {item_total}\n"
                                
                                # Calculate total
                                total = sum(item["quantity"] * item["price"] for item in cart)
                                cart_summary += f"\n*Total:* Rs. {total}"
                                
                                # Send cart with options to modify
                                buttons = ["Continue Shopping", "Clear Cart", "Place Order"]
                                send_interactive_button_message(
                                    sender,
                                    cart_summary,
                                    buttons
                                )
                    
                    elif current_state.get("step") == "enter_order_id":
                        handle_order_id_input(sender, text, current_state)
                    
                    else:
                        # Default response for unrecognized messages
                        send_text_message(sender, "I didn't understand that. Reply with 'menu' to start ordering or 'status' to check your order.")
                
                # INTERACTIVE MESSAGE HANDLING (list selections)
                elif message_type == "interactive":
                    interactive_type = msg.get("interactive", {}).get("type")
                    
                    if interactive_type == "list_reply":
                        selected_id = msg.get("interactive", {}).get("list_reply", {}).get("id", "")
                        
                        if selected_id.startswith("branch_"):
                            branch = selected_id.replace("branch_", "")
                            handle_branch_selection(sender, branch)
                        
                        elif selected_id.startswith("category_"):
                            handle_menu_category(sender, selected_id)
                        
                        elif selected_id.startswith("product_"):
                            handle_product_selection(sender, selected_id)
                    
                    elif interactive_type == "button_reply":
                        selected_id = msg.get("interactive", {}).get("button_reply", {}).get("id", "")
                        
                        if selected_id.startswith("btn_"):
                            # Get the button index
                            btn_idx = int(selected_id.replace("btn_", ""))
                            
                            # Map to cart options
                            cart_options = ["continue shopping", "view cart", "place order"]
                            if btn_idx < len(cart_options):
                                handle_cart_options(sender, cart_options[btn_idx], current_state)
                
                # ORDER MESSAGE HANDLING - This is the critical fix!
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
        import traceback
        print("[ERROR] Message handler error:\n", traceback.format_exc())
        log_user_activity("system", "error", f"Message handler error: {str(e)}")
        return "Error processing message", 500