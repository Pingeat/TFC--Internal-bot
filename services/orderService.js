const { appendToCsv } = require('../utils/csvUtils');
const {
  ORDERS_CSV,
  SUPERVISORS,
  SCHEDULED_MESSAGES_CSV,
} = require('../config/settings');
const { formatISTDateTime, getCurrentIST } = require('../utils/timeUtils');
const { sendTextMessage } = require('./whatsappService');
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

function scheduleSupervisorReminders(orderId, branch, items) {
  const now = getCurrentIST();
  const sendAt = new Date(now);
  sendAt.setDate(sendAt.getDate() + 1);
  sendAt.setHours(7, 0, 0, 0);
  const sendAtStr = formatISTDateTime(sendAt);
  const itemLines = items
    .map((i) => `• ${i.name} x${i.quantity} - ₹${i.price * i.quantity}`)
    .join('\n');
  const total = items.reduce((sum, i) => sum + i.quantity * i.price, 0);
  const message = `Reminder: Order #${orderId}\nBranch: ${branch}\n\nItems:\n${itemLines}\n\nTotal: ₹${total}`;
  SUPERVISORS.forEach((sup) => {
    appendToCsv(SCHEDULED_MESSAGES_CSV, {
      send_at: sendAtStr,
      to: sup,
      message,
    });
  });
}

async function notifySupervisors(orderId, branch, items) {
  const itemLines = items
    .map((i) => `• ${i.name} x${i.quantity} - ₹${i.price * i.quantity}`)
    .join('\n');
  const total = items.reduce((sum, i) => sum + i.quantity * i.price, 0);
  for (const sup of SUPERVISORS) {
    await sendTextMessage(
      sup,
      `🆕 Order #${orderId}\nBranch: ${branch}\n\nItems:\n${itemLines}\n\nTotal: ₹${total}`
    );
  }
  scheduleSupervisorReminders(orderId, branch, items);
}

async function finalizeOrder(
  whatsappNumber,
  branch,
  items,
  paymentType,
  orderId,
  paid = false
) {
  confirmOrder(whatsappNumber, paymentType, orderId, paid);
  await notifySupervisors(orderId, branch, items);
}

module.exports = { confirmOrder, finalizeOrder };
