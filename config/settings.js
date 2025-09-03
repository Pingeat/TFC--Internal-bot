const BRANCHES = [
  'madhapur', 'kondapur', 'west maredpally', 'manikonda',
  'nanakramguda', 'nizampet', 'miyapur', 'pragathinagar'
];

const PAYMENT_BRANCHES = ['madhapur', 'west maredpally', 'miyapur', 'pragathinagar'];

const PRODUCT_CATALOG = require('./productCatalog.json');

const SUPERVISORS = [
  '+919391727848',
  '+919640112005',
  '+918074301029',
];

const SCHEDULED_MESSAGES_CSV = 'data/scheduled_messages.csv';

// Location of the orders log used for generating production and delivery lists
const ORDERS_CSV = 'orders.csv';
const FEEDBACK_CSV = 'data/feedback.csv';
const USER_LOG_CSV = 'data/user_activity_log.csv';
const OFF_HOUR_USERS_CSV = 'data/offhour_users.csv';
const PROMO_LOG_CSV = 'data/promo_sent_log.csv';

const CUT_OFF_HOUR = 7; // 7 AM cut-off

const ORDER_STATUS = {
  PENDING: 'Pending',
  PAID: 'Paid',
  READY: 'Ready',
  DELIVERED: 'Delivered',
  COMPLETED: 'Completed'
};

// Contact numbers grouped by roles
const CHEF_CONTACTS = {
  // Custard chef(s)
  custard: ['+919064060132', '+919640112005', '+918074301029'],
  // Delight chef(s)
  delight: ['+918927830590', '+919640112005','+918074301029']
};

// Delivery staff who should receive delivery lists
const DELIVERY_CONTACTS = ['+919346647165','+919640112005','+918074301029'];

module.exports = {
  BRANCHES,
  PAYMENT_BRANCHES,
  ORDERS_CSV,
  FEEDBACK_CSV,
  USER_LOG_CSV,
  OFF_HOUR_USERS_CSV,
  PROMO_LOG_CSV,
  PRODUCT_CATALOG,
  SUPERVISORS,
  SCHEDULED_MESSAGES_CSV,
  CUT_OFF_HOUR,
  ORDER_STATUS,
  CHEF_CONTACTS,
  DELIVERY_CONTACTS
};
