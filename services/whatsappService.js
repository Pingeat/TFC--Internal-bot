const axios = require('axios');
const {
  META_ACCESS_TOKEN,
  WHATSAPP_API_URL,
  WHATSAPP_CATALOG_ID,
} = require('../config/credentials');
const {
  BRANCHES,
  PAYMENT_BRANCHES,
} = require('../config/settings');
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

async function sendBranchSelectionMessage(to) {
  try {
    const sections = [
      {
        title: 'Select Branch',
        rows: BRANCHES.map((branch) => ({
          id: branch,
          title: branch.charAt(0).toUpperCase() + branch.slice(1),
          description: '',
        })),
      },
    ];
    await axios.post(
      WHATSAPP_API_URL,
      {
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to,
        type: 'interactive',
        interactive: {
          type: 'list',
          header: { type: 'text', text: '🏢 SELECT YOUR BRANCH' },
          body: { text: 'Please select your branch from the list below:' },
          footer: { text: 'Tap to select your branch' },
          action: { button: 'Select Branch', sections },
        },
      },
      {
        headers: {
          Authorization: `Bearer ${META_ACCESS_TOKEN}`,
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (err) {
    logger.error(`Failed to send branch selection: ${err.message}`);
  }
}

async function sendFullCatalog(to, branch = null) {
  try {
    const paymentRequired =
      branch && PAYMENT_BRANCHES.map((b) => b.toLowerCase()).includes(branch.toLowerCase());
    let catalogMessage = '🌟 *CENTRAL KITCHEN ORDERING SYSTEM*\n\n';
    if (paymentRequired) {
      catalogMessage += '⚠️ *Note*: Payment is required for your branch.\n\n';
    }
    catalogMessage += 'Please select a product from our catalog to add to cart.';
    await axios.post(
      WHATSAPP_API_URL,
      {
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to,
        type: 'interactive',
        interactive: {
          type: 'catalog_message',
          body: { text: catalogMessage },
          action: { name: 'catalog_message', catalog_id: WHATSAPP_CATALOG_ID },
        },
      },
      {
        headers: {
          Authorization: `Bearer ${META_ACCESS_TOKEN}`,
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (err) {
    logger.error(`Failed to send catalog: ${err.message}`);
  }
}

module.exports = {
  sendTextMessage,
  sendDailyDeliveryList,
  sendProductionLists,
  sendPaymentLink,
  sendBranchSelectionMessage,
  sendFullCatalog,
};
