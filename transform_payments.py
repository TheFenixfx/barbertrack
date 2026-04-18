#!/usr/bin/env python3
"""
Payment Transformer for Visualization

Purpose:
    Transform raw payment CSV data into JSON format for web visualization.
    
    Each CSV entry represents a day's remaining balance:
    - The Amount shows the prepaid balance remaining on that day
    - When a payment is made, the balance increases
    - Each working day, the daily rate is subtracted
    - When balance reaches $0, debt starts accumulating

    Visualization logic:
    - Show each day as a colored block
    - Block height represents the balance amount
    - Color indicates payment status (paid vs debt)

Rate Schedule:
    - 2025: $7/day for barbers (Alejandro, Andres, David), $5/day for Genesis
    - 2026: $8/day for barbers, $6/day for Genesis
    
    Sundays are always skipped (no charge).

Input:
    CSV files with columns: startDate, endDate, link, Operation, Amount
    
Output:
    data.json file with visualization entries

Author: Barberia Payment System
Date: 2026-04-11
"""

import csv
import json
from datetime import datetime
from pathlib import Path


def parse_date(date_string):
    """Parse date string in YYYY-MM-DD format."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string.strip(), '%Y-%m-%d')
    except ValueError:
        return None


def parse_amount(amount_string):
    """Parse amount to float."""
    if amount_string is None or str(amount_string).strip() in ['', 'null', 'None']:
        return 0
    try:
        return float(str(amount_string).strip())
    except ValueError:
        return 0


def process_barber_csv(csv_path):
    """
    Convert a barber's CSV file to visualization entries.
    Simply reads the CSV and converts to JSON format.
    """
    entries = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = (row.get('startDate') or row.get('endDate', '')).strip()
            amount = parse_amount(row.get('Amount'))
            operation = row.get('Operation', '').strip() if row.get('Operation') else ''
            link = row.get('link', '').strip() if row.get('link') else ''
            
            if date_str:
                entries.append({
                    'startDate': date_str,
                    'endDate': date_str,
                    'link': link,
                    'Operation': operation,
                    'Amount': amount
                })
    
    # Sort by date
    entries.sort(key=lambda x: x['startDate'])
    
    return entries


def main():
    """Main function to process all barber CSV files."""
    barbers_dir = Path('barbers')
    
    if not barbers_dir.exists():
        print(f"Error: Directory '{barbers_dir}' does not exist")
        return
    
    # Find CSV files
    csv_files = [
        f for f in barbers_dir.iterdir() 
        if f.suffix.lower() == '.csv' and not f.name.endswith('_debt.csv')
    ]
    
    if not csv_files:
        print(f"No CSV files found in '{barbers_dir}'")
        return
    
    print(f"Found {len(csv_files)} barber CSV files")
    print("-" * 50)
    
    # Process each barber
    teams_data = {}
    
    for csv_path in sorted(csv_files):
        barber_name = csv_path.stem
        entries = process_barber_csv(csv_path)
        teams_data[barber_name] = entries
        print(f"+ {barber_name}: {len(entries)} entries")
    
    # Write to data.json
    output_data = {'teams': teams_data}
    output_path = Path('data.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print("-" * 50)
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()