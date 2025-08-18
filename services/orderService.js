const { appendToCsv } = require('../utils/csvUtils');
const { ORDERS_CSV } = require('../config/settings');
const { formatISTDateTime } = require('../utils/timeUtils');
const logger = require('../utils/logger');

function confirmOrder(whatsappNumber, paymentType, orderId, paid = false) {
  const timestamp = formatISTDateTime();
  appendToCsv(ORDERS_CSV, {
    timestamp,
    whatsapp_number: whatsappNumber,
    order_id: orderId,
    payment_type: paymentType,
    payment_status: paid ? 'Paid' : 'Pending'
  });
  logger.info(`Order confirmed for ${whatsappNumber}`);
}

module.exports = { confirmOrder };
