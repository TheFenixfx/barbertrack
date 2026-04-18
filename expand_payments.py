#!/usr/bin/env python3
"""
Payment Expander Script

Purpose:
    Expand single payment entries into daily decrementing balance entries.
    
    When a payment of $42 is made, it should cover 6 working days:
    Day 1: $42 (payment day)
    Day 2: $35
    Day 3: $28
    Day 4: $21
    Day 5: $14
    Day 6: $7
    Day 7: $0 (balance exhausted, debt starts)
    
    This script takes CSV files with unexpanded payments and creates
    properly expanded versions with daily balance decrements.

Rate Schedule:
    - 2025: $7/day for barbers (Alejandro, Andres, David), $5/day for Genesis
    - 2026: $8/day for barbers, $6/day for Genesis
    
    Sundays are skipped (no work/decrement on Sundays).

Input:
    Original CSV files in the specified directory (barbers/)
    
Output:
    Expanded CSV files in a new directory (barbers_expanded/)
    Does NOT modify original files.

Data Format:
    Input CSV columns:
    - startDate: Payment/entry date (YYYY-MM-DD)
    - endDate: Same as startDate for single entries
    - link: Image/screenshot reference
    - Operation: Payment reference code
    - Amount: Payment amount
    
    Output CSV keeps same format but with expanded daily entries.

Usage:
    python expand_payments.py [directory]
    
    Default directory: barbers

Author: Barberia Payment System
Date: 2026-04-11
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_daily_rate(date, barber_name):
    """
    Get daily decrement rate based on year and barber.
    
    Args:
        date: datetime object
        barber_name: Name of the barber
        
    Returns:
        Daily rate as float
    """
    is_genesis = barber_name.lower() == 'genesis'
    if date.year == 2025:
        return 5.0 if is_genesis else 7.0
    else:
        return 6.0 if is_genesis else 8.0


def is_sunday(date):
    """Check if date is Sunday (weekday 6)."""
    return date.weekday() == 6


def parse_date(date_string):
    """Parse date string in YYYY-MM-DD format."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string.strip(), '%Y-%m-%d')
    except ValueError:
        return None


def parse_amount(amount_string):
    """Parse amount to float, return None if invalid."""
    if amount_string is None or str(amount_string).strip() in ['', 'null', 'None']:
        return None
    try:
        return float(str(amount_string).strip())
    except ValueError:
        return None


def get_next_working_day(date):
    """Get the next working day (skip Sundays)."""
    next_day = date + timedelta(days=1)
    while is_sunday(next_day):
        next_day += timedelta(days=1)
    return next_day


def expand_payment(entry_date, amount, operation, link, barber_name):
    """
    Expand a single payment into daily entries with decrementing balance.
    
    Args:
        entry_date: datetime of the payment
        amount: Payment amount (float)
        operation: Payment reference code
        link: Image/screenshot reference
        barber_name: Name of the barber
        
    Returns:
        List of expanded entries (dicts with date, amount, operation, link)
    """
    if amount is None or amount <= 0:
        # Zero/negative amount - single entry only
        return [{
            'date': entry_date,
            'amount': amount,
            'operation': operation,
            'link': link
        }]
    
    daily_rate = get_daily_rate(entry_date, barber_name)
    
    # If amount is less than or equal to daily rate, it's a single day
    if amount <= daily_rate:
        return [{
            'date': entry_date,
            'amount': amount,
            'operation': operation,
            'link': link
        }]
    
    # Expand into multiple days
    expanded = []
    current_date = entry_date
    current_balance = amount
    
    while current_balance > 0:
        # Skip Sundays
        if is_sunday(current_date):
            current_date += timedelta(days=1)
            continue
        
        entry = {
            'date': current_date,
            'amount': round(current_balance, 2),
            'operation': operation,
            'link': link
        }
        expanded.append(entry)
        
        # Decrement balance
        current_balance -= daily_rate
        current_date = get_next_working_day(current_date)
    
    return expanded


