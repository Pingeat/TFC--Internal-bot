# handlers/message_handler.py

import json
from services.whatsapp_services import send_text_message
from storage import session_manager
from services import kitchen_services
from pathlib import Path

# Loading all products and branches from JSON files

BRANCHES = Path(__file__).parent.parent.parent / "data" / "branches.json"
# with open(branches_path, "r") as f:
#     branches_data = json.load(f)
# BRANCHES = [branch["name"].lower() for branch in branches_data]
#MENU_ITEMS = [product["name"].lower() for product in products_data]

MENU_ITEMS = Path(__file__).parent.parent.parent / "data" / "products.json"
# with open(products_path, "r") as f:
#     products_data = json.load(f)
# MENU_ITEMS = [product["name"].lower() for product in products_data]


def handle_incoming_message(data):
    print("[MESSAGE HANDLER] Received data:", data)
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    continue
                msg = messages[0]
                sender = msg.get("from")
                text = msg.get("text", {}).get("body", "").strip().lower()

                # 'hi' to reset and start new session
                if text in ["hi", "hello", "hey"]:
                    session_manager.start_session(sender)
                    menu = "Welcome! Here's our menu:\n" + "\n".join([item.title() for item in MENU_ITEMS])
                    send_text_message(sender, menu + "\n\nPlease enter your items (comma separated):")
                    return

                session = session_manager.get_session(sender)

                if not session:
                    send_text_message(sender, "Please type 'hi' to start a new order.")
                    return

                # Step 1: Collect Items
                if session["step"] == "collecting_items":
                    items = [item.strip().lower() for item in text.split(",")]
                    valid_items = [item.title() for item in items if item in MENU_ITEMS]

                    if valid_items:
                        session_manager.set_items(sender, valid_items)
                        branches = "Please select your branch:\n" + "\n".join([b.title() for b in BRANCHES])
                        send_text_message(sender, branches)
                    else:
                        send_text_message(sender, "Invalid items. Please choose valid items from the menu.")

                # Step 2: Collect Branch
                elif session["step"] == "collecting_branch":
                    branch = text.lower()

                    if branch in BRANCHES:
                        session_manager.set_branch(sender, branch.title())
                        order_data = session_manager.get_session(sender)

                        # Send order to kitchen staff
                        kitchen_services.send_order_to_kitchen(sender, order_data)

                        # Send confirmation to user
                        summary = f"✅ Order Summary:\nItems: {', '.join(order_data['items'])}\nBranch: {branch.title()}"
                        send_text_message(sender, summary)
                        send_text_message(sender, "Thank you! Your order has been sent to the kitchen staff.")
                        session_manager.reset_session(sender)
                    else:
                        send_text_message(sender, "Invalid branch. Please select a valid branch.")

    except Exception as e:
        print("[ERROR]", e)
