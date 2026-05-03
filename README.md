# Payment Chart App

## Workflow Steps

1. **Backup CSV files**
   - Create a backup of existing barber CSV files before making changes
   - Backup location: `barbers/backup_YYYYMMDD_HHMMSS/`

2. **Replace CSV files**
   - Copy consolidated CSVs from `E:/Projects/Barberia/consolidated/` to `barbers/`

3. **Update debt calculation rates** (if needed)
   - Edit `calculate_debt.py` to adjust daily rates
   - Default rate: $8/day
   - Genesis special rate: $6/day
c
4. **Run debt calculator**
   - Execute `python calculate_debt.py`
   - Generates debt reports in `barbers/debts/`

5. **Combine CSVs to JSON**
   - Execute `python combine_csvs.py`
   - Reads all CSVs from `barbers/` and produces `data.json`

6. **Generate CSVs from JSON**
   - Execute `python generate_csvs.py`
   - Reads `data.json` and writes individual CSVs per barber

7. **Start server**
   - Run `node server.js`
   - Server mounted at `http://localhost:3000`
   - API endpoint: `http://localhost:3000/api/chartdata`

## Files

| File | Purpose |
|------|---------|
| `calculate_debt.py` | Calculates debt from last payment date |
| `combine_csvs.py` | Consolidates barbers CSVs into `data.json` |
| `generate_csvs.py` | Generates individual CSVs from `data.json` |
| `calculate_dollars.py` | Utility for converting amounts to USD |
| `server.js` | Node.js server for the payment chart app |

## Directory Structure

```
payment-chart-app/
├── barbers/
│   ├── Alejandro.csv
│   ├── Andres.csv
│   ├── David.csv
│   ├── Genesis.csv
│   └── debts/
│       ├── Alejandro_debt.csv
│       ├── Andres_debt.csv
│       ├── David_debt.csv
│       └── Genesis_debt.csv
├── data.json
├── server.js
├── calculate_debt.py
├── combine_csvs.py
├── generate_csvs.py
└── calculate_dollars.py
```