def process_csv_file(input_path, output_path, barber_name):
    """
    Process a CSV file and expand payments into daily entries.
    
    Args:
        input_path: Path to original CSV file
        output_path: Path to save expanded CSV
        barber_name: Name of the barber
    """
    entries = []
    
    # Read original file
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            date = parse_date(row.get('startDate') or row.get('endDate'))
            amount = parse_amount(row.get('Amount'))
            operation = row.get('Operation', '').strip() if row.get('Operation') else ''
            link = row.get('link', '').strip() if row.get('link') else ''
            
            if date:
                entries.append({
                    'date': date,
                    'amount': amount,
                    'operation': operation,
                    'link': link,
                    'original_row': row
                })
    
    # Sort by date
    entries.sort(key=lambda x: x['date'])
    
    # Expand each entry
    expanded_entries = []
    previous_end_date = None
    
    for entry in entries:
        date = entry['date']
        amount = entry['amount']
        operation = entry['operation']
        link = entry['link']
        
        # Check if this needs expansion
        if amount and amount > 0 and operation:
            daily_rate = get_daily_rate(date, barber_name)
            
            if amount > daily_rate:
                # This payment needs expansion
                expanded = expand_payment(date, amount, operation, link, barber_name)
                
                # But we need to stop at the next existing payment date
                # Find next payment in original data
                next_payment_date = None
                entry_idx = entries.index(entry)
                for future_entry in entries[entry_idx + 1:]:
                    if future_entry['amount'] and future_entry['amount'] > 0 and future_entry['operation']:
                        next_payment_date = future_entry['date']
                        break
                
                # Trim expanded entries that go beyond next payment
                if next_payment_date:
                    expanded = [e for e in expanded if e['date'] < next_payment_date]
                
                expanded_entries.extend(expanded)
            else:
                # Already a single day entry
                expanded_entries.append({
                    'date': date,
                    'amount': amount,
                    'operation': operation,
                    'link': link
                })
        else:
            # Zero/null amount or no operation - keep as is
            expanded_entries.append({
                'date': date,
                'amount': amount or 0,
                'operation': operation,
                'link': link
            })
    
    # Sort expanded entries
    expanded_entries.sort(key=lambda x: x['date'])
    
    # Remove duplicates (same date, keep highest amount)
    deduplicated = []
    seen_dates = {}
    
    for entry in expanded_entries:
        date_str = entry['date'].strftime('%Y-%m-%d')
        if date_str in seen_dates:
            # Keep entry with higher amount (the payment)
            if entry['amount'] and entry['amount'] > seen_dates[date_str]['amount']:
                seen_dates[date_str] = entry
        else:
            seen_dates[date_str] = entry
    
    deduplicated = list(seen_dates.values())
    deduplicated.sort(key=lambda x: x['date'])
    
    # Write expanded file
    output_fieldnames = ['startDate', 'endDate', 'link', 'Operation', 'Amount']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        
        for entry in deduplicated:
            date_str = entry['date'].strftime('%Y-%m-%d')
            writer.writerow({
                'startDate': date_str,
                'endDate': date_str,
                'link': entry['link'],
                'Operation': entry['operation'] or '',
                'Amount': str(entry['amount']) if entry['amount'] else '0'
            })
    
    return len(deduplicated)


def main():
    """Main function to process all barber CSV files."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Expand payment entries into daily decrements")
    parser.add_argument(
        "directory",
        nargs="?",
        default="barbers",
        help="Directory containing barber CSV files (default: barbers)"
    )
    args = parser.parse_args()
    
    input_directory = Path(args.directory)
    
    if not input_directory.exists():
        print(f"Error: Directory '{input_directory}' does not exist")
        sys.exit(1)
    
    # Create output directory (don't modify originals)
    output_directory = input_directory.parent / f"{input_directory.name}_expanded"
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # Find CSV files
    csv_files = [
        entry for entry in input_directory.iterdir()
        if entry.suffix.lower() == '.csv' and not entry.name.endswith('_debt.csv')
    ]
    
    if not csv_files:
        print(f"No CSV files found in '{args.directory}'")
        sys.exit(0)
    
    print(f"Found {len(csv_files)} barber CSV files")
    print(f"Output directory: {output_directory}")
    print("-" * 50)
    
    for input_path in csv_files:
        barber_name = input_path.stem
        output_path = output_directory / input_path.name
        
        try:
            # Read original count
            with open(input_path, 'r', encoding='utf-8') as f:
                original_count = sum(1 for _ in f) - 1  # Minus header
            
            expanded_count = process_csv_file(input_path, output_path, barber_name)
            
            print(f"+ {barber_name}: {original_count} entries -> {expanded_count} expanded entries")
            
        except Exception as e:
            print(f"- {barber_name}: Error - {str(e)}")
    
    print("-" * 50)
    print(f"Expanded files saved to: {output_directory}")
    print("Original files unchanged.")


if __name__ == "__main__":
    main()