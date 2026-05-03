#!/usr/bin/env python3
"""
Barber Debt Calculator

Purpose:
    Calculate accumulated debt for each barber based on their payment records.
    
    Debt occurs when a barber's prepaid balance runs out (Amount=0) and they
    continue working without making a new payment. The script identifies:
    
    1. Historical debt gaps: Periods where Amount=0 followed by long gap to next payment
    2. Current debt: Gap from last payment date to today
    
    Days with positive Amount (remaining balance) are NOT counted as debt,
    even if there are gaps in the data - the prepaid balance covers those days.

Rate Schedule:
    - 2025: $7/day for barbers (Alejandro, Andres, David), $5/day for Genesis
    - 2026: $8/day for barbers (Alejandro, Andres, David), $6/day for Genesis
    
    Sundays are always excluded from debt calculations.

Output:
    Creates _debt.csv files in barbers/debts/ directory for each barber,
    containing total debt days and amount, plus breakdown by debt period.

Usage:
    python calculate_debt.py [directory]
    
    If no directory provided, defaults to 'barbers' directory.

Author: Barberia Payment System
Date: 2025-04-11
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate barber debt from payment records"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="barbers",
        help="Directory containing barber CSV files (default: barbers)"
    )
    return parser.parse_args()


def read_csv_file(file_path):
    """
    Read CSV file and return the data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of dictionaries containing CSV rows
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV file {file_path}: {str(e)}")


