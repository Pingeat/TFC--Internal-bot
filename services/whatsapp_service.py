# # services/whatsapp_service.py

# import json
# import re
# import requests
# from config.credentials import META_ACCESS_TOKEN, WHATSAPP_API_URL, META_PHONE_NUMBER_ID
# from config.settings import STAFF_CONTACTS

# def send_text_message(to, message):
#     print(f"[WHATSAPP] Sending message to {to}")
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "type": "text",
#         "text": {
#             "preview_url": False,
#             "body": message
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print(f"[WHATSAPP] Status: {response.status_code}")
#     return response

# def send_greeting_template(to):
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "type": "template",
#         "template": {
#             "name": "fruitcustard_greeting",
#             "language": {"code": "en_US"}
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print(f"[WHATSAPP] Greeting sent: {response.status_code}")

# def send_delivery_takeaway_template(to):
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "type": "template",
#         "template": {
#             "name": "delivery_takeaway",
#             "language": {"code": "en_US"}
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print(f"[WHATSAPP] Delivery/Takeaway template sent: {response.status_code}")

# def send_payment_option_template(to):
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "type": "template",
#         "template": {
#             "name": "pay_now",
#             "language": {"code": "en_US"}
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print(f"[WHATSAPP] Payment option sent: {response.status_code}")


# def send_pay_online_template(phone_number, payment_link):
#     """
#     Sends payment button via WhatsApp using 'pays_online' template.
#     """
#     token = payment_link.split("/")[-1] if payment_link.startswith("https://rzp.io/rzp/")  else payment_link

#     url = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages" 
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone_number,
#         "type": "template",
#         "template": {
#             "name": "pays_online",
#             "language": {"code": "en_US"},
#             "components": [
#                 {
#                     "type": "button",
#                     "sub_type": "url",
#                     "index": 0,
#                     "parameters": [
#                         {"type": "text", "text": token}
#                     ]
#                 }
#             ]
#         }
#     }

#     response = requests.post(url, headers=headers, json=payload)
#     print(f"[WHATSAPP] Payment link sent. Status: {response.status_code}")

# def send_full_catalog(to):
#     """
#     Sends the full catalog message via WhatsApp.
#     Assumes a pre-configured catalog ID.
#     """
#     payload = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "to": to,
#         "type": "interactive",
#         "interactive": {
#             "type": "catalog_message",
#             "body": {
#                 "text": "🍓 Explore our full Fruit Custard menu!"
#             },
#             "action": {
#                 "name": "catalog_message",
#                 "catalog_id": "1008650128092617"  
#             },
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print(f"[WHATSAPP] Full catalog sent. Status: {response}")
    
# def send_selected_catalog_items(to,selected_items):
#     """
#     Send only selected items from your catalog.
#     """
#     payload = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "to": to,
#         "type": "interactive",
#         "interactive": {
#             "type": "product_list",
#             "header": {
#             "type": "text",
#             "text": "Your Selected Items"
#             },
#             "body": {
#                 "text": "🍓 Here are some similar products!!"
#             },
#             "footer": {
#             "text": "View details below"
#             },
#             "action": {
#                 "catalog_id": "1225552106016549",
#                 "sections": [
#                     {
#                         "title": "Products",
#                         "product_items": [
#                             {"product_retailer_id": id}
#                             for id in selected_items
#                         ]
#                     }
#                 ]
#             }
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print(f"[WHATSAPP] Sent selected items. Status: {response.status_code}, Response: {response.text}")


# def send_kitchen_branch_alert_template(phone_number, order_type, order_id, customer, order_time, item_summary, total, branch, address, location_url): 
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone_number,
#         "type": "template",
#         "template": {
#             "name": "kitchen_branch_alert",
#             "language": { "code": "en_US" },
#             "components": [
#                 {
#                     "type": "body",
#                     "parameters": [
#                         { "type": "text", "text": order_type },
#                         { "type": "text", "text": order_id },
#                         { "type": "text", "text": customer },
#                         { "type": "text", "text": order_time },
#                         { "type": "text", "text": item_summary},
#                         { "type": "text", "text": str(total) },
#                         { "type": "text", "text": branch },
#                         { "type": "text", "text": address },
#                         { "type": "text", "text": location_url }
#                     ]
#                 }
#             ]
#         }
#     }
#     print("[KITCHEN_PARAMETERS] : ",payload)

