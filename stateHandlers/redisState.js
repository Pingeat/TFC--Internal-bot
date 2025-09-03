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

async function branchHasOrders(branch) {
  try {
    const count = await redis.llen(`orders:${branch.toLowerCase()}`);
    return count > 0;
  } catch (err) {
    logger.error(`Failed to check orders for ${branch}: ${err.message}`);
    return false;
  }
}

async function getBranchesWithOrders() {
  try {
    const keys = await redis.keys('orders:*');
    const branches = [];
    for (const key of keys) {
      const count = await redis.llen(key);
      if (count > 0) {
        branches.push(key.split(':')[1]);
      }
    }
    return branches;
  } catch (err) {
    logger.error(`Failed to fetch branches with orders: ${err.message}`);
    return [];
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

// Delivery status helpers
async function setBranchDeliveryStatus(branch, status) {
  try {
    const key = `delivery:${branch.toLowerCase()}`;
    const data = { status: status.toLowerCase(), updated_at: Date.now() };
    await redis.set(key, JSON.stringify(data));
  } catch (err) {
    logger.error(`Failed to set delivery status for ${branch}: ${err.message}`);
  }
}

async function markBranchDelivered(branch) {
  try {
    const key = `delivery:${branch.toLowerCase()}`;
    const existing = await redis.get(key);
    const payload = existing
      ? { ...JSON.parse(existing), status: 'delivered', updated_at: Date.now() }
      : { status: 'delivered', updated_at: Date.now() };
    const archiveKey = `delivery_archive:${branch.toLowerCase()}:${Date.now()}`;
    await redis.set(archiveKey, JSON.stringify(payload), 'EX', 3 * 24 * 60 * 60);
    await redis.del(key);
  } catch (err) {
    logger.error(`Failed to archive delivery status for ${branch}: ${err.message}`);
  }
}

async function getDeliveryStatuses() {
  try {
    const keys = await redis.keys('delivery:*');
    const result = {};
    for (const key of keys) {
      const branch = key.split(':')[1];
      const data = await redis.get(key);
      result[branch] = data ? JSON.parse(data).status : null;
    }
    return result;
  } catch (err) {
    logger.error(`Failed to fetch delivery statuses: ${err.message}`);
    return {};
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
  branchHasOrders,
  getBranchesWithOrders,
  getAllOrders,
  archiveOrders,
  setBranchDeliveryStatus,
  markBranchDelivered,
  getDeliveryStatuses,
};
