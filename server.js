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

// Serve the main HTML file for the root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Payment Chart App server is running on http://localhost:${PORT}`);
  console.log(`API endpoint available at http://localhost:${PORT}/api/chartdata`);
});
