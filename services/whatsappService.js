const axios = require('axios');
const { META_ACCESS_TOKEN, WHATSAPP_API_URL } = require('../config/credentials');
const logger = require('../utils/logger');
const { generatePaymentLink } = require('../utils/paymentUtils');

async function sendTextMessage(to, message) {
  try {
    await axios.post(WHATSAPP_API_URL, {
      messaging_product: 'whatsapp',
      to,
      type: 'text',
      text: { body: message }
    }, {
      headers: {
        Authorization: `Bearer ${META_ACCESS_TOKEN}`
      }
    });
  } catch (err) {
    logger.error(`Failed to send message to ${to}: ${err.message}`);
  }
}

// Placeholder functions to mirror Python structure
function sendDailyDeliveryList() {
  logger.info('Sending daily delivery list (not implemented).');
}

function sendProductionLists() {
  logger.info('Sending production lists (not implemented).');
}

/**
 * Send a payment link message to the user.
 * @param {string} to
 * @param {string} orderId
 * @param {number} amount
 */
async function sendPaymentLink(to, orderId, amount) {
  try {
    const paymentLink = await generatePaymentLink(to, amount, orderId);
    const message =
      `💳 *PAYMENT REQUIRED*\n\n` +
      `Please complete payment for your order #${orderId}:\n\n` +
      `Amount: ₹${amount}\n\n` +
      `Payment Link: ${paymentLink}\n\n` +
      `You will receive order confirmation after payment is successful.`;
    return sendTextMessage(to, message);
  } catch (err) {
    logger.error(`Failed to send payment link: ${err.message}`);
    return null;
  }
}

module.exports = {
  sendTextMessage,
  sendDailyDeliveryList,
  sendProductionLists,
  sendPaymentLink,
};