#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print("📤 Sent kitchen/branch alert:", response.status_code, response.text)

# def send_feedback_template(to):
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "type": "template",
#         "template": {
#             "name": "feedback_2",  # your actual template name
#             "language": { "code": "en_US" }
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print("📤 Sent feedback quick reply template:", response.status_code, response.text)

# def send_marketing_promo1(phone_number, message_text):
#     cleaned_message = clean_message_text(message_text)
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone_number,
#         "type": "template",
#         "template": {
#             "name": "promo_mark",  # Your correct template name
#             "language": { "code": "en_US" },
#             "components": [
#                 {
#                     "type": "body",
#                     "parameters": [
#                         { "type": "text", "text": cleaned_message }
#                     ]
#                 }
#                 # ❌ No need to send header if it's static
#                 # ❌ No need to send footer component if it's static
#             ]
#         }
#     }

#     print("📦 Payload:", json.dumps(payload, indent=2))
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print("📤 Sent promo message:", response.status_code, response.text)

# def send_marketing_promo2(phone_number, message_text):
#     cleaned_message = clean_message_text(message_text)
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone_number,
#         "type": "template",
#         "template": {
#             "name": "promo_marketing_p",
#             "language": { "code": "en_US" },
#             "components": [
#                 {
#                     "type": "body",
#                     "parameters": [
#                         { "type": "text", "text": cleaned_message }
#                     ]
#                 }
#             ]
#         }
#     }
#     print("📦 Payload:", json.dumps(payload, indent=2))
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#     print("📤 Sent promo message:", response.status_code, response.text)
    
# def send_marketing_promo(phone_number, message_text):
#     cleaned_message = clean_message_text(message_text)
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone_number,
#         "type": "template",
#         "template": {
#             "name": "promo_marketing",
#             "language": { "code": "en_US" },
#             "components": [
#                 {
#                     "type": "header",
#                     "parameters": [
#                         {
#                             "type": "image",
#                             "image": {
#                                 "link": "https://thefruitcustard.com/auto.png"
#                             }
#                         }
#                     ]
#                 },
#                 {
#                     "type": "body",
#                     "parameters": [
#                         { "type": "text", "text": cleaned_message }
#                     ]
#                 }
#             ]
#         }
#     }

#     print("📦 Payload:", json.dumps(payload, indent=2))
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     try:
#         response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#         print(f"[SEND] Marketing promo to {phone_number}: {response.status_code} - {response.text}")
#         return response.status_code == 200
#     except Exception as e:
#         print(f"[ERROR] Failed to send promo to {phone_number}: {str(e)}")
#         return False

# def send_catalog_set(phone, retailer_product_id):
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": phone,
#         "type": "template",
#         "template": {
#             "name": "set_cat",  # ✅ Your approved template name
#             "language": { "code": "en_US" },
#             "components": [
#                 {
#                     "type": "button",
#                     "sub_type": "CATALOG",
#                     "index": 0,
#                     "parameters": [
#                         {
#                             "type": "action",
#                             "action": {
#                                 "thumbnail_product_retailer_id": retailer_product_id  # e.g., "tidjkafgwc"
#                             }
#                         }
#                     ]
#                 }
#             ]
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
#     print("📦 Sent catalog set:", response.status_code, response.text)

# def clean_message_text(text, max_len=250):
#     if not text:
#         return ""
#     text = text.replace("\n", " ").replace("\t", " ")
#     text = re.sub(r"\s{2,}", " ", text)
#     text = re.sub(r"[^\x20-\x7E₹]+", "", text)  # allow only safe ASCII + ₹
#     return text.strip()[:max_len]



