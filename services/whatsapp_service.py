# services/whatsapp_service.py
import re
import requests
import json
from config.credentials import META_ACCESS_TOKEN, WHATSAPP_API_URL, WHATSAPP_CATALOG_ID
from config.settings import CATEGORY_DISPLAY_NAMES, ORDER_STATUS, PRODUCT_CATALOG, PRODUCT_CATEGORIES, BRANCHES, PAYMENT_BRANCHES, STAFF_ASSIGNMENTS, STAFF_CONTACTS, PRODUCT_PRICES, STAFF_ROLES
from utils.logger import get_logger
from stateHandlers.redis_state import redis_state
from utils.payments_utils import generate_payment_link

logger = get_logger("whatsapp_service")

def send_text_message(to, message):
    """Send a text message via WhatsApp"""
    logger.info(f"Sending message to {to}")
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        logger.info(f"WhatsApp API response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"WhatsApp API error: {response.text}")
        
        return response
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {str(e)}")
        return None

def send_branch_selection_message(to):
    """Send branch selection message using interactive list template"""
    logger.info(f"Sending branch selection to {to}")
    
    # Create sections for the list
    sections = [{
        "title": "Select Branch",
        "rows": [
            {"id": branch, "title": branch.title(), "description": ""} 
            for branch in BRANCHES
        ]
    }]
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "🏢 SELECT YOUR BRANCH"
            },
            "body": {
                "text": "Please select your branch from the list below:"
            },
            "footer": {
                "text": "Tap to select your branch"
            },
            "action": {
                "button": "Select Branch",
                "sections": sections
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        logger.info(f"Branch selection template sent. Status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Branch selection error: {response.text}")
        return response
    except Exception as e:
        logger.error(f"Failed to send branch selection: {str(e)}")
        return None

def send_full_catalog(to, branch=None):
    """Send full catalog message via WhatsApp"""
    logger.info(f"Sending catalog to {to}")
    
    # If branch is provided, check if payment is required
    payment_required = False
    if branch and branch.lower() in [b.lower() for b in PAYMENT_BRANCHES]:
        payment_required = True
    
    # Build catalog message
    catalog_message = "🌟 *CENTRAL KITCHEN ORDERING SYSTEM*\n\n"
    if payment_required:
        catalog_message += "⚠️ *Note*: Payment is required for your branch.\n\n"
    catalog_message += "Please select a product from our catalog to add to cart."
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "catalog_message",
            "body": {
                "text": catalog_message
            },
            "action": {
                "name": "catalog_message",
                "catalog_id": WHATSAPP_CATALOG_ID
            }
        }
    }
    
    # Only include catalog_id if we have one configured
    # if WHATSAPP_CATALOG_ID:
    #     payload["interactive"]["action"]["catalog_id"] = WHATSAPP_CATALOG_ID
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        logger.info(f"Catalog template sent. Status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Catalog error: {response.text}")
        return response
    except Exception as e:
        logger.error(f"Failed to send catalog: {str(e)}")
        return None

def send_cart_summary(to):
    """Send cart summary to user with interactive buttons"""
    logger.info(f"Sending cart summary to {to}")
    cart = redis_state.get_cart(to)
    if not cart["items"]:
        message = "🛒 *YOUR CART IS EMPTY*\n\n"
        message += "Use the catalog to add items to your cart."
        return send_text_message(to, message)
    
    message = "🛒 *YOUR CART*\n\n"
    total = 0
    
    for item in cart["items"]:
        item_total = item["quantity"] * item["price"]
        total += item_total
        message += f"• {item['name'].title()} x{item['quantity']} = ₹{item_total}\n"
    
    message += f"\n*TOTAL*: ₹{total}\n\n"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": message
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "continue_shopping",
                            "title": "Continue Shopping"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "checkout",
                            "title": "Checkout"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "clear_cart",
                            "title": "Clear Cart"
                        }
                    }
                ]
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        logger.info(f"Cart summary template sent. Status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Cart summary error: {response.text}")
        return response
    except Exception as e:
        logger.error(f"Failed to send cart summary: {str(e)}")
        return None

