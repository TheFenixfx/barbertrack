#!/usr/bin/env python3
"""
Barber Debt Calculator - Current Year (2026)

Purpose:
    Calculate accumulated debt for each barber ONLY for the current year (2026).
    
    This script filters debt periods to only include days from January 1, 2026
    onwards, providing a year-specific debt report.
    
    Debt occurs when a barber's prepaid balance runs out (Amount=0) and they
    continue working without making a new payment. The script identifies:
    
    1. Explicit debt days: Entries where Amount=0 and no Operation (payment)
    2. Gap debt days: Missing days between when balance ran out and next payment
    
    Days with positive Amount (remaining balance) are NOT counted as debt,
    even if there are gaps in the data - the prepaid balance covers those days.

Rate Schedule for 2026:
    - $8/day for barbers (Alejandro, Andres, David)
    - $6/day for Genesis
    
    Sundays are always excluded from debt calculations.

Data Format:
    Each CSV entry contains:
    - endDate: The date of the entry (YYYY-MM-DD)
    - Amount: Remaining prepaid balance for that day
    - Operation: Payment reference code (null/empty if no payment)
    
    When a payment is made, Amount starts high and decreases each day:
    Example: $42 → $35 → $28 → $21 → $14 → $7 → $0 (each day subtracts rate)
    
    When Amount reaches 0, debt begins accumulating until a new payment.

Output:
    Creates _debt_2026.csv files in barbers/debts/ directory for each barber,
    containing total debt days and amount for 2026 only.

Usage:
    python calculate_debt_2026.py [directory]
    
    If no directory provided, defaults to 'barbers' directory.

Author: Barberia Payment System
Date: 2026-04-11
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Current year for filtering
CURRENT_YEAR = 2026
YEAR_START = datetime(CURRENT_YEAR, 1, 1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"Calculate barber debt for year {CURRENT_YEAR}"
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
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: For other CSV reading errors
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


def get_daily_rate(barber_name):
    """
    Get daily debt rate for the current year (2026).
    
    Rates for 2026:
        - $8/day for barbers (Alejandro, Andres, David)
        - $6/day for Genesis
    
    Args:
        barber_name: Name of the barber
        
    Returns:
        Daily rate as float
    """
    is_genesis = barber_name.lower() == 'genesis'
    return 6.0 if is_genesis else 8.0


def is_debt_day(amount, operation):
    """
    Check if an entry represents a debt day.
    
    A debt day occurs when:
    - Amount is 0 or None (no prepaid balance)
    - Operation is empty/null (no payment made)
    
    Args:
        amount: The Amount value (parsed float or None)
        operation: The Operation value (payment reference)
        
    Returns:
        True if this is a debt day, False otherwise
    """
    # Invalid/null operation codes that indicate no real payment
    null_operations = ['null', 'None', '000000', '00000000', '000000000000', '']
    
    if operation is None or not str(operation).strip() or str(operation).strip() in null_operations:
        return amount == 0 or amount is None
    return False


def is_real_payment(amount, operation):
    """
    Check if an entry represents a real payment.
    
    A real payment has:
    - Amount > 0 (positive balance)
    - Valid Operation code (payment reference)
    
    Args:
        amount: The Amount value (parsed float or None)
        operation: The Operation value (payment reference)
        
    Returns:
        True if this is a real payment, False otherwise
    """
    # Invalid/null operation codes
    null_operations = ['null', 'None', '000000', '00000000', '000000000000', '']
    
    if amount and amount > 0:
        if operation and str(operation).strip() and str(operation).strip() not in null_operations:
            return True
    return False


def count_debt_days_in_range(start_date, end_date, barber_name):
    """
    Count debt days within a date range for the current year.
    
    Only counts days that fall within 2026 (Jan 1 onwards).
    Sundays are excluded.
    
    Args:
        start_date: Start of the range (datetime)
        end_date: End of the range (datetime)
        barber_name: Name of the barber
        
    Returns:
        Tuple of (days_count, debt_amount)
    """
    # Only count days in current year
    effective_start = max(start_date, YEAR_START)
    effective_end = end_date
    
    if effective_start > effective_end:
        return 0, 0.0
    
    days_count = 0
    debt_amount = 0.0
    rate = get_daily_rate(barber_name)
    
    temp = effective_start
    while temp <= effective_end:
        if not is_sunday(temp):
            days_count += 1
            debt_amount += rate
        temp += timedelta(days=1)
    
    return days_count, debt_amount


def calculate_debt_2026(csv_data, barber_name, current_date):
    """
    Calculate total debt for a barber for year 2026 only.
    
    Debt Logic:
        1. Find first real payment (to skip early placeholder entries)
        2. Track when balance runs out (Amount=0 with no Operation)
        3. Count explicit debt days and gap days until next payment
        4. Only include days from January 1, 2026 onwards
        
    Args:
        csv_data: List of CSV row dictionaries
        barber_name: Name of the barber
        current_date: datetime for today (to calculate current debt)
        
    Returns:
        Dictionary with:
        - total_days: Total debt days in 2026
        - total_debt: Total debt amount in 2026
        - debt_periods: List of debt period details (filtered to 2026)
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
    
    # Find first real payment
    first_payment_idx = None
    for i, e in enumerate(entries):
        if is_real_payment(e['amount'], e['operation']):
            first_payment_idx = i
            break
    
    if first_payment_idx is None:
        return {'total_days': 0, 'total_debt': 0.0, 'debt_periods': []}
    
    total_debt = 0.0
    total_days = 0
    debt_periods = []
    
    # Track debt periods
    in_debt = False
    
    for i in range(first_payment_idx, len(entries)):
        e = entries[i]
        date = e['date']
        amount = e['amount']
        operation = e['operation']
        
        # Check if this is a debt day
        if is_debt_day(amount, operation):
            if not in_debt:
                in_debt = True
            
            # Count this explicit debt day if in 2026 and not Sunday
            if date.year == CURRENT_YEAR and not is_sunday(date):
                rate = get_daily_rate(barber_name)
                total_debt += rate
                total_days += 1
        
        elif is_real_payment(amount, operation):
            # Real payment found
            if in_debt:
                # Count gap days from last entry to this payment
                prev_entry_date = entries[i - 1]['date'] if i > 0 else None
                
                if prev_entry_date and prev_entry_date < date:
                    gap_start = prev_entry_date + timedelta(days=1)
                    gap_end = date - timedelta(days=1)
                    
                    # Only count days in 2026
                    days, debt = count_debt_days_in_range(gap_start, gap_end, barber_name)
                    
                    if days > 0:
                        total_debt += debt
                        total_days += days
                        # Record period (show effective dates in 2026)
                        effective_start = max(gap_start, YEAR_START)
                        debt_periods.append({
                            'from': effective_start.strftime('%Y-%m-%d'),
                            'to': gap_end.strftime('%Y-%m-%d'),
                            'days': days,
                            'debt': debt
                        })
                
                in_debt = False
    
    # If still in debt at end, count gap to today
    if in_debt:
        last_entry_date = entries[-1]['date']
        gap_start = last_entry_date + timedelta(days=1)
        gap_end = current_date
        
        # Only count days in 2026
        days, debt = count_debt_days_in_range(gap_start, gap_end, barber_name)
        
        if days > 0:
            total_debt += debt
            total_days += days
            effective_start = max(gap_start, YEAR_START)
            debt_periods.append({
                'from': effective_start.strftime('%Y-%m-%d'),
                'to': gap_end.strftime('%Y-%m-%d'),
                'days': days,
                'debt': debt,
                'is_current': True
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
    output_filename = f"{barber_name}_debt_{CURRENT_YEAR}.csv"
    output_path = output_directory / output_filename

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['days_passed', 'debt_amount'])
            writer.writerow([total_days, f"{total_debt:.2f}"])
            
            if debt_periods:
                writer.writerow([])
                writer.writerow(['from', 'to', 'days', 'debt', 'is_current'])
                for period in debt_periods:
                    is_current = 'yes' if period.get('is_current') else ''
                    writer.writerow([
                        period['from'],
                        period['to'],
                        period['days'],
                        f"{period['debt']:.2f}",
                        is_current
                    ])

        print(f"Created debt report: {output_path}")
        return output_path
    except Exception as e:
        raise Exception(f"Error writing debt CSV file {output_path}: {str(e)}")


def process_barber_file(file_path, output_directory):
    """
    Process a single barber CSV file and generate 2026 debt report.
    
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
        debt_info = calculate_debt_2026(csv_data, barber_name, current_date)

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
    Main function to process all barber files for 2026.
    
    Workflow:
        1. Find all CSV files in the input directory
        2. Process each file to calculate 2026 debt only
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
    print(f"Calculating debt for year {CURRENT_YEAR} only")
    print(f"Rate Schedule: $8/day for barbers, $6/day for Genesis")
    print("-" * 50)

    successful = 0
    for file_path in csv_files:
        result = process_barber_file(file_path, output_directory)

        if result['success']:
            successful += 1
            print(f"+ {result['barber']}: {result['total_days']} days = {result['total_debt']}")
            for period in result.get('debt_periods', []):
                marker = " [CURRENT]" if period.get('is_current') else ""
                print(f"    {period['from']} -> {period['to']}: {period['days']} days, ${period['debt']:.2f}{marker}")
        else:
            print(f"- {result['barber']}: {result['error']}")

    print("-" * 50)
    print(f"Completed: {successful}/{len(csv_files)} files processed")


if __name__ == "__main__":
    main()