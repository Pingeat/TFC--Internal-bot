const express = require('express');
const path = require('path');
const { handleIncomingMessage } = require('./messageHandler');
const { confirmOrder } = require('../services/orderService');
const { META_VERIFY_TOKEN } = require('../config/credentials');
const logger = require('../utils/logger');

const router = express.Router();

router.post('/', async (req, res) => {
  logger.info('Incoming POST request received.');
  const data = req.body;
  logger.debug && logger.debug(`Data received: ${JSON.stringify(data)}`);
  const [status, code] = await handleIncomingMessage(data);
  res.status(code).json({ status });
});

router.get('/', (req, res) => {
  logger.info('Verifying token...');
  const hubMode = req.query['hub.mode'];
  const hubToken = req.query['hub.verify_token'];
  const hubChallenge = req.query['hub.challenge'];
  if (hubMode === 'subscribe' && hubToken === META_VERIFY_TOKEN) {
    logger.info('Verification successful.');
    res.status(200).send(hubChallenge);
  } else {
    logger.warn('Verification failed.');
    res.status(403).send('Verification failed');
  }
});

router.get('/payment-success', (req, res) => {
  logger.info('Payment success callback received.');
  const whatsappNumber = req.query.whatsapp;
  const orderId = req.query.order_id;
  if (whatsappNumber && orderId) {
    confirmOrder(whatsappNumber, 'Online', orderId, true);
    res.status(200).send('Payment confirmed');
  } else {
    logger.error('Missing parameters in payment success callback');
    res.status(400).send('Missing parameters');
  }
});

router.post('/razorpay-webhook-tfcmarket', (req, res) => {
  logger.info('Razorpay webhook received.');
  const data = req.body;
  if (data.event === 'payment_link.paid') {
    const paymentData = data.payload?.payment_link?.entity || {};
    const whatsappNumber = paymentData.customer?.contact;
    const orderId = paymentData.reference_id;
    if (whatsappNumber && orderId) {
      confirmOrder(whatsappNumber, 'Online', orderId, true);
    }
  }
  res.status(200).send('OK');
});

router.get('/download-orders', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'data', 'orders.csv'));
});

router.get('/download-user-log', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'data', 'user_activity_log.csv'));
});

router.get('/download-offhour', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'data', 'offhour_users.csv'));
});

module.exports = router;
