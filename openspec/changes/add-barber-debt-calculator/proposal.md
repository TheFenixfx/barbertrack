## Why
The barber shop needs an automated way to calculate debt from the last known payment date for each barber, excluding Sundays from the calculation, to track outstanding payments accurately.

## What Changes
- Add Python script to process barber CSV files
- Calculate days passed from last payment date to current date
- Exclude Sundays from day count calculation
- Calculate debt amount at $7 per day
- Generate output CSV files with barber name + "_debt" suffix
- Parse date information from existing CSV file structure

## Impact
- Affected specs: New capability "data-processing"
- Affected code: New Python script in project root
- New files: Python processing script, sample debt calculation files