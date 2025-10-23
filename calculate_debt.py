#!/usr/bin/env python3
"""
Barber Debt Calculator

This script processes barber CSV files to calculate debt from the last payment date.
It counts days from the last payment to current date, excluding Sundays, and calculates
debt at $7 per day.

Usage:
    python calculate_debt.py [directory]

If no directory is provided, it defaults to the 'barbers' directory.
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate barber debt from CSV payment files"
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
        file_path (str): Path to the CSV file

    Returns:
        list: List of dictionaries containing CSV data

    Raises:
        FileNotFoundError: If the file doesn't exist
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


def get_latest_payment_date(csv_data):
    """
    Find the latest endDate from CSV data.

    Args:
        csv_data (list): List of dictionaries containing CSV data

    Returns:
        datetime: Latest payment date or None if no valid dates found
    """
    latest_date = None

    for row in csv_data:
        end_date_str = row.get('endDate', '').strip()
        if not end_date_str:
            continue

        try:
            # Parse date in YYYY-MM-DD format
            current_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            if latest_date is None or current_date > latest_date:
                latest_date = current_date
        except ValueError:
            # Skip invalid date formats
            continue

    return latest_date


def count_excluding_sundays(start_date, end_date):
    """
    Count days between two dates, excluding Sundays.

    Args:
        start_date (datetime): Start date
        end_date (datetime): End date

    Returns:
        int: Number of days excluding Sundays
    """
    if start_date >= end_date:
        return 0

    days_count = 0
    current_date = start_date + timedelta(days=1)  # Start from day after last payment

    while current_date <= end_date:
        if current_date.weekday() != 6:  # 6 = Sunday
            days_count += 1
        current_date += timedelta(days=1)

    return days_count


def calculate_debt(days_passed, daily_rate=7.0):
    """
    Calculate debt amount based on days passed.

    Args:
        days_passed (int): Number of days passed
        daily_rate (float): Daily rate (default: $7)

    Returns:
        float: Total debt amount
    """
    return days_passed * daily_rate


def extract_barber_name(file_path):
    """
    Extract barber name from file path.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        str: Barber name (filename without extension)
    """
    return Path(file_path).stem


def write_debt_csv(barber_name, days_passed, debt_amount, output_directory):
    """
    Write debt information to a CSV file.

    Args:
        barber_name (str): Name of the barber
        days_passed (int): Number of days passed
        debt_amount (float): Total debt amount
        output_directory (str): Directory to save the output file
    """
    output_filename = f"{barber_name}_debt.csv"
    output_path = os.path.join(output_directory, output_filename)

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['days_passed', 'debt_amount'])
            writer.writerow([days_passed, f"{debt_amount:.2f}"])

        print(f"Created debt report: {output_path}")
        return output_path
    except Exception as e:
        raise Exception(f"Error writing debt CSV file {output_path}: {str(e)}")


def process_barber_file(file_path, output_directory):
    """
    Process a single barber CSV file and generate debt report.

    Args:
        file_path (str): Path to the barber CSV file
        output_directory (str): Directory to save the output file

    Returns:
        dict: Processing results
    """
    barber_name = extract_barber_name(file_path)

    try:
        # Read CSV data
        csv_data = read_csv_file(file_path)

        if not csv_data:
            print(f"Warning: {file_path} is empty or has no data")
            return {
                'barber': barber_name,
                'success': False,
                'error': 'Empty file'
            }

        # Get latest payment date
        latest_date = get_latest_payment_date(csv_data)

        if latest_date is None:
            print(f"Warning: No valid dates found in {file_path}")
            return {
                'barber': barber_name,
                'success': False,
                'error': 'No valid dates'
            }

        # Calculate days passed (excluding Sundays)
        current_date = datetime.now()
        days_passed = count_excluding_sundays(latest_date, current_date)

        # Determine daily rate (Genesis discounts $5 per day)
        daily_rate = 5.0 if barber_name == "Genesis" else 7.0

        # Calculate debt
        debt_amount = calculate_debt(days_passed, daily_rate)

        # Write debt report
        write_debt_csv(barber_name, days_passed, debt_amount, output_directory)

        return {
            'barber': barber_name,
            'success': True,
            'latest_payment': latest_date.strftime('%Y-%m-%d'),
            'days_passed': days_passed,
            'debt_amount': f"${debt_amount:.2f}"
        }

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return {
            'barber': barber_name,
            'success': False,
            'error': str(e)
        }


def main():
    """Main function to process all barber files."""
    args = parse_arguments()

    # Validate input directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)

    # Use same directory for output files
    output_directory = args.directory

    # Find all CSV files in the directory
    csv_files = []
    for file in os.listdir(args.directory):
        if file.endswith('.csv') and not file.endswith('_debt.csv'):
            csv_files.append(os.path.join(args.directory, file))

    if not csv_files:
        print(f"No CSV files found in directory '{args.directory}'")
        sys.exit(0)

    print(f"Found {len(csv_files)} barber CSV files to process...")
    print("-" * 50)

    # Process each file
    results = []
    successful_processes = 0

    for file_path in csv_files:
        result = process_barber_file(file_path, output_directory)
        results.append(result)

        if result['success']:
            successful_processes += 1
            print(f"+ {result['barber']}: {result['days_passed']} days, {result['debt_amount']} debt")
        else:
            print(f"- {result['barber']}: {result['error']}")

    # Print summary
    print("-" * 50)
    print(f"Processing complete: {successful_processes}/{len(csv_files)} files processed successfully")

    if successful_processes == 0:
        print("No files were processed successfully.")
        sys.exit(1)


if __name__ == "__main__":
    main()