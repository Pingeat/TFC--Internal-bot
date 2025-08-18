const { sendTextMessage } = require('../services/whatsappService');
const redisState = require('../stateHandlers/redisState');
const logger = require('../utils/logger');
const { BRANCHES } = require('../config/settings');

async function handleIncomingMessage(data) {
  try {
    const entry = data.entry?.[0];
    const change = entry?.changes?.[0];
    const value = change?.value || {};
    const messages = value.messages || [];
    if (!messages.length) {
      return ['No messages', 200];
    }
    const msg = messages[0];
    const sender = msg.from?.replace('+', '');
    const type = msg.type;
    let state = await redisState.getUserState(sender) || { step: 'SELECT_BRANCH' };

    if (type === 'text') {
      const text = msg.text?.body?.trim().toLowerCase();
      logger.info(`Message received from ${sender}: ${text}`);
      if (state.step === 'SELECT_BRANCH') {
        if (BRANCHES.includes(text)) {
          await redisState.setUserState(sender, { step: 'IN_CATALOG', branch: text });
          await sendTextMessage(sender, `✅ Selected ${text} branch. Send 'menu' to view items.`);
        } else {
          await sendTextMessage(sender, `Please choose a valid branch: ${BRANCHES.join(', ')}`);
        }
      } else if (text === 'hi' || text === 'hello') {
        await sendTextMessage(sender, 'Hello! How can I help you today?');
      } else {
        await sendTextMessage(sender, 'Command not recognized.');
      }
    } else {
      logger.warn(`Unhandled message type: ${type}`);
    }
    return ['Message processed', 200];
  } catch (err) {
    logger.error(`Message handler error: ${err.message}`);
    return ['Error processing message', 500];
  }
}

module.exports = { handleIncomingMessage };
