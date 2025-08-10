# handlers/webhook_handler.py
from flask import Blueprint, request, jsonify
from handlers.message_handler import handle_incoming_message
from services.order_service import confirm_order
from services.whatsapp_service import send_text_message
from config.credentials import META_VERIFY_TOKEN
from utils.logger import get_logger

logger = get_logger("webhook_handler")

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook POST requests"""
    logger.info("Incoming POST request received.")
    data = request.get_json()
    logger.debug(f"Data received: {data}")
    
    # Process the incoming message
    status, code = handle_incoming_message(data)
    return jsonify({"status": status}), code

@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    """Verify webhook with Meta"""
    logger.info("Verifying token...")
    hub_mode = request.args.get("hub.mode")
    hub_token = request.args.get("hub.verify_token")
    hub_challenge = request.args.get("hub.challenge")
    
    if hub_mode == "subscribe" and hub_token == META_VERIFY_TOKEN:
        logger.info("Verification successful.")
        return hub_challenge, 200
    else:
        logger.warning("Verification failed.")
        return "Verification failed", 403

# Payment success webhook
@webhook_bp.route("/payment-success", methods=["GET"])
def payment_success():
    """Handle payment success callback"""
    logger.info("Payment success callback received.")
    whatsapp_number = request.args.get("whatsapp")
    order_id = request.args.get("order_id")
    
    if whatsapp_number and order_id:
        # Confirm the order
        confirm_order(whatsapp_number, "Online", order_id, paid=True)
        return "Payment confirmed", 200
    else:
        logger.error("Missing parameters in payment success callback")
        return "Missing parameters", 400

# Razorpay webhook (for production)
@webhook_bp.route("/razorpay-webhook-tfcmarket", methods=["POST"])
def razorpay_webhook():
    """Handle Razorpay payment webhook"""
    logger.info("Razorpay webhook received.")
    data = request.get_json()
    
    if data.get("event") == "payment_link.paid":
        payment_data = data.get("payload", {}).get("payment_link", {}).get("entity", {})
        whatsapp_number = payment_data.get("customer", {}).get("contact")
        order_id = payment_data.get("reference_id")
        
        if whatsapp_number and order_id:
            # send_text_message(whatsapp_number, "✅ Your payment is confirmed! Your order is being processed.")
            # Confirm the order
            confirm_order(whatsapp_number, "Online", order_id, paid=True)
    
    return "OK", 200


@webhook_bp.route("/download-orders")
def download_orders():
    from flask import send_file
    return send_file("orders.csv", as_attachment=True)

@webhook_bp.route("/download-user-log")
def download_user_log():
    from flask import send_file
    return send_file("user_activity_log.csv", as_attachment=True)

# @webhook_bp.route("/download-orders")
# def download_orders():
#     from flask import send_file
#     return send_file("orders.csv", as_attachment=True)

@webhook_bp.route("/download-offhour")
def download_offhour_users():
    from flask import send_file
    return send_file("offhour_users.csv", as_attachment=True)