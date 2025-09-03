const axios = require('axios');
const {
  META_ACCESS_TOKEN,
  WHATSAPP_API_URL,
  WHATSAPP_CATALOG_ID,
} = require('../config/credentials');
const {
  BRANCHES,
  PAYMENT_BRANCHES,
  ORDERS_CSV,
  SUPERVISORS,
  CHEF_CONTACTS,
  DELIVERY_CONTACTS,
} = require('../config/settings');
const logger = require('../utils/logger');
const { generatePaymentLink } = require('../utils/paymentUtils');
const redisState = require('../stateHandlers/redisState');
const { readCsv } = require('../utils/csvUtils');

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

// Utility helpers
function toTitleCase(str) {
  return str.replace(/\b\w/g, (c) => c.toUpperCase());
}

function parseItems(itemsStr) {
  if (!itemsStr) return [];
  try {
    const parsed = JSON.parse(itemsStr);
    if (Array.isArray(parsed)) return parsed;
  } catch (e) {
    // fall back to semi-colon separated format "Item xQty"
  }
  return itemsStr
    .split(/;|\n/)
    .map((part) => {
      const match = part.trim().match(/(.+?)\s*x\s*(\d+)/i);
      if (match) {
        return { name: match[1].trim(), quantity: parseInt(match[2], 10) };
      }
      return null;
    })
    .filter(Boolean);
}

function categorizeProduct(name) {
  const lower = name.toLowerCase();
  if (lower.includes('mango custard')) return 'mango custard';
  if (lower.includes('less sugar')) return 'less sugar custards';
  if (lower.includes('oatmeal')) return 'oatmeal';
  if (lower.includes('custard')) return 'custard';
  if (lower.includes('apricot')) return 'apricot delight';
  if (lower.includes('strawberry')) return 'strawberry delight';
  if (lower.includes('blueberry')) return 'blueberry delight';
  if (lower.includes('delight')) return 'delights';
  return null;
}

function aggregateOrders(orders) {
  const categoryTotals = {};
  const branchTotals = {};

  orders.forEach((order) => {
    const branch = (order.Branch || '').toLowerCase();
    if (!branch) return;
    if (!branchTotals[branch]) branchTotals[branch] = {};

    const items = parseItems(order.Items);
    items.forEach((item) => {
      const name = item.name || '';
      const qty = parseInt(item.quantity, 10) || 0;
      const lowerName = name.toLowerCase();

      if (!branchTotals[branch][lowerName]) branchTotals[branch][lowerName] = 0;
      branchTotals[branch][lowerName] += qty;

      const category = categorizeProduct(lowerName);
      if (category) {
        if (!categoryTotals[category]) categoryTotals[category] = 0;
        categoryTotals[category] += qty;
      }
    });
  });

  return { categoryTotals, branchTotals };
}

// Send daily delivery list to delivery staff
async function sendDailyDeliveryList() {
  try {
    const orders = readCsv(ORDERS_CSV);
    if (!orders.length) {
      logger.info('No orders for delivery today');
      return;
    }
    const { branchTotals } = aggregateOrders(orders);

    let message = '🚚 *DAILY DELIVERY LIST*\n\n';
    Object.keys(branchTotals).forEach((branch) => {
      message += `*${toTitleCase(branch)}*\n`;
      const products = branchTotals[branch];
      Object.keys(products).forEach((product) => {
        message += `• ${toTitleCase(product)} x${products[product]}\n`;
      });
      message += '\n';
    });

    for (const to of DELIVERY_CONTACTS) {
      // eslint-disable-next-line no-await-in-loop
      await sendTextMessage(to, message);
    }
  } catch (err) {
    logger.error(`Failed to send delivery list: ${err.message}`);
  }
}

// Send production lists to chefs and supervisors
async function sendProductionLists() {
  try {
    const orders = readCsv(ORDERS_CSV);
    if (!orders.length) {
      logger.info('No orders for production today');
      return;
    }

    const { categoryTotals, branchTotals } = aggregateOrders(orders);

    const chefCategories = {
      custard: ['custard', 'oatmeal', 'mango custard', 'less sugar custards'],
      delight: ['delights', 'apricot delight', 'strawberry delight', 'blueberry delight'],
    };

    // Send category totals to each chef group
    for (const chef of Object.keys(CHEF_CONTACTS)) {
      const contacts = CHEF_CONTACTS[chef];
      const categories = chefCategories[chef] || [];
      let message = '📋 *PRODUCTION LIST*\n\n';
      categories.forEach((cat) => {
        const count = categoryTotals[cat] || 0;
        if (count) {
          message += `• ${toTitleCase(cat)} x${count}\n`;
        }
      });
      if (message.trim() === '📋 *PRODUCTION LIST*') continue; // nothing to send

      for (const to of contacts) {
        // eslint-disable-next-line no-await-in-loop
        await sendTextMessage(to, message);
      }
    }

    // Build consolidated branch-wise summary for supervisors
    let supMessage = '📊 *CONSOLIDATED PRODUCTION LIST*\n\n';
    Object.keys(branchTotals).forEach((branch) => {
      supMessage += `*${toTitleCase(branch)}*\n`;
      const products = branchTotals[branch];
      Object.keys(products).forEach((product) => {
        supMessage += `• ${toTitleCase(product)} x${products[product]}\n`;
      });
      supMessage += '\n';
    });

    for (const to of SUPERVISORS) {
      // eslint-disable-next-line no-await-in-loop
      await sendTextMessage(to, supMessage);
    }
  } catch (err) {
    logger.error(`Failed to send production lists: ${err.message}`);
  }
}

function sendDailyReminder() {
  const message =
    '⏰ *DAILY ORDER REMINDER*\n\n' +
    'Hello! Reminder to order any raw materials required today via WhatsApp bot. ' +
    'Cut-off: 7:00 AM tomorrow';
  logger.info(`Daily reminder message: ${message}`);
  // In a full implementation, this would send the message to branch managers
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

async function sendCartSummary(to) {
  try {
    logger.info(`Sending cart summary to ${to}`);
    const cart = await redisState.getCart(to);
    if (!cart.items.length) {
      const message = '🛒 *YOUR CART IS EMPTY*\n\nUse the catalog to add items to your cart.';
      return sendTextMessage(to, message);
    }

    let message = '🛒 *YOUR CART*\n\n';
    let total = 0;

    cart.items.forEach((item) => {
      const itemTotal = item.quantity * item.price;
      total += itemTotal;
      message += `• ${item.name} x${item.quantity} = ₹${itemTotal}\n`;
    });

    message += `\n*TOTAL*: ₹${total}\n\n`;

    await axios.post(
      WHATSAPP_API_URL,
      {
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to,
        type: 'interactive',
        interactive: {
          type: 'button',
          body: { text: message },
          action: {
            buttons: [
              {
                type: 'reply',
                reply: { id: 'continue_shopping', title: 'Continue Shopping' },
              },
              { type: 'reply', reply: { id: 'checkout', title: 'Checkout' } },
              { type: 'reply', reply: { id: 'clear_cart', title: 'Clear Cart' } },
            ],
          },
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
    logger.error(`Failed to send cart summary to ${to}: ${err.message}`);
  }
}

module.exports = {
  sendTextMessage,
  sendDailyDeliveryList,
  sendProductionLists,
  sendDailyReminder,
  sendPaymentLink,
  sendBranchSelectionMessage,
  sendFullCatalog,
  sendCartSummary,
};
