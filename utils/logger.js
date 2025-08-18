const { createLogger, format, transports } = require('winston');
const { appendToCsv } = require('./csvUtils');
const { USER_LOG_CSV } = require('../config/settings');
const { formatISTDateTime } = require('./timeUtils');

const logger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.printf(({ timestamp, level, message }) => `${timestamp} [${level.toUpperCase()}] ${message}`)
  ),
  transports: [new transports.Console()]
});

/**
 * Log user activity to CSV and console
 * @param {string} userId
 * @param {string} activityType
 * @param {string} details
 */
function logUserActivity(userId, activityType, details) {
  logger.info(`${userId} - ${activityType}: ${details}`);
  try {
    const logEntry = {
      timestamp: formatISTDateTime(),
      user_id: userId,
      activity_type: activityType,
      details,
    };
    appendToCsv(USER_LOG_CSV, logEntry);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(`[LOGGER] Failed to log to CSV: ${err.message}`);
  }
}

/**
 * Truncate a text to specified max length, adding ellipsis if needed
 * @param {string} text
 * @param {number} maxLength
 */
function truncateText(text, maxLength = 24) {
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}…` : text;
}

module.exports = Object.assign(logger, { logUserActivity, truncateText });
