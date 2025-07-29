# handlers/message_handler.py
import json
import traceback
from config.settings import BRANCHES, PAYMENT_BRANCHES, PRODUCT_CATALOG, PRODUCT_CATEGORIES, PRODUCT_PRICES
from stateHandlers.redis_state import redis_state
from services.whatsapp_service import (
    send_branch_selection_message,
    send_full_catalog,
    send_cart_summary,
    send_text_message
)
from services.order_service import place_order
from utils.logger import get_logger
from datetime import datetime

logger = get_logger("message_handler")

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

def handle_text_message(sender, text, current_state):
    """Handle text messages from users (fallback for non-interactive clients)"""
    logger.info(f"Handling text message from {sender}: {text}")
    
    # Check if it's a branch selection
    if current_state and current_state.get("step") == "SELECT_BRANCH":
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
            send_text_message(sender, "❌ Please enter a valid branch number (1-8).")
        return
    
    # Check if it's a catalog interaction
    if current_state and current_state.get("step") == "IN_CATALOG":
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
                send_text_message(sender, "❌ Branch not selected. Please start over.")
            return
        
        # Check for clear cart command
        if text in ["clear cart", "3"]:
            redis_state.clear_cart(sender)
            send_text_message(sender, "🗑️ Your cart has been cleared.")
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
            # Check if it's a continue shopping command
            if text in ["continue shopping", "1"]:
                send_full_catalog(sender, redis_state.get_cart(sender)["branch"])
                return
            
            send_text_message(sender, "❌ Product not found. Please select from the catalog, type 'cart' to view your cart, or type 'checkout' to place your order.")
        
        return
    
    # Default: Start the ordering process
    send_branch_selection_message(sender)
    redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})

def handle_branch_selection(sender, selected_branch, current_state):
    """Handle branch selection from interactive list"""
    logger.info(f"Handling branch selection for {sender}: {selected_branch}")
    
    if current_state and current_state.get("step") == "SELECT_BRANCH":
        # Check if the selected branch is valid
        valid_branches = [b.lower() for b in BRANCHES]
        if selected_branch.lower() in valid_branches:
            # Find the exact branch name from our list (to maintain consistent casing)
            selected_branch = next(b for b in BRANCHES if b.lower() == selected_branch.lower())
            
            redis_state.set_branch(sender, selected_branch)
            redis_state.set_user_state(sender, {"step": "IN_CATALOG"})
            send_full_catalog(sender, selected_branch)
        else:
            send_text_message(sender, "❌ Invalid branch selection. Please try again.")
    else:
        # If we're not expecting a branch selection, send the branch selection menu again
        send_branch_selection_message(sender)
        redis_state.set_user_state(sender, {"step": "SELECT_BRANCH"})

def handle_button_response(sender, button_id, current_state):
    """Handle button responses from user"""
    logger.info(f"Handling button response for {sender}: {button_id}")
    
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