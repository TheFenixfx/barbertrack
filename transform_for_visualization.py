#!/usr/bin/env python3
"""
Transform Payment Data for Visualization - Daily Block Format

This script reads data.json and transforms it into a visualization-ready format
compatible with the existing web page. It generates one block per working day
(excluding Sundays), with each day's block pointing to the most recent payment.

This creates a continuous stacked column where every working day has a block,
eliminating visual gaps. Days without their own payment inherit data from the
last payment date.

Usage:
    python transform_for_visualization.py

Output:
    visualization_data.json - transformed data for the web page
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data.json"
OUTPUT_FILE = ROOT / "visualization_data.json"


def is_sunday(date):
    """Check if a date is a Sunday (weekday 6)."""
    return date.weekday() == 6


def parse_date(date_string):
    """Parse a date string into a datetime object."""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return None


def get_payment_data_by_date(payments):
    """
    Build a dictionary mapping each payment endDate to its data.
    """
    payment_map = {}
    for payment in payments:
        end_date = parse_date(payment.get('endDate'))
        if end_date:
            # Store the most complete data for this date
            if end_date not in payment_map or payment.get('Amount'):
                payment_map[end_date] = payment
    return payment_map


def get_sorted_payment_dates(payments):
    """
    Get sorted list of unique payment end dates.
    """
    dates = set()
    for payment in payments:
        end_date = parse_date(payment.get('endDate'))
        if end_date and not is_sunday(end_date):
            dates.add(end_date)
    return sorted(dates)


def find_last_payment_data(target_date, sorted_dates, payment_map):
    """
    Find the most recent payment date and its data for a target date.
    """
    last_payment_date = None
    for payment_date in sorted_dates:
        if payment_date <= target_date:
            last_payment_date = payment_date
        else:
            break
    
    if last_payment_date:
        return last_payment_date, payment_map.get(last_payment_date)
    return None, None


def transform_barber_payments(payments, global_start, global_end):
    """
    Transform a barber's payments into daily blocks.
    
    Creates one entry per working day, each pointing to the last payment.
    
    Args:
        payments: List of payment entries for a barber
        global_start: The minimum date to start from
        global_end: The maximum date to end at
    
    Returns:
        List of transformed daily entries
    """
    if not payments:
        return []
    
    payment_map = get_payment_data_by_date(payments)
    sorted_dates = get_sorted_payment_dates(payments)
    
    if not sorted_dates:
        return []
    
    # Start from barber's first payment date
    barber_start = sorted_dates[0]
    barber_end = sorted_dates[-1]
    
    # Clip to global range
    timeline_start = max(global_start, barber_start)
    timeline_end = min(global_end, barber_end)
    
    transformed = []
    current_date = timeline_start
    
    while current_date <= timeline_end:
        # Skip Sundays
        if is_sunday(current_date):
            current_date += timedelta(days=1)
            continue
        
        # Find last payment for this date
        last_payment_date, last_payment_data = find_last_payment_data(
            current_date, sorted_dates, payment_map
        )
        
        if last_payment_date:
            # Is this day itself a payment day?
            is_payment_day = (current_date == last_payment_date)
            
            entry = {
                'startDate': current_date.strftime('%Y-%m-%d'),
                'endDate': current_date.strftime('%Y-%m-%d'),
                'link': last_payment_data.get('link') if last_payment_data else None,
                'Operation': last_payment_data.get('Operation') if last_payment_data else None,
                'Amount': last_payment_data.get('Amount') if last_payment_data else '0',
                'isPaymentDay': is_payment_day,
                'lastPaymentDate': last_payment_date.strftime('%Y-%m-%d')
            }
            transformed.append(entry)
        
        current_date += timedelta(days=1)
    
    return transformed


def calculate_global_date_range(teams_data):
    """
    Calculate the global date range from all barber data.
    Returns (start_date, end_date) as datetime objects.
    """
    all_dates = []
    
    for payments in teams_data.values():
        for payment in payments:
            start = parse_date(payment.get('startDate'))
            end = parse_date(payment.get('endDate'))
            if start:
                all_dates.append(start)
            if end:
                all_dates.append(end)
    
    if not all_dates:
        return None, None
    
    return min(all_dates), max(all_dates)


def transform_data():
    """
    Main transformation function.
    Reads data.json and produces visualization_data.json.
    """
    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} not found")
        return False
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    teams = data.get('teams', {})
    
    if not teams:
        print("Error: No teams data found")
        return False
    
    # Calculate global date range
    global_start, global_end = calculate_global_date_range(teams)
    
    if not global_start or not global_end:
        print("Error: Could not determine date range")
        return False
    
    print(f"Global date range: {global_start.strftime('%Y-%m-%d')} to {global_end.strftime('%Y-%m-%d')}")
    
    # Transform each barber's data
    transformed_teams = {}
    
    for barber_name, payments in teams.items():
        print(f"Processing {barber_name}: {len(payments)} original entries")
        
        transformed_payments = transform_barber_payments(
            payments, global_start, global_end
        )
        
        transformed_teams[barber_name] = transformed_payments
        print(f"  -> Generated {len(transformed_payments)} daily blocks")
    
    # Build output structure (same format as original data.json)
    output = {
        'teams': transformed_teams
    }
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nTransformed data written to {OUTPUT_FILE}")
    return True


if __name__ == "__main__":
    transform_data()