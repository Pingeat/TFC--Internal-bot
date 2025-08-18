const axios = require('axios');
const { RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET } = require('../config/credentials');
const logger = require('./logger');

/**
 * Generate a Razorpay payment link with retry mechanism
 * @param {string} to - WhatsApp number
 * @param {number} total - Amount in INR
 * @param {string} orderId - Order identifier
 * @param {number} [maxRetries=3]
 * @param {number} [delay=1000] - delay between retries in ms
 * @returns {Promise<string|null>}
 */
async function generatePaymentLink(to, total, orderId, maxRetries = 3, delay = 1000) {
  const url = 'https://api.razorpay.com/v1/payment_links';

  if (total <= 0) {
    logger.error(`Invalid total amount: ${total}`);
    return null;
  }

  const payload = {
    amount: Math.round(total * 100),
    currency: 'INR',
    accept_partial: false,
    reference_id: orderId,
    description: 'Fruit Custard Order',
    customer: {
      name: 'Customer',
      contact: `+91${to.slice(-10)}`,
    },
    notify: { sms: true, email: false },
    reminder_enable: true,
    callback_url: 'https://yourdomain.com/razorpay-webhook-tfcmarket',
    callback_method: 'get',
  };

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      logger.info(`Attempt ${attempt + 1} to generate payment link for order ${orderId}`);
      const response = await axios.post(url, payload, {
        auth: { username: RAZORPAY_KEY_ID, password: RAZORPAY_KEY_SECRET },
        timeout: 10000,
      });

      if (response.status === 200 && response.data?.short_url) {
        logger.info(`Payment link generated successfully: ${response.data.short_url}`);
        return response.data.short_url;
      }

      if ([429, 500, 502, 503, 504].includes(response.status)) {
        logger.warn(`Razorpay API returned ${response.status}. Retrying in ${delay} ms`);
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }

      logger.error(`Failed to generate payment link. Status: ${response.status}, Response: ${response.data}`);
      break;
    } catch (err) {
      logger.warn(`Request exception on attempt ${attempt + 1}: ${err.message}`);
      if (attempt < maxRetries - 1) {
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }
      logger.error(`Error generating Razorpay link after all retries: ${err.message}`);
    }
  }
  return null;
}

module.exports = { generatePaymentLink };