# def send_order_confirmation(user_id, order_id, branch, items, total, payment_required):
    
#     if payment_required:
#         message += "\n\nPlease complete your payment using the link below."
#     else:
#         message += "\n\nYour order has been placed successfully."
    
#     send_text_message(user_id, message)
    
#     # Send to Krishna (Supervisor)
#     supervisor_msg = f"🆕 *NEW ORDER*\nOrder ID: #{order_id}\nBranch: {branch.title()}\n\n"
#     for item in items:
#         supervisor_msg += f"- {item['item'].title()} x{item['quantity']}\n"
    
#     send_text_message(STAFF_CONTACTS["krishna"], supervisor_msg)

# def send_payment_link(user_id, order_id, amount):
#     """Send payment link for Razorpay"""
#     # In a real implementation, you would generate a real Razorpay link
#     payment_link = f"https://yourdomain.com/payment?order_id={order_id}&amount={amount}"
    
#     message = f"💳 *Payment Required*\n\nPlease complete your payment for Order #{order_id}:\n\nTotal: Rs. {amount}\n\n{payment_link}\n\nThe order will be processed once payment is confirmed."
    
#     send_text_message(user_id, message)

# def send_kitchen_production_list():
#     """Send production list to Sochin and Sagar at 7 AM"""
#     # In a real implementation, you would fetch today's orders
#     # For now, we'll send a sample message
    
#     # Sochin's items (custard related)
#     sochin_items = "Custard Cans - 3\nOatmeal - 2kg\nMango Custard - 1"
#     sochin_msg = f"🍳 *PRODUCTION LIST - SOCHIN*\n\n{sochin_items}\n\nPlease prepare these items for delivery today."
#     send_text_message(STAFF_CONTACTS["sochin"], sochin_msg)
    
#     # Sagar's items (delights)
#     sagar_items = "Apricot Delight - 5\nStrawberry Delight - 6\nBlueberry Delight - 1"
#     sagar_msg = f"🍰 *PRODUCTION LIST - SAGAR*\n\n{sagar_items}\n\nPlease prepare these items for delivery today."
#     send_text_message(STAFF_CONTACTS["sagar"], sagar_msg)

# def send_delivery_list():
#     """Send delivery list to Ashok at 7 AM"""
#     # In a real implementation, you would fetch today's orders
#     # For now, we'll send a sample message
    
#     delivery_msg = "📦 *DELIVERY SCHEDULE*\n\n*Madhapur:*\n- Banana - 3kg\n- Custard Can - 1\n\n*Kondapur:*\n- Custard Can - 2\n- Oatmeal - 2kg\n- Strawberry Delight - 4\n\n*West Maredpally:*\n- Apricot Delight - 5\n- Strawberry Delight - 2\n\n*Manikonda:*\n- Custard Can - 2\n- Oatmeal - 2kg\n- Strawberry Delight - 4\n- Blueberry Delight - 1\n- Apple - 2kg\n- Hand Gloves - 1 pack"
    
#     send_text_message(STAFF_CONTACTS["ashok"], delivery_msg)

# def send_daily_reminder():
#     """Send daily reminder to all branches at 7:05 AM"""
#     reminder_msg = "⏰ *DAILY REMINDER*\n\nHello! Please order any raw materials required today via WhatsApp bot.\n\n*Cut-off time:* 7:00 AM tomorrow\n\nReply with 'menu' to start ordering."
    
#     # In a real implementation, you would send this to all registered branch numbers
#     # For now, we'll send to a sample number
#     send_text_message("919876543210", reminder_msg)  # Replace with actual branch numbers

# def send_status_update(user_id, order_id, status, details=None):
#     """Send order status update to customer"""
#     status_messages = {
#         "ready": "✅ *Order Ready*\n\nYour order #{order_id} is ready for delivery.",
#         "delivered": "📦 *Order Delivered*\n\nYour order #{order_id} has been successfully delivered.",
#         "cancelled": "❌ *Order Cancelled*\n\nYour order #{order_id} has been cancelled."
#     }
    
