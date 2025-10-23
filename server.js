const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the public directory
app.use(express.static('public'));

// API endpoint to get chart data
app.get('/api/chartdata', (req, res) => {
  try {
    const dataPath = path.join(__dirname, 'data.json');
    const data = fs.readFileSync(dataPath, 'utf8');
    const jsonData = JSON.parse(data);
    res.json(jsonData);
  } catch (error) {
    console.error('Error reading data.json:', error);
    res.status(500).json({ error: 'Failed to load chart data' });
  }
});

app.get('/api/debts', (req, res) => {
  try {
    const barbersDir = path.join(__dirname, 'barbers');
    const files = fs.readdirSync(barbersDir);
    const debtSummaries = files
      .filter((file) => file.endsWith('_debt.csv'))
      .map((file) => {
        const filePath = path.join(barbersDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split(/\r?\n/).filter((line) => line.trim().length > 0);

        if (lines.length < 2) {
          return null;
        }

        const dataLine = lines[1].split(',');
        const days = parseInt(dataLine[0], 10);
        const amount = parseFloat(dataLine[1]);
        const name = path.basename(file, '_debt.csv');

        return {
          name,
          days,
          amount
        };
      })
      .filter((entry) => entry !== null)
      .sort((a, b) => b.amount - a.amount);

    res.json({ debts: debtSummaries });
  } catch (error) {
    console.error('Error reading debt CSV files:', error);
    res.status(500).json({ error: 'Failed to load debt summaries' });
  }
});

// Serve the main HTML file for the root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Payment Chart App server is running on http://localhost:${PORT}`);
  console.log(`API endpoint available at http://localhost:${PORT}/api/chartdata`);
});
