const fs = require('fs');
const path = require('path');

/**
 * Ensure that a CSV file exists with the provided headers.
 * @param {string} filePath
 * @param {string[]} headers
 */
function ensureCsvExists(filePath, headers) {
  try {
    if (!fs.existsSync(filePath)) {
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, headers.join(',') + '\n', 'utf8');
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(`[CSV_UTILS] Error creating CSV file ${filePath}: ${err.message}`);
  }
}

/**
 * Append an object as a row to a CSV file. Headers are inferred from the object keys.
 * @param {string} filePath
 * @param {object} data
 */
function appendToCsv(filePath, data) {
  try {
    const headers = Object.keys(data);
    ensureCsvExists(filePath, headers);

    // Read existing headers to maintain column order
    const firstLine = fs.readFileSync(filePath, 'utf8').split('\n')[0];
    const existingHeaders = firstLine ? firstLine.split(',') : headers;

    const row = existingHeaders.map((h) => data[h] !== undefined ? data[h] : '').join(',');
    fs.appendFileSync(filePath, row + '\n', 'utf8');
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(`[CSV_UTILS] Error appending to CSV ${filePath}: ${err.message}`);
    throw err;
  }
}

/**
 * Read a CSV file into an array of objects.
 * @param {string} filePath
 * @returns {object[]}
 */
function readCsv(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return [];
    }

    const lines = fs.readFileSync(filePath, 'utf8').trim().split('\n');
    const headers = lines.shift().split(',');
    return lines.map((line) => {
      const values = line.split(',');
      const row = {};
      headers.forEach((h, i) => {
        row[h] = values[i];
      });
      return row;
    });
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error(`[CSV_UTILS] Error reading CSV ${filePath}: ${err.message}`);
    return [];
  }
}

module.exports = { ensureCsvExists, appendToCsv, readCsv };

