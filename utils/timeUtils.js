/**
 * Return current time in Indian Standard Time
 */
function getCurrentIST() {
  const now = new Date();
  // Convert to IST (UTC+5:30)
  const istOffset = 5.5 * 60 * 60 * 1000;
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  return new Date(utc + istOffset);
}

/**
 * Format a date object in IST using the provided format string.
 * Supported tokens: YYYY, MM, DD, HH, mm, ss
 * @param {Date} [date] - date object to format (defaults to now in IST)
 * @param {string} [formatStr]
 * @returns {string}
 */
function formatISTDateTime(date = getCurrentIST(), formatStr = 'YYYY-MM-DD HH:mm:ss') {
  const pad = (n) => n.toString().padStart(2, '0');
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());
  return formatStr
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * Check if current time is within business hours (9 AM to 9 PM IST)
 * @returns {boolean}
 */
function isBusinessHours() {
  const now = getCurrentIST();
  return now.getHours() >= 9 && now.getHours() < 21;
}

module.exports = { getCurrentIST, formatISTDateTime, isBusinessHours };
