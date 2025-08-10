# Payment Chart Application

A full-stack web application that displays payment status charts with clickable payment blocks. Built with Node.js/Express backend and vanilla HTML/CSS/JavaScript frontend.

## Features

- **Interactive Payment Chart**: Visualizes payment periods as stacked blocks for different teams
- **Clickable Payment Blocks**: Each payment block is clickable and opens a WhatsApp message with payment details
- **Scrollable Timeline**: Y-axis timeline with date labels in dd/mm/yy format
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data**: Reads from data.json file for easy manual updates

## Project Structure

```
payment-chart-app/
├── package.json          # Node.js dependencies and scripts
├── server.js            # Express server with API endpoint
├── data.json            # Payment data (manually editable)
├── public/
│   ├── index.html       # Main HTML file
│   ├── styles.css       # CSS styling
│   └── chart.js         # Frontend JavaScript logic
└── README.md            # This file
```

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start the Server**:
   ```bash
   npm start
   ```

3. **Access the Application**:
   Open your browser and go to: `http://localhost:3000`

## Data Management

The application reads payment data from `data.json`. To add or modify payments:

1. **Edit the data.json file** with your payment records
2. **Restart the server** for changes to take effect
3. **Refresh the browser** to see the updated chart

### Data Structure

```json
{
  "teams": {
    "Team Name": [
      {
        "startDate": "YYYY-MM-DD",
        "endDate": "YYYY-MM-DD",
        "link": "https://example.com/payment-link"
      }
    ]
  }
}
```

**Note**: The original `link` field in the data is replaced by WhatsApp links that include the team name and date range.

## API Endpoints

- **GET /**: Serves the main application
- **GET /api/chartdata**: Returns the payment data from data.json

## How It Works

### Backend (server.js)
- Serves static files from the `public` directory
- Provides `/api/chartdata` endpoint that reads and returns data.json
- Handles errors gracefully

### Frontend Features
- **Timeline**: Scrollable Y-axis with date labels for each day
- **Team Columns**: Each team gets its own column with a header
- **Payment Blocks**: Visual blocks positioned based on start/end dates
- **Interactive Links**: Clicking a block opens WhatsApp with a pre-filled message
- **Synchronized Scrolling**: Timeline and chart area scroll together

### WhatsApp Integration
When a payment block is clicked, it opens WhatsApp with a message like:
```
Payment details for Team Alpha - Period: 01/08/2025 to 07/08/2025
```

## Styling & Visual Features

- **Color-coded Blocks**: Different colors for visual distinction
- **Hover Effects**: Blocks change color and position on hover
- **Grid Lines**: Horizontal lines for each day on the timeline
- **Responsive Design**: Adapts to different screen sizes
- **Smooth Animations**: CSS transitions for better UX

## Customization

### Modify Colors
Edit the CSS gradients in `public/styles.css`:
```css
.payment-block {
    background: linear-gradient(135deg, #3498db, #2980b9);
}
```

### Adjust Timeline Scale
Change the pixels per day in `public/chart.js`:
```javascript
this.pixelsPerDay = 40; // Height of each day in pixels
```

### Update WhatsApp Message Format
Modify the `createWhatsAppLink` method in `public/chart.js`.

## Browser Compatibility

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge
- Mobile browsers

## Development

For development with auto-restart, you can use nodemon:
```bash
npm install -g nodemon
nodemon server.js
```

## Troubleshooting

1. **Port Already in Use**: Change the PORT in server.js or set environment variable
2. **Data Not Loading**: Check that data.json is valid JSON format
3. **WhatsApp Links Not Working**: Ensure the device has WhatsApp installed
4. **Styling Issues**: Clear browser cache and refresh

## License

MIT License - Feel free to use and modify as needed.
