const Redis = require('ioredis');
const { REDIS_URL } = require('../config/credentials');
const logger = require('../utils/logger');

const redis = new Redis(REDIS_URL);

async function getUserState(phone) {
  try {
    const data = await redis.get(`state:${phone}`);
    return data ? JSON.parse(data) : null;
  } catch (err) {
    logger.error(`Failed to get state for ${phone}: ${err.message}`);
    return null;
  }
}

async function setUserState(phone, state) {
  try {
    await redis.set(`state:${phone}`, JSON.stringify(state));
  } catch (err) {
    logger.error(`Failed to set state for ${phone}: ${err.message}`);
  }
}

async function clearUserState(phone) {
  try {
    await redis.del(`state:${phone}`);
  } catch (err) {
    logger.error(`Failed to clear state for ${phone}: ${err.message}`);
  }
}

async function getCart(phone) {
  try {
    const data = await redis.get(`cart:${phone}`);
    return data ? JSON.parse(data) : { items: [], branch: null };
  } catch (err) {
    logger.error(`Failed to get cart for ${phone}: ${err.message}`);
    return { items: [], branch: null };
  }
}

async function addToCart(phone, name, quantity, price) {
  try {
    const cart = await getCart(phone);
    const existing = cart.items.find((item) => item.name === name);
    if (existing) {
      existing.quantity += quantity;
      existing.price = price;
    } else {
      cart.items.push({ name, quantity, price });
    }
    await redis.set(`cart:${phone}`, JSON.stringify(cart));
    logger.info(`Cart updated for ${phone}: ${quantity}x ${name} @ ₹${price}`);
    return cart;
  } catch (err) {
    logger.error(`Failed to add to cart for ${phone}: ${err.message}`);
    return null;
  }
}

async function clearCart(phone) {
  try {
    await redis.del(`cart:${phone}`);
    logger.info(`Cleared cart for ${phone}`);
    return true;
  } catch (err) {
    logger.error(`Failed to clear cart for ${phone}: ${err.message}`);
    return false;
  }
}

async function setBranch(phone, branch) {
  try {
    const cart = await getCart(phone);
    cart.branch = branch;
    await redis.set(`cart:${phone}`, JSON.stringify(cart));
  } catch (err) {
    logger.error(`Failed to set branch for ${phone}: ${err.message}`);
  }
}

async function savePendingOrder(orderId, data) {
  try {
    await redis.set(`pending:${orderId}`, JSON.stringify(data), 'EX', 24 * 60 * 60);
  } catch (err) {
    logger.error(`Failed to save pending order ${orderId}: ${err.message}`);
  }
}

async function getPendingOrder(orderId) {
  try {
    const data = await redis.get(`pending:${orderId}`);
    return data ? JSON.parse(data) : null;
  } catch (err) {
    logger.error(`Failed to get pending order ${orderId}: ${err.message}`);
    return null;
  }
}

async function deletePendingOrder(orderId) {
  try {
    await redis.del(`pending:${orderId}`);
  } catch (err) {
    logger.error(`Failed to delete pending order ${orderId}: ${err.message}`);
  }
}

async function addConfirmedOrder(order) {
  try {
    const key = `orders:${(order.branch || 'unknown').toLowerCase()}`;
    await redis.rpush(key, JSON.stringify(order));
  } catch (err) {
    logger.error(`Failed to save order ${order.order_id}: ${err.message}`);
  }
}

async function getAllOrders() {
  try {
    const keys = await redis.keys('orders:*');
    const orders = [];
    for (const key of keys) {
      const list = await redis.lrange(key, 0, -1);
      list.forEach((o) => orders.push(JSON.parse(o)));
    }
    return orders;
  } catch (err) {
    logger.error(`Failed to fetch orders: ${err.message}`);
    return [];
  }
}

async function archiveOrders() {
  try {
    const keys = await redis.keys('orders:*');
    const date = new Date().toISOString().slice(0, 10);
    for (const key of keys) {
      const archiveKey = key.replace('orders:', `archive:${date}:`);
      await redis.rename(key, archiveKey);
    }
  } catch (err) {
    logger.error(`Failed to archive orders: ${err.message}`);
  }
}

module.exports = {
  getUserState,
  setUserState,
  clearUserState,
  getCart,
  addToCart,
  clearCart,
  setBranch,
  savePendingOrder,
  getPendingOrder,
  deletePendingOrder,
  addConfirmedOrder,
  getAllOrders,
  archiveOrders,
};
