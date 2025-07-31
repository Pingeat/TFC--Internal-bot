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

# STAFF_ROLES = {
#     "+919064060132": "chef",    # Sochin
#     "+918927830590": "chef",    # Sagar
#     "+919391727848": "supervisor",  # Krishna
#     "+919346647165": "delivery"     # Ashok
# }

# Staff assignments - maps staff to categories they handle
STAFF_ASSIGNMENTS = {
    "sochin": ["custard", "oatmeal", "mango custard", "less sugar custards"],
    "sagar": ["delights", "apricot delight", "strawberry delight", "blueberry delight"],
    "krishna": ["supervisor"],  # Gets order notifications
    "ashok": ["delivery"]       # Gets delivery list
}

# Category display names for messages
CATEGORY_DISPLAY_NAMES = {
    "custard": "Custard Items",
    "oatmeal": "Oatmeal Items",
    "mango custard": "Mango Custard",
    "less sugar custards": "Less Sugar Custards",
    "delights": "Delights Items",
    "apricot delight": "Apricot Delight",
    "strawberry delight": "Strawberry Delight",
    "blueberry delight": "Blueberry Delight",
    "fruits": "Fruits",
    "others": "Other Items",
    "delivery": "Delivery List"
}

# Product categories
PRODUCT_CATEGORIES = {
    "custard": ["custard", "custard can"],
    "oatmeal": ["oatmeal"],
    "mango custard": ["mango custard", "mangoo custard"],
    "less sugar custards": ["less sugar"],
    "delights": ["delight", "delights"],
    "apricot delight": ["apricot"],
    "strawberry delight": ["strawberry"],
    "blueberry delight": ["blueberry"],
    "fruits": ["apple", "banana", "pineapple", "papaya", "watermelon", "muskmelon", "kiwi"],
    "others": ["hand gloves", "tissues", "sandwich", "paper bowl", "glass jar", "head cap", "party pack", 
               "mayonnaise", "cashew", "waste cloth", "fork", "oreo", "ice pops", "honey", "family pack", 
               "caps", "walnut", "custard post cards"]
}

# Product catalog mapping (ID -> Name and Price)
PRODUCT_CATALOG = {
    "1.00": {"name": "Apple 1kg", "price": 100, "category": "fruits"},
    "2.00": {"name": "Avacado 1pc", "price": 200, "category": "fruits"},
    "3.00": {"name": "Choco chips packet", "price": 300, "category": "others"},
    "4.00": {"name": "Tissues (10 pack)", "price": 400, "category": "others"},
    "5.00": {"name": "Sandwich kit (all vegetables)", "price": 500, "category": "others"},
    "6.00": {"name": "Paper bowl for fruit bowl 350ML", "price": 100, "category": "others"},
    "7.00": {"name": "Pineapple", "price": 60, "category": "fruits"},
    "8.00": {"name": "Papaya 1psc", "price": 70, "category": "fruits"},
    "9.00": {"name": "Glass jars reg 72 pcs with caps", "price": 80, "category": "others"},
    "10.00": {"name": "Watermelon 1pc", "price": 60, "category": "fruits"},
    "11.00": {"name": "Head Cap Pack Of 100", "price": 90, "category": "others"},
    "12.00": {"name": "Party pack boxes", "price": 300, "category": "others"},
    "13.00": {"name": "Mayonnaise 1Kg", "price": 20, "category": "others"},
    "14.00": {"name": "Custard - 1 can", "price": 40, "category": "custard"},
    "15.00": {"name": "Sandwich packing box (pack of 50)", "price": 51, "category": "others"},
    "16.00": {"name": "Cashew 1kg", "price": 52, "category": "others"},
    "17.00": {"name": "Waste cloth pack of 5", "price": 43, "category": "others"},
    "18.00": {"name": "Muskmelon 1psc", "price": 50, "category": "fruits"},
    "19.00": {"name": "Glass jar caps pack of 50", "price": 67, "category": "others"},
    "20.00": {"name": "Fork 14cm", "price": 68, "category": "others"},
    "21.00": {"name": "Oreo biscuit", "price": 69, "category": "others"},
    "22.00": {"name": "Kiwi 3psc", "price": 90, "category": "fruits"},
    "23.00": {"name": "Ice pops (pack of 20)", "price": 100, "category": "others"},
    "24.00": {"name": "Fruit Custard", "price": 760, "category": "custard"},
    "25.00": {"name": "Honey 1kg", "price": 900, "category": "others"},
    "26.00": {"name": "Glass Jar - 300ml with caps", "price": 880, "category": "others"},
    "27.00": {"name": "Mangoo custard - 1 kg", "price": 780, "category": "mango custard"},
    "28.00": {"name": "Family pack container", "price": 540, "category": "others"},
    "29.00": {"name": "Caps", "price": 300, "category": "others"},
    "30.00": {"name": "Walnut 250g", "price": 200, "category": "others"},
    "31.00": {"name": "Custard post cards", "price": 220, "category": "others"},
    "32.00": {"name": "Glass jars mini 80 pcs", "price": 230, "category": "others"}
}

# Product prices (for fallback if catalog ID not found)
PRODUCT_PRICES = {
    "custard can": 40,
    "mango custard": 780,
    "oatmeal": 180,
    "less sugar custards": 160,
    "apricot delight": 220,
    "strawberry delight": 220,
    "blueberry delight": 220,
    "banana": 50,
    "apple": 100,
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

# Add staff roles mapping
STAFF_ROLES = {
    "+919064060132": "chef",    # Sochin
    "+918927830590": "chef",    # Sagar
    "+919391727848": "supervisor",  # Krishna
    "+919346647165": "delivery"     # Ashok
}
# STAFF_ROLES = {
#     "+918074301029": "chef",    # Sochin
#     "+918074301029": "chef",    # Sagar
#     "+918074301029": "supervisor",  # Krishna
#     "+918074301029": "delivery"     # Ashok
# }

# Status progression rules
STATUS_PROGRESSION = {
    "Pending": ["Paid"],
    "Paid": ["Ready"],
    "Ready": ["Delivered"],
    "Delivered": ["Completed"]
}