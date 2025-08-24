const {
  sendTextMessage,
  sendBranchSelectionMessage,
  sendFullCatalog,
} = require('../services/whatsappService');
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
    let state = await redisState.getUserState(sender);

    // Reset to branch selection if state missing or invalid
    if (!state || !['SELECT_BRANCH', 'IN_CATALOG'].includes(state.step)) {
      await redisState.clearUserState(sender);
      await sendBranchSelectionMessage(sender);
      await redisState.setUserState(sender, { step: 'SELECT_BRANCH' });
      return ['Branch selection sent', 200];
    }

    if (type === 'interactive') {
      const interactiveType = msg.interactive?.type;
      if (interactiveType === 'list_reply') {
        const selectedBranch = msg.interactive?.list_reply?.id;
        if (BRANCHES.includes(selectedBranch)) {
          await redisState.setBranch(sender, selectedBranch);
          await redisState.setUserState(sender, {
            step: 'IN_CATALOG',
            branch: selectedBranch,
          });
          await sendFullCatalog(sender, selectedBranch);
        } else {
          await sendBranchSelectionMessage(sender);
        }
      } else {
        logger.warn(`Unhandled interactive type: ${interactiveType}`);
      }
    } else if (type === 'text') {
      const text = msg.text?.body?.trim().toLowerCase();
      logger.info(`Message received from ${sender}: ${text}`);
      const greetings = ['hi', 'hello', 'hey'];
      if (greetings.includes(text)) {
        await sendBranchSelectionMessage(sender);
        await redisState.setUserState(sender, { step: 'SELECT_BRANCH' });
      } else if (state.step === 'SELECT_BRANCH') {
        if (BRANCHES.includes(text)) {
          await redisState.setBranch(sender, text);
          await redisState.setUserState(sender, { step: 'IN_CATALOG', branch: text });
          await sendFullCatalog(sender, text);
        } else {
          await sendBranchSelectionMessage(sender);
        }
      } else if (text === 'menu') {
        await sendFullCatalog(sender, state.branch);
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