def send_order_confirmation(to, order_id, branch, items, total):
    """Send order confirmation message with detailed order items"""
    logger.info(f"Sending order confirmation to {to} for order {order_id}")
    
    message = f"✅ *ORDER CONFIRMED*\n\n"
    message += f"Order ID: #{order_id}\n"
    message += f"Branch: {branch.title()}\n\n"
    
    # Add order items section
    message += "ORDER ITEMS:\n"
    for item in items:
        item_total = item["quantity"] * item["price"]
        message += f"• {item['name'].title()} x{item['quantity']} = ₹{item_total}\n"
    
    message += f"\n*TOTAL*: ₹{total}\n\n"
    message += "Your order has been placed successfully!\n"
    message += "You will receive a notification when your order is ready for delivery."
    
    return send_text_message(to, message)

def send_payment_link(to, order_id, amount):
    """Send payment link for branches that require payment"""
    logger.info(f"Sending payment link to {to} for order {order_id}")
    
    # In a real implementation, this would generate a Razorpay payment link
    payment_link = generate_payment_link(to,1,order_id)
    
    message = "💳 *PAYMENT REQUIRED*\n\n"
    message += f"Please complete payment for your order #{order_id}:\n\n"
    message += f"Amount: ₹{amount}\n\n"
    message += f"Payment Link: {payment_link}\n\n"
    message += "You will receive order confirmation after payment is successful."
    
    return send_text_message(to, message)

# def notify_supervisor(order_id, branch, items):
#     """Notify supervisor (Krishna) about new order with dynamic staff assignment"""
#     logger.info(f"Notifying supervisor about order {order_id} from {branch}")
    
#     # Double-check branch consistency
#     if not branch or branch.lower() not in [b.lower() for b in BRANCHES]:
#         logger.error(f"Invalid branch in order notification: {branch}")
#         return
    
#     message = f"📋 *NEW ORDER*\n\n"
#     message += f"Order ID: #{order_id}\n"
#     message += f"Branch: {branch.title()}\n\n"
#     message += "Items:\n"
    
#     for item in items:
#         message += f"• {item['name'].title()} x{item['quantity']}\n"
    
#     # Send to all supervisors
#     for staff in STAFF_ASSIGNMENTS:
#         if "supervisor" in STAFF_ASSIGNMENTS[staff] and staff in STAFF_CONTACTS:
#             logger.info(f"Sending order notification to Supervisor: {STAFF_CONTACTS[staff]}")
#             send_text_message(STAFF_CONTACTS[staff], message)
#     # send_production_lists()
#     # send_daily_delivery_list()


def notify_supervisor(order_id, branch, items):
    """Notify ALL supervisors about new order with dynamic staff assignment"""
    logger.info(f"Notifying supervisors about order {order_id} from {branch}")
    
    # Validate branch
    if not branch or branch.lower() not in [b.lower() for b in BRANCHES]:
        logger.error(f"Invalid branch in order notification: {branch}")
        return
    
    # Format order message
    message = (
        f"📋 *NEW ORDER*\n\n"
        f"Order ID: #{order_id}\n"
        f"Branch: {branch.title()}\n\n"
        "Items:\n"
    )
    for item in items:
        message += f"• {item['name'].title()} x{item['quantity']}\n"
    
    # Send notification to ALL supervisors
    for phone_number in STAFF_ROLES.get("supervisor", []):
        # print(STAFF_ROLES.get("supervisor", []))
        logger.info(f"Sending order notification to Supervisor: {phone_number}")
        send_text_message(phone_number, message)
    
def send_branch_delivery_instructions(to):
    """Send delivery instructions to delivery staff"""
    logger.info(f"Sending delivery instructions to {to}")
    
    message = "🚚 *DELIVERY COMMANDS*\n\n"
    message += "To update delivery status, use these commands:\n\n"
    message += "• *Ready [Branch]* - Mark all orders for a branch as READY\n"
    message += "• *Delivered [Branch]* - Mark all READY orders for a branch as DELIVERED\n"
    message += "• *Completed [Branch]* - Mark all DELIVERED orders for a branch as COMPLETED\n\n"
    message += "Example: \"Delivered Kondapur\"\n\n"
    message += "Type \"/list\" to see current delivery status for all branches."
    
    return send_text_message(to, message)

