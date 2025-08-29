const express = require('express');
const fs = require('fs');
const path = require('path');
const logger = require('./utils/logger');
const webhookRouter = require('./handlers/webhookHandler');
const { scheduleDailyTasks } = require('./handlers/reminderHandler');

const app = express();
app.use(express.json());

// Ensure data directory exists
fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });

// Serve static UI files
app.use(express.static(path.join(__dirname, 'public')));

// Register routes
app.use('/webhook', webhookRouter);

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start scheduler
scheduleDailyTasks();

const port = process.env.PORT || 5000;
app.listen(port, () => {
  logger.info(`Starting Express server on port ${port}`);
});
