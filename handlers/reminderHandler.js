const cron = require('node-cron');
const logger = require('../utils/logger');
const {
  sendDailyDeliveryList,
  sendProductionLists,
  sendDailyReminder,
} = require('../services/whatsappService');

function scheduleDailyTasks() {
  logger.info('Starting daily tasks scheduler');
  // Every day at 7:05 AM IST except Sunday
  cron.schedule('5 7 * * 1-6', () => {
    logger.info('Sending morning reminders at 7:05 AM');
    sendDailyReminder();
  }, { timezone: 'Asia/Kolkata' });

  cron.schedule('5 7 * * 1-6', () => {
    logger.info('Sending kitchen notifications at 7:05 AM');
    sendProductionLists();
    sendDailyDeliveryList();
  }, { timezone: 'Asia/Kolkata' });
}

module.exports = { scheduleDailyTasks };