def send_delivery_status(to):
    """Send current delivery status for all branches"""
    logger.info(f"Sending delivery status to {to}")
    
    # Get all orders
    orders = redis_state.get_todays_orders()
    
    # Group by branch and status
    branch_status = {}
    for order in orders:
        branch = order["branch"].lower()
        if branch not in branch_status:
            branch_status[branch] = {
                "ready": 0,
                "delivered": 0,
                "total": 0
            }
        
        branch_status[branch]["total"] += 1
        if order["status"] == ORDER_STATUS["READY"]:
            branch_status[branch]["ready"] += 1
        elif order["status"] == ORDER_STATUS["DELIVERED"]:
            branch_status[branch]["delivered"] += 1
    
    # Create status message
    message = "📊 *CURRENT DELIVERY STATUS*\n\n"
    for branch, status in branch_status.items():
        branch_name = next((b for b in BRANCHES if b.lower() == branch), branch)
        message += f"*{branch_name.title()}*\n"
        message += f"• Total Orders: {status['total']}\n"
        message += f"• Ready for Delivery: {status['ready']}\n"
        message += f"• Delivered: {status['delivered']}\n\n"
    
    message += "Use delivery commands to update status."
    
    return send_text_message(to, message)

def send_delivery_confirmation(to, branch, status, count):
    """Send delivery confirmation message"""
    logger.info(f"Sending delivery confirmation for {branch} to {to}")
    
    status_text = status.lower().replace("_", " ").title()
    
    message = f"✅ *{status_text.upper()}*\n\n"
    message += f"Branch: {branch.title()}\n"
    message += f"Orders updated: {count}\n\n"
    message += f"All orders for this branch have been marked as {status_text}.\n\n"
    message += "Type \"/status\" for current delivery status."
    
    return send_text_message(to, message)

# def send_production_lists():
#     """Send production lists to appropriate staff based on dynamic category assignments"""
#     logger.info("Sending production lists to staff from Redis")
    
#     # Get orders directly from Redis (primary source)
#     orders = redis_state.get_todays_orders()
    
#     # Group orders by category with aggregation
#     categorized_orders = {}
    
#     # Initialize all categories
#     for category in PRODUCT_CATEGORIES.keys():
#         categorized_orders[category] = {}
    
#     # First pass: aggregate quantities by product and branch
#     for order in orders:
#         # Parse items from order
#         try:
#             for item in order["items"]:
#                 product_name = item['name'].lower()
                
#                 # Try to get category from catalog first (most reliable)
#                 catalog_product = None
#                 for pid, pinfo in PRODUCT_CATALOG.items():
#                     if pinfo["name"].lower() == product_name:
#                         catalog_product = pinfo
#                         break
                
#                 # Determine category
#                 category = None
#                 if catalog_product and "category" in catalog_product:
#                     category = catalog_product["category"]
#                 else:
#                     # Fallback to keyword matching
#                     for cat, keywords in PRODUCT_CATEGORIES.items():
#                         if any(keyword in product_name for keyword in keywords):
#                             category = cat
#                             break
                
#                 # If still no category, assign to "others"
#                 if not category:
#                     category = "others"
#                     logger.warning(f"Product '{item['name']}' could not be categorized, assigned to 'others'")
                
#                 # Initialize product entry if not exists
#                 if product_name not in categorized_orders[category]:
#                     categorized_orders[category][product_name] = {
#                         "name": item['name'],
#                         "total_quantity": 0,
#                         "by_branch": {}
#                     }
                
#                 # Update total quantity
#                 categorized_orders[category][product_name]["total_quantity"] += item['quantity']
                
#                 # Update branch-specific quantity
#                 branch = order['branch'].lower()
#                 if branch not in categorized_orders[category][product_name]["by_branch"]:
#                     categorized_orders[category][product_name]["by_branch"][branch] = 0
#                 categorized_orders[category][product_name]["by_branch"][branch] += item['quantity']
                
