# services/whatsapp_service.py
import requests
import json
from config.credentials import META_ACCESS_TOKEN, WHATSAPP_API_URL, WHATSAPP_CATALOG_ID
from config.settings import PRODUCT_CATEGORIES, BRANCHES, PAYMENT_BRANCHES, STAFF_CONTACTS, PRODUCT_PRICES
from utils.logger import get_logger
from stateHandlers.redis_state import redis_state

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

def send_order_confirmation(to, order_id, branch):
    """Send order confirmation message"""
    logger.info(f"Sending order confirmation to {to} for order {order_id}")
    
    message = f"✅ *ORDER CONFIRMED*\n\n"
    message += f"Order ID: #{order_id}\n"
    message += f"Branch: {branch.title()}\n\n"
    message += "Your order has been placed successfully!\n"
    message += "You will receive a notification when your order is ready for delivery."
    
    return send_text_message(to, message)

def send_payment_link(to, order_id, amount):
    """Send payment link for branches that require payment"""
    logger.info(f"Sending payment link to {to} for order {order_id}")
    
    # In a real implementation, this would generate a Razorpay payment link
    payment_link = f"https://api.razorpay.com/v1/payment_links/create?order_id={order_id}&amount={amount}"
    
    message = "💳 *PAYMENT REQUIRED*\n\n"
    message += f"Please complete payment for your order #{order_id}:\n\n"
    message += f"Amount: ₹{amount}\n\n"
    message += f"Payment Link: {payment_link}\n\n"
    message += "You will receive order confirmation after payment is successful."
    
    return send_text_message(to, message)

def notify_supervisor(order_id, branch, items):
    """Notify supervisor (Krishna) about new order with Redis validation"""
    logger.info(f"Notifying supervisor about order {order_id} from {branch}")
    
    # Double-check branch consistency
    if not branch or branch.lower() not in [b.lower() for b in BRANCHES]:
        logger.error(f"Invalid branch in order notification: {branch}")
        return
    
    message = f"📋 *NEW ORDER*\n\n"
    message += f"Order ID: #{order_id}\n"
    message += f"Branch: {branch.title()}\n\n"
    message += "Items:\n"
    
    for item in items:
        message += f"• {item['name'].title()} x{item['quantity']}\n"
    
    return send_text_message(STAFF_CONTACTS["krishna"], message)

def send_production_list():
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
        send_text_message(STAFF_CONTACTS["sochin"], message)
    
    # Send to Sagar (delights items)
    if production_list["delights"]:
        message = "🍰 *PRODUCTION LIST - SAGAR*\n\n"
        for item in production_list["delights"]:
            message += f"• {item['name'].title()} x{item['quantity']} ({item['branch'].title()})\n"
        send_text_message(STAFF_CONTACTS["sagar"], message)

def send_delivery_list():
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
        
        send_text_message(STAFF_CONTACTS["ashok"], message)
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