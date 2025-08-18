const { appendCsvRow } = require('../utils/csvUtils');
const { ORDERS_CSV } = require('../config/settings');
const { getCurrentIST } = require('../utils/timeUtils');
const logger = require('../utils/logger');

function confirmOrder(whatsappNumber, paymentType, orderId, paid=false) {
  const timestamp = getCurrentIST().toISOString();
  appendCsvRow(ORDERS_CSV, [timestamp, whatsappNumber, orderId, paymentType, paid ? 'Paid' : 'Pending']);
  logger.info(`Order confirmed for ${whatsappNumber}`);
}

module.exports = { confirmOrder };