#         except Exception as e:
#             logger.error(f"Error parsing order items for order {order.get('order_id')}: {str(e)}")
    
#     # Send to appropriate staff based on category assignments
#     staff_lists = {}
    
#     # Group categories by staff member
#     for staff, assigned_categories in STAFF_ASSIGNMENTS.items():
#         # Skip delivery staff (ashok) for production lists
#         if staff == "ashok":
#             continue
            
#         staff_lists[staff] = []
        
#         # Add all categories assigned to this staff
#         for category in assigned_categories:
#             if category in categorized_orders and categorized_orders[category]:
#                 staff_lists[staff].append({
#                     "category": category,
#                     "items": categorized_orders[category]
#                 })
    
#     # Special handling for supervisor - send ALL categories
#     if "krishna" in STAFF_ASSIGNMENTS:
#         staff_lists["krishna"] = []
#         for category in categorized_orders:
#             if categorized_orders[category]:
#                 staff_lists["krishna"].append({
#                     "category": category,
#                     "items": categorized_orders[category]
#                 })
    
#     # Send messages to each staff member
#     for staff, category_lists in staff_lists.items():
#         if not category_lists:
#             continue
            
#         # Build message
#         message = f"📋 *PRODUCTION LIST - {staff.title()}*\n\n"
        
#         for category_list in category_lists:
#             category = category_list["category"]
#             items = category_list["items"]
            
#             # Get display name for category
#             display_name = CATEGORY_DISPLAY_NAMES.get(category, category.title())
#             message += f"*{display_name}*\n"
            
#             for product_data in items.values():
#                 # Format branch details
#                 branch_details = ", ".join([f"{qty} from {branch.title()}" 
#                                           for branch, qty in product_data["by_branch"].items()])
#                 message += f"• {product_data['name'].title()} x{product_data['total_quantity']} ({branch_details})\n"
            
#             message += "\n"
        
#         # Send to staff
#         if staff in STAFF_CONTACTS:
#             send_text_message(STAFF_CONTACTS[staff], message)
#         else:
#             logger.error(f"Staff {staff} not found in contacts")

def send_daily_delivery_list():
    """Send delivery list to Ashok at 7:00 AM using Redis data with proper aggregation"""
    logger.info("Sending delivery list to Ashok from Redis")
    
    # Get orders directly from Redis (primary source)
    orders = redis_state.get_todays_orders()
    
    # Group orders by branch with product aggregation
    delivery_list = {}
    
    for order in orders:
        branch = order['branch'].lower()
        if branch not in delivery_list:
            delivery_list[branch] = {}
        
        # Parse items
        try:
            for item in order["items"]:
                product_name = item['name'].lower()
                
                # Initialize product entry if not exists
                if product_name not in delivery_list[branch]:
                    delivery_list[branch][product_name] = {
                        "name": item['name'],
                        "quantity": 0
                    }
                
                # Aggregate quantity
                delivery_list[branch][product_name]["quantity"] += item['quantity']
                
        except Exception as e:
            logger.error(f"Error parsing order items for order {order.get('order_id')}: {str(e)}")
    
    # Format message
    if delivery_list:
        message = "🚚 *DAILY DELIVERY LIST*\n\n"
        for branch, products in delivery_list.items():
            message += f"*{branch.title()}*\n"
            for product_data in products.values():
                message += f"• {product_data['name'].title()} x{product_data['quantity']}\n"
            message += "\n"
        
        # Send to all delivery staff (could be multiple)
        for staff in STAFF_ASSIGNMENTS:
            if "delivery" in STAFF_ASSIGNMENTS[staff] and staff in STAFF_CONTACTS:
                send_text_message(STAFF_CONTACTS[staff], message)
                logger.info(f"Delivery list Sent to Ashok {STAFF_CONTACTS[staff]}")
    else:
        logger.info("No orders for delivery today")

