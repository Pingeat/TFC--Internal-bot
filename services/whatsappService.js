const axios = require('axios');
const { META_ACCESS_TOKEN, WHATSAPP_API_URL } = require('../config/credentials');
const logger = require('../utils/logger');

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

module.exports = { sendTextMessage, sendDailyDeliveryList, sendProductionLists };
