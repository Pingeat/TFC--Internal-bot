# app.py
import os
from flask import Flask
from handlers.webhook_handler import webhook_bp
from handlers.reminder_handler import schedule_daily_tasks
from utils.logger import get_logger
import threading

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.register_blueprint(webhook_bp)

# Initialize logger
logger = get_logger("app")

@app.route("/")
def home():
    return "Central Kitchen WhatsApp Bot is running!"

if __name__ == "__main__":
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_daily_tasks, daemon=True)
    scheduler_thread.start()
    
    # Start Flask app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)