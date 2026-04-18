import csv
from datetime import datetime, timedelta

def parse_date_dd_mm_yyyy(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y')

def format_date_yyyy_mm_dd(date):
    return date.strftime('%Y-%m-%d')

def is_sunday(date):
    return date.weekday() == 6

def get_next_non_sunday(date):
    next_date = date + timedelta(days=1)
    while is_sunday(next_date):
        next_date += timedelta(days=1)
    return next_date

def process_transaction(date, transaction_number, amount_usd):
    rows = []
    current_date = date
    current_amount = amount_usd
    
    while current_amount > 0:
        if is_sunday(current_date):
            current_date += timedelta(days=1)
            continue
        
        row = {
            'startDate': format_date_yyyy_mm_dd(current_date),
            'endDate': format_date_yyyy_mm_dd(current_date),
            'link': 'Video',
            'Operation': transaction_number,
            'Amount': int(current_amount) if current_amount == int(current_amount) else round(current_amount, 2)
        }
        rows.append(row)
        
        current_date += timedelta(days=1)
        current_amount -= 8
    
    while is_sunday(current_date):
        current_date += timedelta(days=1)
    
    final_row = {
        'startDate': format_date_yyyy_mm_dd(current_date),
        'endDate': format_date_yyyy_mm_dd(current_date),
        'link': '',
        'Operation': '',
        'Amount': int(current_amount) if current_amount == int(current_amount) else round(current_amount, 2)
    }
    rows.append(final_row)
    
    return rows

source_file = r'E:\Projects\Barberia\tomerge\Alejandro.csv'
target_file = r'E:\Projects\Barberia\payment-chart-app\barbers\Alejandro.csv'

existing_rows = []
with open(target_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        existing_rows.append(row)

transactions = []
with open(source_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = parse_date_dd_mm_yyyy(row['date'])
        transaction_number = row['transaction_number']
        amount_usd = float(row['amount_usd'])
        transactions.append({
            'date': date,
            'transaction_number': transaction_number,
            'amount_usd': amount_usd
        })

new_rows = []
for txn in transactions:
    txn_rows = process_transaction(txn['date'], txn['transaction_number'], txn['amount_usd'])
    new_rows.extend(txn_rows)
    print(f"Transaction {txn['transaction_number']} on {format_date_yyyy_mm_dd(txn['date'])}: {len(txn_rows)} rows generated")

all_rows = existing_rows + new_rows

with open(target_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nTotal rows added: {len(new_rows)}")
print(f"Total rows in file: {len(all_rows)}")