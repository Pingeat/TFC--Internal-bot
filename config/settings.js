const BRANCHES = [
  'madhapur', 'kondapur', 'west maredpally', 'manikonda',
  'nanakramguda', 'nizampet', 'miyapur', 'pragathinagar'
];

const PAYMENT_BRANCHES = ['madhapur', 'west maredpally', 'miyapur', 'pragathinagar'];

const ORDERS_CSV = 'data/orders.csv';
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

module.exports = {
  BRANCHES,
  PAYMENT_BRANCHES,
  ORDERS_CSV,
  FEEDBACK_CSV,
  USER_LOG_CSV,
  OFF_HOUR_USERS_CSV,
  PROMO_LOG_CSV,
  CUT_OFF_HOUR,
  ORDER_STATUS
};