#     message = status_messages.get(status, f"🔄 *Order Status Update*\n\nYour order #{order_id} status has been updated to: {status.title()}")
    
#     if details:
#         message += f"\n\n*Details:* {details}"
    
#     send_text_message(user_id, message)














# services/whatsapp_service.py
import json
import re
import requests
from config.credentials import META_ACCESS_TOKEN, WHATSAPP_API_URL, META_PHONE_NUMBER_ID
from config.settings import STAFF_CONTACTS
from utils.logger import log_user_activity

# def send_text_message(to, message):
#     """Send a text message via WhatsApp"""
#     print(f"[WHATSAPP] Sending message to {to}")
#     log_user_activity(to, "message_sent", f"Text: {message[:50]}...")
    
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "type": "text",
#         "text": {
#             "preview_url": False,
#             "body": message
#         }
#     }
    
#     headers = {
#         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }
    
#     try:
#         response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
#         print(f"[WHATSAPP] Status: {response.status_code}")
#         if response.status_code != 200:
#             print(f"[WHATSAPP] Error: {response.text}")
#         return response
#     except Exception as e:
#         print(f"[WHATSAPP] Request failed: {e}")
#         return None


def send_text_message(to, message):
    """Send a text message via WhatsApp"""
    print(f"[WHATSAPP] Sending message to {to}")
    log_user_activity(to, "message_sent", f"Text: {message[:50]}...")
    
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
        print(f"[WHATSAPP] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[WHATSAPP] Error: {response.text}")
        return response
    except Exception as e:
        print(f"[WHATSAPP] Request failed: {e}")
        return None

def send_template_message(to, template_name, language="en_US", components=None):
    """Send a WhatsApp template message"""
    print(f"[WHATSAPP] Sending template '{template_name}' to {to}")
    log_user_activity(to, "template_sent", f"Template: {template_name}")
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language}
        }
    }
    
    if components:
        payload["template"]["components"] = components
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        print(f"[WHATSAPP] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[WHATSAPP] Error: {response.text}")
        return response
    except Exception as e:
        print(f"[WHATSAPP] Request failed: {e}")
        return None

def send_interactive_list_message(to, header, body, footer, button_text, sections):
    """Send an interactive list message"""
    print(f"[WHATSAPP] Sending interactive list to {to}")
    log_user_activity(to, "interactive_list_sent", f"Header: {header}")
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": header
            },
            "body": {
                "text": body
            },
            "footer": {
                "text": footer
            },
            "action": {
                "button": button_text,
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
        print(f"[WHATSAPP] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[WHATSAPP] Error: {response.text}")
        return response
    except Exception as e:
        print(f"[WHATSAPP] Request failed: {e}")
        return None

def send_interactive_button_message(to, body, buttons):
    """Send an interactive button message"""
    print(f"[WHATSAPP] Sending interactive buttons to {to}")
    log_user_activity(to, "interactive_buttons_sent", f"Body: {body[:50]}...")
    
    action_buttons = []
    for i, button in enumerate(buttons):
        action_buttons.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{i}",
                "title": button
            }
        })
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": action_buttons
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        print(f"[WHATSAPP] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[WHATSAPP] Error: {response.text}")
        return response
    except Exception as e:
        print(f"[WHATSAPP] Request failed: {e}")
        return None

def send_order_confirmation(user_id, order_id, branch, items, total, payment_required):
    """Send order confirmation message"""
    message = f"✅ *Order Confirmed!*\n\nOrder ID: #{order_id}\nBranch: {branch.title()}\n\n*Items Ordered:*\n"
    
    for item in items:
        message += f"- {item['item'].title()} x{item['quantity']}"
        if item.get('price', 0) > 0:
            message += f" (Rs. {item['price'] * item['quantity']})"
        message += "\n"
    
    message += f"\n*Total:* Rs. {total}"
    
    if payment_required:
        message += "\n\nPlease complete your payment using the link below."
    else:
        message += "\n\nYour order has been placed successfully."
    
    send_text_message(user_id, message)
    
    # Send to Krishna (Supervisor)
    supervisor_msg = f"🆕 *NEW ORDER*\nOrder ID: #{order_id}\nBranch: {branch.title()}\n\n"
    for item in items:
        supervisor_msg += f"- {item['item'].title()} x{item['quantity']}\n"
    
    send_text_message(STAFF_CONTACTS["krishna"], supervisor_msg)

