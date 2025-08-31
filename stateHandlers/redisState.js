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

async function setBranch(phone, branch) {
  try {
    const cart = await getCart(phone);
    cart.branch = branch;
    await redis.set(`cart:${phone}`, JSON.stringify(cart));
  } catch (err) {
    logger.error(`Failed to set branch for ${phone}: ${err.message}`);
  }
}

module.exports = {
  getUserState,
  setUserState,
  clearUserState,
  getCart,
  addToCart,
  setBranch,
};