def parse_date(date_string):
    """
    Parse a date string in YYYY-MM-DD format.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string.strip(), '%Y-%m-%d')
    except ValueError:
        return None


def parse_amount(amount_string):
    """
    Parse amount field, handling various formats.
    
    Args:
        amount_string: Amount value (string, float, or None)
        
    Returns:
        float amount, 0 for null/empty, or None for invalid
    """
    if amount_string is None:
        return None
    amount_string = str(amount_string).strip()
    if not amount_string or amount_string in ['0', '0.0', 'null', 'None']:
        return 0
    try:
        return float(amount_string)
    except ValueError:
        return None


def is_sunday(date):
    """
    Check if a date is a Sunday.
    
    Args:
        date: datetime object
        
    Returns:
        True if Sunday (weekday 6), False otherwise
    """
    return date.weekday() == 6


def get_daily_rate(date, barber_name):
    """
    Get daily debt rate based on year and barber.
    
    Rate Schedule:
        2025: $7/day for barbers, $5/day for Genesis
        2026: $8/day for barbers, $6/day for Genesis
    
    Args:
        date: datetime object for the debt day
        barber_name: Name of the barber
        
    Returns:
        Daily rate as float
    """
    is_genesis = barber_name.lower() == 'genesis'
    if date.year == 2025:
        return 5.0 if is_genesis else 7.0
    else:
        return 6.0 if is_genesis else 8.0


def calculate_debt(csv_data, barber_name, current_date):
    """
    Calculate total debt for a barber.
    
    Debt Logic:
        TOTAL DEBT = Historical debt gaps + Current debt from last payment to today
        
        Historical debt gaps: Periods where Amount=0 (or very low) followed by 
        long gap to next payment. This captures the Oct-Dec 2025 gaps.
        
        Current debt: Gap from last payment date to today.
        
    Args:
        csv_data: List of CSV row dictionaries
        barber_name: Name of the barber
        current_date: datetime for today (to calculate current debt)
        
    Returns:
        Dictionary with:
        - total_days: Total debt days
        - total_debt: Total debt amount
        - debt_periods: List of debt period details
    """
    # Sort entries by date
    entries = []
    for row in csv_data:
        date = parse_date(row.get('endDate', '').strip())
        if date:
            amount = parse_amount(row.get('Amount'))
            operation = row.get('Operation')
            entries.append({
                'date': date,
                'amount': amount,
                'operation': operation
            })
    
    entries.sort(key=lambda x: x['date'])
    
    if not entries:
        return {'total_days': 0, 'total_debt': 0.0, 'debt_periods': []}
    
    total_debt = 0.0
    total_days = 0
    debt_periods = []
    
    # Invalid/null operation codes that indicate no real payment
    null_ops = ['null', 'None', '000000', '00000000', '000000000000', '']
    
    # STEP 1: Find all historical debt gaps (Amount=0 or <=5, followed by long gap)
    # We need to find the LAST consecutive debt entry before each payment gap
    # to avoid counting overlapping periods
    
    i = 0
    while i < len(entries):
        e = entries[i]
        amount = e['amount']
        operation = e['operation']
        date = e['date']
        
        # Check if this is a debt endpoint (Amount=0 or very low, no valid operation)
        is_debt_endpoint = False
        if amount == 0 or (amount and amount <= 5):
            op_str = str(operation).strip() if operation else ''
            if not op_str or op_str in null_ops:
                is_debt_endpoint = True
        
        if is_debt_endpoint:
            # Find the LAST consecutive debt endpoint before a payment
            last_debt_idx = i
            for k in range(i + 1, len(entries)):
                next_e = entries[k]
                next_amt = next_e['amount']
                next_op = next_e['operation']
                next_op_str = str(next_op).strip() if next_op else ''
                
                # Check if still in debt state
                if (next_amt == 0 or (next_amt and next_amt <= 5)) and (not next_op_str or next_op_str in null_ops):
                    last_debt_idx = k
                else:
                    break
            
            # Now find next real payment after the last debt entry
            next_payment = None
            for j in range(last_debt_idx + 1, len(entries)):
                next_e = entries[j]
                next_amount = next_e['amount']
                next_op = next_e['operation']
                
                # A real payment has positive amount and valid operation
                next_op_str = str(next_op).strip() if next_op else ''
                if next_amount and next_amount > 0 and next_op_str and next_op_str not in null_ops:
                    next_payment = next_e
                    break
            
            if next_payment:
                # Calculate gap from LAST debt entry to next payment
                last_debt_date = entries[last_debt_idx]['date']
                gap_start = last_debt_date + timedelta(days=1)
                gap_end = next_payment['date'] - timedelta(days=1)
                
                # Only count if gap is significant (more than 0 days)
                if gap_start <= gap_end:
                    gap_debt = 0.0
                    gap_days = 0
                    
                    temp = gap_start
                    while temp <= gap_end:
                        if not is_sunday(temp):
                            rate = get_daily_rate(temp, barber_name)
                            gap_debt += rate
                            gap_days += 1
                        temp += timedelta(days=1)
                    
                    if gap_days > 0:
                        total_debt += gap_debt
                        total_days += gap_days
                        debt_periods.append({
                            'from': gap_start.strftime('%Y-%m-%d'),
                            'to': gap_end.strftime('%Y-%m-%d'),
                            'days': gap_days,
                            'debt': gap_debt,
                            'type': 'historical_gap'
                        })
            
            # Skip to after the last debt entry we processed
            i = last_debt_idx + 1
        else:
            i += 1
    
    # STEP 2: Calculate current debt from last payment to today
    # Find the last entry with a valid payment
    last_payment_entry = None
    for e in reversed(entries):
        op = e['operation']
        amt = e['amount']
        op_str = str(op).strip() if op else ''
        if op_str and op_str not in null_ops:
            if amt and amt > 0:
                last_payment_entry = e
                break
    
    if last_payment_entry:
        last_payment_date = last_payment_entry['date']
        
        # Calculate days from last payment date to today (excluding Sundays)
        gap_start = last_payment_date + timedelta(days=1)
        gap_end = current_date
        
        current_gap_debt = 0.0
        current_gap_days = 0
        
        temp = gap_start
        while temp <= gap_end:
            if not is_sunday(temp):
                rate = get_daily_rate(temp, barber_name)
                current_gap_debt += rate
                current_gap_days += 1
            temp += timedelta(days=1)
        
        if current_gap_days > 0:
            total_debt += current_gap_debt
            total_days += current_gap_days
            debt_periods.append({
                'from': gap_start.strftime('%Y-%m-%d'),
                'to': gap_end.strftime('%Y-%m-%d'),
                'days': current_gap_days,
                'debt': current_gap_debt,
                'is_current': True,
                'last_payment': last_payment_date.strftime('%Y-%m-%d'),
                'last_amount': last_payment_entry['amount']
            })
    
    return {
        'total_days': total_days,
        'total_debt': total_debt,
        'debt_periods': debt_periods
    }


def extract_barber_name(file_path):
    """
    Extract barber name from file path.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Barber name (filename without extension)
    """
    return Path(file_path).stem


def write_debt_csv(barber_name, total_days, total_debt, output_directory, debt_periods=None):
    """
    Write debt information to a CSV file.
    
    Output format:
        Row 1: days_passed, debt_amount
        Row 2: total days, total amount
        Optional: Detailed breakdown of each debt period
    
    Args:
        barber_name: Name of the barber
        total_days: Total debt days
        total_debt: Total debt amount
        output_directory: Directory to save the file
        debt_periods: Optional list of debt period details
    """
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_filename = f"{barber_name}_debt.csv"
    output_path = output_directory / output_filename

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['days_passed', 'debt_amount'])
            writer.writerow([total_days, f"{total_debt:.2f}"])
            
            if debt_periods:
                writer.writerow([])
                writer.writerow(['from', 'to', 'days', 'debt', 'type', 'is_current'])
                for period in debt_periods:
                    is_current = 'yes' if period.get('is_current') else ''
                    period_type = period.get('type', 'current')
                    writer.writerow([
                        period['from'],
                        period['to'],
                        period['days'],
                        f"{period['debt']:.2f}",
                        period_type,
                        is_current
                    ])

        print(f"Created debt report: {output_path}")
        return output_path
    except Exception as e:
        raise Exception(f"Error writing debt CSV file {output_path}: {str(e)}")


def process_barber_file(file_path, output_directory):
    """
    Process a single barber CSV file and generate debt report.
    
    Args:
        file_path: Path to the barber's CSV file
        output_directory: Directory to save debt reports
        
    Returns:
        Dictionary with processing results
    """
    barber_name = extract_barber_name(file_path)

    try:
        csv_data = read_csv_file(file_path)

        if not csv_data:
            return {'barber': barber_name, 'success': False, 'error': 'Empty file'}

        current_date = datetime.now()
        debt_info = calculate_debt(csv_data, barber_name, current_date)

        write_debt_csv(
            barber_name,
            debt_info['total_days'],
            debt_info['total_debt'],
            output_directory,
            debt_info['debt_periods']
        )

        return {
            'barber': barber_name,
            'success': True,
            'total_days': debt_info['total_days'],
            'total_debt': f"${debt_info['total_debt']:.2f}",
            'debt_periods': debt_info['debt_periods']
        }

    except Exception as e:
        return {'barber': barber_name, 'success': False, 'error': str(e)}


def main():
    """
    Main function to process all barber files.
    
    Workflow:
        1. Find all CSV files in the input directory
        2. Process each file to calculate debt
        3. Write debt reports to debts/ subdirectory
        4. Display summary results
    """
    args = parse_arguments()
    input_directory = Path(args.directory)

    if not input_directory.exists() or not input_directory.is_dir():
        print(f"Error: Directory '{input_directory}' does not exist")
        sys.exit(1)

    output_directory = input_directory / "debts"
    output_directory.mkdir(parents=True, exist_ok=True)

    # Find all barber CSV files (exclude debt files)
    csv_files = [
        entry for entry in input_directory.iterdir()
        if entry.suffix.lower() == '.csv' and not entry.name.endswith('_debt.csv')
    ]

    if not csv_files:
        print(f"No CSV files found in '{args.directory}'")
        sys.exit(0)

    print(f"Found {len(csv_files)} barber CSV files...")
    print("Rate Schedule: 2025 = $7/$5, 2026 = $8/$6 (barbers/Genesis)")
    print("-" * 60)

    successful = 0
    for file_path in csv_files:
        result = process_barber_file(file_path, output_directory)

        if result['success']:
            successful += 1
            print(f"+ {result['barber']}: {result['total_days']} days = {result['total_debt']}")
            for period in result.get('debt_periods', []):
                marker = " [CURRENT]" if period.get('is_current') else " [HISTORICAL]"
                print(f"    {period['from']} -> {period['to']}: {period['days']} days, ${period['debt']:.2f}{marker}")
        else:
            print(f"- {result['barber']}: {result['error']}")

    print("-" * 60)
    print(f"Completed: {successful}/{len(csv_files)} files processed")


if __name__ == "__main__":
    main()