def send_payment_link(user_id, order_id, amount):
    """Send payment link for Razorpay"""
    # In a real implementation, you would generate a real Razorpay link
    payment_link = f"https://yourdomain.com/payment?order_id={order_id}&amount={amount}"
    
    message = f"💳 *Payment Required*\n\nPlease complete your payment for Order #{order_id}:\n\nTotal: Rs. {amount}\n\n{payment_link}\n\nThe order will be processed once payment is confirmed."
    
    send_text_message(user_id, message)

def send_kitchen_production_list():
    """Send production list to Sochin and Sagar at 7 AM"""
    # In a real implementation, you would fetch today's orders
    # For now, we'll send a sample message
    
    # Sochin's items (custard related)
    sochin_items = "Custard Cans - 3\nOatmeal - 2kg\nMango Custard - 1"
    sochin_msg = f"🍳 *PRODUCTION LIST - SOCHIN*\n\n{sochin_items}\n\nPlease prepare these items for delivery today."
    send_text_message(STAFF_CONTACTS["sochin"], sochin_msg)
    
    # Sagar's items (delights)
    sagar_items = "Apricot Delight - 5\nStrawberry Delight - 6\nBlueberry Delight - 1"
    sagar_msg = f"🍰 *PRODUCTION LIST - SAGAR*\n\n{sagar_items}\n\nPlease prepare these items for delivery today."
    send_text_message(STAFF_CONTACTS["sagar"], sagar_msg)

def send_delivery_list():
    """Send delivery list to Ashok at 7 AM"""
    # In a real implementation, you would fetch today's orders
    # For now, we'll send a sample message
    
    delivery_msg = "📦 *DELIVERY SCHEDULE*\n\n*Madhapur:*\n- Banana - 3kg\n- Custard Can - 1\n\n*Kondapur:*\n- Custard Can - 2\n- Oatmeal - 2kg\n- Strawberry Delight - 4\n\n*West Maredpally:*\n- Apricot Delight - 5\n- Strawberry Delight - 2\n\n*Manikonda:*\n- Custard Can - 2\n- Oatmeal - 2kg\n- Strawberry Delight - 4\n- Blueberry Delight - 1\n- Apple - 2kg\n- Hand Gloves - 1 pack"
    
    send_text_message(STAFF_CONTACTS["ashok"], delivery_msg)

def send_daily_reminder():
    """Send daily reminder to all branches at 7:05 AM"""
    reminder_msg = "⏰ *DAILY REMINDER*\n\nHello! Please order any raw materials required today via WhatsApp bot.\n\n*Cut-off time:* 7:00 AM tomorrow\n\nReply with 'menu' to start ordering."
    
    # In a real implementation, you would send this to all registered branch numbers
    # For now, we'll send to a sample number
    send_text_message("919876543210", reminder_msg)  # Replace with actual branch numbers

def send_status_update(user_id, order_id, status, details=None):
    """Send order status update to customer"""
    status_messages = {
        "ready": "✅ *Order Ready*\n\nYour order #{order_id} is ready for delivery.",
        "delivered": "📦 *Order Delivered*\n\nYour order #{order_id} has been successfully delivered.",
        "cancelled": "❌ *Order Cancelled*\n\nYour order #{order_id} has been cancelled."
    }
    
    message = status_messages.get(status, f"🔄 *Order Status Update*\n\nYour order #{order_id} status has been updated to: {status.title()}")
    
    if details:
        message += f"\n\n*Details:* {details}"
    
    send_text_message(user_id, message)