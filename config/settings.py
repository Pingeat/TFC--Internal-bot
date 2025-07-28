# config/settings.py

# ORDERS_CSV = "orders.csv"
# FEEDBACK_CSV = "feedback.csv"
# USER_LOG_CSV = "user_activity_log.csv"
# OFF_HOUR_USERS_CSV = "offhour_users.csv"
# PROMO_LOG_CSV = "promo_sent_log.csv"

# KITCHEN_NUMBERS = ["918074301029"]


# config/settings.py
# Branch configuration
BRANCHES = [
    "madhapur", "kondapur", "west maredpally", "manikonda", 
    "nanakramguda", "nizampet", "miyapur", "pragathinagar"
]

# Branches requiring payment
PAYMENT_BRANCHES = ["madhapur", "west maredpally", "miyapur", "pragathinagar"]

# Staff contacts
STAFF_CONTACTS = {
    "sochin": "+919064060132",
    "sagar": "+918927830590",
    "krishna": "+919391727848",  # Supervisor
    "ashok": "+919346647165"     # Delivery
}

# Product categories
PRODUCT_CATEGORIES = {
    "custard": ["custard can", "mango custard", "oatmeal", "less sugar custards"],
    "delights": ["apricot delight", "strawberry delight", "blueberry delight"],
    "fruits": ["banana", "apple"],
    "others": ["hand gloves"]
}

# CSV file paths
ORDERS_CSV = "orders.csv"
FEEDBACK_CSV = "feedback.csv"
USER_LOG_CSV = "user_activity_log.csv"
OFF_HOUR_USERS_CSV = "offhour_users.csv"
PROMO_LOG_CSV = "promo_sent_log.csv"

# Operational hours
CUT_OFF_HOUR = 7  # 7 AM cut-off

