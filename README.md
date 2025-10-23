# Payment Chart Application

A full-stack web application that displays payment status charts with clickable payment blocks. Built with Node.js/Express backend and vanilla HTML/CSS/JavaScript frontend.

## Features

- **Interactive Payment Chart**: Visualizes payment periods as stacked blocks for different teams
- **Clickable Payment Blocks**: Each payment block is clickable and opens a WhatsApp message with payment details
- **Scrollable Timeline**: Y-axis timeline with date labels in dd/mm/yy format
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data**: Reads from data.json file for easy manual updates
- **Debt Calculation**: Python script to calculate debt from last payment date (excluding Sundays)

## Project Structure

```
payment-chart-app/
├── package.json          # Node.js dependencies and scripts
├── server.js            # Express server with API endpoint
├── calculate_debt.py    # Python debt calculation script
├── data.json            # Payment data (manually editable)
├── barbers/             # Barber CSV files
│   ├── Alejandro.csv    # Individual barber payment data
│   ├── David.csv        # Individual barber payment data
│   ├── Andres.csv       # Individual barber payment data
│   ├── Genesis.csv      # Individual barber payment data
│   └── *_debt.csv       # Generated debt reports
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
- **Timeline**: Scrollable Y-axis with date labels (bottom-to-top, most recent at bottom)
- **Team Columns**: Each team gets its own column with a header
- **Payment Blocks**: Visual blocks positioned based on start/end dates (green by default, red for most recent)
- **Interactive Links**: Clicking a block opens WhatsApp with a pre-filled message
- **Synchronized Scrolling**: Timeline and chart area scroll together
- **Auto-scroll**: Chart starts scrolled to bottom to show most recent payments first

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
nodemon server.jsc
```

## Debt Calculator

The project includes a Python script (`calculate_debt.py`) that calculates debt from the last payment date for each barber.

### Features
- **Automatic Date Processing**: Reads barber CSV files and finds the latest payment date
- **Sunday Exclusion**: Excludes Sundays from day count calculation (barbers don't work on Sundays)
- **$7/Day Rate**: Calculates debt at $7 per working day
- **Batch Processing**: Processes all barber CSV files in a directory
- **CSV Output**: Generates `[barber_name]_debt.csv` files with calculated results

### Usage

```bash
# Process all barber CSV files in default 'barbers' directory
python calculate_debt.py

# Process files in a specific directory
python calculate_debt.py /path/to/csv/files

# Show help information
python calculate_debt.py --help
```

### Input Format
The script expects CSV files with this structure:
```csv
startDate,endDate,link,Operation,Amount
2025-07-28,2025-07-28,backup_link,,amount
```

### Output Format
The script generates CSV files named `[barber_name]_debt.csv`:
```csv
days_passed,debt_amount
20,140.00
```

### Example Output
```
Found 4 barber CSV files to process...
--------------------------------------------------
Created debt report: barbers\Alejandro_debt.csv
+ Alejandro: 20 days, $140.00 debt
Created debt report: barbers\Andres_debt.csv
+ Andres: 26 days, $182.00 debt
Created debt report: barbers\David_debt.csv
+ David: 36 days, $252.00 debt
Created debt report: barbers\Genesis_debt.csv
+ Genesis: 33 days, $231.00 debt
--------------------------------------------------
Processing complete: 4/4 files processed successfully
```

## Troubleshooting

1. **Port Already in Use**: Change the PORT in server.js or set environment variable
2. **Data Not Loading**: Check that data.json is valid JSON format
3. **WhatsApp Links Not Working**: Ensure the device has WhatsApp installed
4. **Styling Issues**: Clear browser cache and refresh
5. **Python Script Issues**:
   - Ensure Python 3.6+ is installed
   - Check that CSV files have the correct format with `endDate` column
   - Verify directory permissions for reading input and writing output files

## License

MIT License - Feel free to use and modify as needed.
