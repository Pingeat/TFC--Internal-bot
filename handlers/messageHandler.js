const {
  sendTextMessage,
  sendBranchSelectionMessage,
  sendFullCatalog,
  sendCartSummary,
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
    } else if (type === 'order') {
      try {
        const items = msg.order?.product_items || [];
        if (!items.length) {
          logger.warn(`Order message from ${sender} contained no items`);
          await sendTextMessage(sender, '❌ No items found in your order. Please try again.');
        } else if (!state.branch) {
          logger.warn(`Order received from ${sender} without branch`);
          await sendBranchSelectionMessage(sender);
          await redisState.setUserState(sender, { step: 'SELECT_BRANCH' });
        } else {
          for (const item of items) {
            const productId = item.product_retailer_id || 'unknown';
            const quantity = parseInt(item.quantity || '1', 10);
            const price = parseFloat(item.item_price || item.price || '0');
            await redisState.addToCart(sender, productId, quantity, price);
            logger.info(`Added ${quantity}x ${productId} @ ₹${price} for ${sender}`);
          }
          await sendCartSummary(sender);
        }
      } catch (err) {
        logger.error(`Error processing order message for ${sender}: ${err.message}`);
        await sendTextMessage(sender, '⚠️ There was an error adding items to your cart. Please try again.');
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
