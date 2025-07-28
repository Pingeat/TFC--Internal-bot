# # handlers/webhook_handler.py

# from flask import Blueprint, request, jsonify
# from handlers.message_handler import handle_incoming_message
# # from services.order_service import update_order_status
# from services.whatsapp_service import send_text_message
# from config.credentials import META_VERIFY_TOKEN

# webhook_bp = Blueprint('webhook', __name__)

# @webhook_bp.route("/webhook", methods=["POST"])
# def webhook():
#     print("[WEBHOOK] Incoming POST request received.")
#     data = request.get_json()
#     handle_incoming_message(data)
#     return jsonify({"status": "OK"}), 200

# @webhook_bp.route("/webhook", methods=["GET"])
# def verify_webhook():
#     print("[WEBHOOK] Verifying token...")
#     hub_mode = request.args.get("hub.mode")
#     hub_token = request.args.get("hub.verify_token")
#     hub_challenge = request.args.get("hub.challenge")

#     if hub_mode == "subscribe" and hub_token == META_VERIFY_TOKEN :
#         print("[WEBHOOK] Verification successful.")
#         return hub_challenge, 200
#     else:
#         print("[WEBHOOK] Verification failed.")
#         return "Verification failed", 403

# # ✅ Add these for payment handling
# @webhook_bp.route("/payment-success", methods=["GET"])
# def payment_success():
#     from services.order_service import confirm_order
#     whatsapp_number = request.args.get("whatsapp")
#     order_id = request.args.get("order_id")
#     if whatsapp_number and order_id:
#         confirm_order(whatsapp_number, "Online", order_id, paid=True)
#     return "Payment confirmed", 200

# @webhook_bp.route("/razorpay-webhook", methods=["POST"])
# def razorpay_webhook():
#     data = request.get_json()
#     if data.get("event") == "payment_link.paid":
#         payment_data = data.get("payload", {}).get("payment_link", {}).get("entity", {})
#         whatsapp_number = payment_data.get("customer", {}).get("contact")
#         order_id = payment_data.get("reference_id")
#         if whatsapp_number and order_id:
#             send_text_message(whatsapp_number, "✅ Your payment is confirmed! Your order is being processed.")
#     return "OK", 200




# handlers/webhook_handler.py
from flask import Blueprint, request, jsonify
from handlers.message_handler import handle_incoming_message
from services.order_service import confirm_order
from services.whatsapp_service import send_text_message
from config.credentials import META_VERIFY_TOKEN
from utils.logger import log_user_activity

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook POST requests"""
    print("[WEBHOOK] Incoming POST request received.")
    log_user_activity("system", "webhook_received", "POST request")
    
    data = request.get_json()
    print("[WEBHOOK] Data received:", data)
    
    # Process the incoming message
    status, code = handle_incoming_message(data)
    
    return jsonify({"status": status}), code

@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    """Verify webhook with Meta"""
    print("[WEBHOOK] Verifying token...")
    log_user_activity("system", "webhook_verification", "GET request")
    
    hub_mode = request.args.get("hub.mode")
    hub_token = request.args.get("hub.verify_token")
    hub_challenge = request.args.get("hub.challenge")
    
    if hub_mode == "subscribe" and hub_token == META_VERIFY_TOKEN:
        print("[WEBHOOK] Verification successful.")
        log_user_activity("system", "webhook_verified", "Token matched")
        return hub_challenge, 200
    else:
        print("[WEBHOOK] Verification failed.")
        log_user_activity("system", "webhook_verification_failed", "Invalid token")
        return "Verification failed", 403

# Payment success webhook
@webhook_bp.route("/payment-success", methods=["GET"])
def payment_success():
    """Handle payment success callback"""
    print("[WEBHOOK] Payment success callback received.")
    log_user_activity("system", "payment_success", "Payment success callback")
    
    whatsapp_number = request.args.get("whatsapp")
    order_id = request.args.get("order_id")
    
    if whatsapp_number and order_id:
        # Confirm the order
        confirm_order(whatsapp_number, "Online", order_id, paid=True)
        return "Payment confirmed", 200
    else:
        log_user_activity("system", "payment_error", "Missing parameters in payment success")
        return "Missing parameters", 400

# Razorpay webhook (for production)
@webhook_bp.route("/razorpay-webhook", methods=["POST"])
def razorpay_webhook():
    """Handle Razorpay payment webhook"""
    print("[WEBHOOK] Razorpay webhook received.")
    log_user_activity("system", "razorpay_webhook", "Razorpay payment notification")
    
    data = request.get_json()
    
    if data.get("event") == "payment_link.paid":
        payment_data = data.get("payload", {}).get("payment_link", {}).get("entity", {})
        whatsapp_number = payment_data.get("customer", {}).get("contact")
        order_id = payment_data.get("reference_id")
        
        if whatsapp_number and order_id:
            send_text_message(whatsapp_number, "✅ Your payment is confirmed! Your order is being processed.")
            # Confirm the order
            confirm_order(whatsapp_number, "Online", order_id, paid=True)
    
    return "OK", 200