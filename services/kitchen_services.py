# services/kitchen_services.py

from services.whatsapp_services import send_text_message

KITCHEN_NUMBER = "+91917671011599"

def send_order_to_kitchen(user_id, order_data):
    message = (
        f"🚨 NEW ORDER 🚨\n"
        f"Customer: {user_id}\n"
        f"Items: {', '.join(order_data['items'])}\n"
        f"Branch: {order_data['branch']}"
    )

    send_text_message(KITCHEN_NUMBER, message)
