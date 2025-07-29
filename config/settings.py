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

# Product catalog mapping (ID -> Name and Price)
PRODUCT_CATALOG = {
    "1.00": {"name": "Apple 1kg", "price": 100},
    "2.00": {"name": "Avacado 1pc", "price": 200},
    "3.00": {"name": "Choco chips packet", "price": 300},
    "4.00": {"name": "Tissues (10 pack)", "price": 400},
    "5.00": {"name": "Sandwich kit (all vegetables)", "price": 500},
    "6.00": {"name": "Paper bowl for fruit bowl 350ML", "price": 100},
    "7.00": {"name": "Pineapple", "price": 60},
    "8.00": {"name": "Papaya 1psc", "price": 70},
    "9.00": {"name": "Glass jars reg 72 pcs with caps", "price": 80},
    "10.00": {"name": "Watermelon 1pc", "price": 60},
    "11.00": {"name": "Head Cap Pack Of 100", "price": 90},
    "12.00": {"name": "Party pack boxes", "price": 300},
    "13.00": {"name": "Mayonnaise 1Kg", "price": 20},
    "14.00": {"name": "Custard - 1 can", "price": 40},
    "15.00": {"name": "Sandwich packing box (pack of 50)", "price": 51},
    "16.00": {"name": "Cashew 1kg", "price": 52},
    "17.00": {"name": "Waste cloth pack of 5", "price": 43},
    "18.00": {"name": "Muskmelon 1psc", "price": 50},
    "19.00": {"name": "Glass jar caps pack of 50", "price": 67},
    "20.00": {"name": "Fork 14cm", "price": 68},
    "21.00": {"name": "Oreo biscuit", "price": 69},
    "22.00": {"name": "Kiwi 3psc", "price": 90},
    "23.00": {"name": "Ice pops (pack of 20)", "price": 100},
    "24.00": {"name": "Fruit Custard", "price": 760},
    "25.00": {"name": "Honey 1kg", "price": 900},
    "26.00": {"name": "Glass Jar - 300ml with caps", "price": 880},
    "27.00": {"name": "Mangoo custard - 1 kg", "price": 780},
    "28.00": {"name": "Family pack container", "price": 540},
    "29.00": {"name": "Caps", "price": 300},
    "30.00": {"name": "Walnut 250g", "price": 200},
    "31.00": {"name": "Custard post cards", "price": 220},
    "32.00": {"name": "Glass jars mini 80 pcs", "price": 230}
}

# Product prices (for fallback if catalog ID not found)
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