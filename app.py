# # app.py

# from flask import Flask
# from handlers.webhook_handler import webhook_bp
# # from scheduler.background_jobs import start_scheduler

# print("[APP] Initializing WhatsApp bot...")

# app = Flask(__name__)
# app.register_blueprint(webhook_bp)

# if __name__ == "__main__":
#     print("[APP] Starting scheduler and Flask server...")
#     # start_scheduler()
#     app.run(host="0.0.0.0", port=10000)



# app.py
from flask import Flask
from handlers.webhook_handler import webhook_bp
from handlers.reminder_handler import schedule_daily_tasks
from utils.logger import log_user_activity
from utils.csv_utils import initialize_csv_files
import threading

print("[APP] Initializing WhatsApp bot...")

# Initialize CSV files
initialize_csv_files()

app = Flask(__name__)
app.register_blueprint(webhook_bp)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=schedule_daily_tasks, daemon=True)
scheduler_thread.start()
print("[APP] Daily tasks scheduler started")

if __name__ == "__main__":
    print("[APP] Starting Flask server...")
    log_user_activity("system", "app_started", "Flask server started")
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=10000, debug=True)