const fs = require('fs');
const path = require('path');

function appendCsvRow(filePath, row) {
  const line = row.join(',') + '\n';
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.appendFileSync(filePath, line, 'utf8');
}

module.exports = { appendCsvRow };