def send_daily_reminder():
    """Send daily reminder at 7:05 AM"""
    logger.info("Sending daily reminder to branches")
    
    message = ("⏰ *DAILY ORDER REMINDER*\n\n"
               "Hello! Reminder to order any raw materials required today via WhatsApp bot. "
               "Cut-off: 7:00 AM tomorrow")
    
    # In a real implementation, this would send to all branches
    # For now, we'll just log it
    logger.info(f"Daily reminder message: {message}")
    
    # In a real system, you would send this to all branch managers
    # For demonstration, we're just logging it





def send_production_lists():
    """Send production lists to appropriate staff based on dynamic category assignments"""
    logger.info("Sending production lists to staff from Redis")
    # Get orders directly from Redis (primary source)
    orders = redis_state.get_todays_orders()
    
    # Group orders by category with aggregation
    categorized_orders = {}
    
    # Initialize all categories
    for category in PRODUCT_CATEGORIES.keys():
        categorized_orders[category] = {}
    
    # Sort categories by length (longest first) for more specific matching
    sorted_categories = sorted(
        PRODUCT_CATEGORIES.items(), 
        key=lambda x: len(x[0]), 
        reverse=True
    )
    
    # First pass: aggregate quantities by product and branch
    for order in orders:
        # Parse items from order
        try:
            for item in order["items"]:
                # Extract product name and quantity
                item_name = item["name"].lower()
                quantity = item["quantity"]
                
                # Find matching category - try most specific categories first
                matched_category = None
                for category, keywords in sorted_categories:
                    for keyword in keywords:
                        # Check if keyword is a whole word match
                        if re.search(rf'\b{re.escape(keyword)}\b', item_name):
                            matched_category = category
                            break
                    if matched_category:
                        break
                
                # If no category matched, use "others"
                if not matched_category:
                    matched_category = "others"
                
                # Get product name without quantity details
                product_name = item_name
                
                # Add to category aggregation
                if product_name not in categorized_orders[matched_category]:
                    categorized_orders[matched_category][product_name] = {}
                
                # Add quantity for this branch
                branch = order["branch"].lower()
                if branch not in categorized_orders[matched_category][product_name]:
                    categorized_orders[matched_category][product_name][branch] = 0
                
                categorized_orders[matched_category][product_name][branch] += quantity
        
        except Exception as e:
            logger.error(f"Error parsing order items for order {order['order_id']}: {str(e)}")
            continue
    
    # Second pass: send lists to appropriate staff
    for category, products in categorized_orders.items():
        if not products:  # Skip empty categories
            continue
        
        # Find staff responsible for this category
        staff_list = []
        for staff, categories in STAFF_ASSIGNMENTS.items():
            if category in categories and staff in STAFF_CONTACTS:
                staff_list.append(staff)
        
        if not staff_list:
            logger.info(f"No staff assigned for category: {category}")
            continue
        
        # Format message for this category
        message = f"📋 *{CATEGORY_DISPLAY_NAMES.get(category, category).upper()} PRODUCTION LIST*\n\n"
        
        for product, branches in products.items():
            message += f"*{product.title()}*\n"
            for branch, quantity in branches.items():
                # Fix: Use BRANCHES dictionary properly
                branch_name = BRANCHES.get(branch, branch).title()
                message += f"• {branch_name}: {quantity}\n"
            message += "\n"
        
        # Send to all staff responsible for this category
        for staff in staff_list:
            send_text_message(STAFF_CONTACTS[staff], message)
    
    # Send delivery list to delivery staff
    delivery_message = "🚚 *DELIVERY LIST*\n\n"
    for order in orders:
        if order["status"] == ORDER_STATUS["READY"]:
            # Fix: Use BRANCHES dictionary properly
            branch_name = BRANCHES.get(order["branch"].lower(), order["branch"]).title()
            delivery_message += f"• #{order['order_id']} - {branch_name}\n"
    
    if "•" in delivery_message:  # Check if there are any delivery items
        for staff in STAFF_ASSIGNMENTS:
            if "delivery" in STAFF_ASSIGNMENTS[staff] and staff in STAFF_CONTACTS:
                send_text_message(STAFF_CONTACTS[staff], delivery_message)
    else:
        logger.info("No orders for delivery today")