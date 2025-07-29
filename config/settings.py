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
    "ashok": "+919346647165" ,
    "David": "+918074301029"# Delivery
}

# Product categories
PRODUCT_CATEGORIES = {
    "custard": ["custard can", "mango custard", "oatmeal", "less sugar custards"],
    "delights": ["apricot delight", "strawberry delight", "blueberry delight"],
    "fruits": ["banana", "apple"],
    "others": ["hand gloves"]
}

# Product prices
PRODUCT_PRICES = {
    "custard can": 150,
    "mango custard": 200,
    "oatmeal": 180,
    "less sugar custards": 160,
    "apricot delight": 220,
    "strawberry delight": 220,
    "blueberry delight": 220,
    "banana": 50,
    "apple": 60,
    "hand gloves": 30
}

# CSV file paths
ORDERS_CSV = "data/orders.csv"
FEEDBACK_CSV = "data/feedback.csv"
USER_LOG_CSV = "data/user_activity_log.csv"
OFF_HOUR_USERS_CSV = "data/offhour_users.csv"
PROMO_LOG_CSV = "data/promo_sent_log.csv"

# Operational hours
CUT_OFF_HOUR = 7  # 7 AM cut-off

# Order status
ORDER_STATUS = {
    "PENDING": "Pending",
    "PAID": "Paid",
    "READY": "Ready",
    "DELIVERED": "Delivered",
    "COMPLETED": "Completed"
}