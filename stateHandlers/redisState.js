const Redis = require('ioredis');
const { REDIS_URL } = require('../config/credentials');

const redis = new Redis(REDIS_URL);

async function getUserState(phone) {
  const data = await redis.get(`state:${phone}`);
  return data ? JSON.parse(data) : null;
}

async function setUserState(phone, state) {
  await redis.set(`state:${phone}`, JSON.stringify(state));
}

async function clearUserState(phone) {
  await redis.del(`state:${phone}`);
}

async function getCart(phone) {
  const data = await redis.get(`cart:${phone}`);
  return data ? JSON.parse(data) : { items: [], branch: null };
}

async function addToCart(phone, name, quantity, price) {
  const cart = await getCart(phone);
  cart.items.push({ name, quantity, price });
  await redis.set(`cart:${phone}`, JSON.stringify(cart));
}

async function setBranch(phone, branch) {
  const cart = await getCart(phone);
  cart.branch = branch;
  await redis.set(`cart:${phone}`, JSON.stringify(cart));
}

module.exports = { getUserState, setUserState, clearUserState, getCart, addToCart, setBranch };
