import csv
import os
from datetime import datetime

from datetime import datetime

dollar_prices = {
    datetime(2025, 12, 28): 294.96,
    datetime(2025, 12, 30): 298.14,
    datetime(2026, 1, 2): 301.37,
    datetime(2026, 1, 13): 330.37,
    datetime(2026, 1, 27): 358.00,
    datetime(2026, 2, 27): 417.35,
    datetime(2026, 3, 2): 419.98,
    datetime(2026, 3, 3): 421.87,
    datetime(2026, 3, 4): 425.67,
    datetime(2026, 3, 5): 427.93,
    # --- Actualización Marzo / Abril 2026 ---
    datetime(2026, 3, 15): 442.10, # Promedio quincenal
    datetime(2026, 3, 29): 471.11, # Mínimo de cierre de mes
    datetime(2026, 3, 31): 473.87, # Cierre de marzo
    datetime(2026, 4, 1): 473.91,  # Apertura de abril
    datetime(2026, 4, 2): 474.05,  # Tasa oficial BCV
    datetime(2026, 4, 3): 474.06,  # Último cierre registrado
    datetime(2026, 4, 5): 474.06,  # Tasa vigente (Hoy)
}

def parse_date(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y')

def get_nearest_dollar_price(date):
    if date in dollar_prices:
        return dollar_prices[date]
    
    sorted_dates = sorted(dollar_prices.keys())
    
    if date < sorted_dates[0]:
        return dollar_prices[sorted_dates[0]]
    
    if date > sorted_dates[-1]:
        return dollar_prices[sorted_dates[-1]]
    
    for i in range(len(sorted_dates) - 1):
        if sorted_dates[i] <= date <= sorted_dates[i + 1]:
            diff_before = abs((date - sorted_dates[i]).days)
            diff_after = abs((sorted_dates[i + 1] - date).days)
            if diff_before <= diff_after:
                return dollar_prices[sorted_dates[i]]
            else:
                return dollar_prices[sorted_dates[i + 1]]
    
    return dollar_prices[sorted_dates[-1]]

def process_barber_file(filepath):
    rows = []
    
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_fields = ['date', 'concept', 'transaction_number', 'bank', 'amount', 'barber_name']
        new_fieldnames = original_fields + ['dollar_price', 'amount_usd']
        
        for row in reader:
            clean_row = {k: row[k] for k in original_fields if k in row}
            
            date = parse_date(clean_row['date'])
            dollar_price = get_nearest_dollar_price(date)
            amount = float(clean_row['amount'])
            amount_usd = round(amount / dollar_price, 2)
            
            clean_row['dollar_price'] = dollar_price
            clean_row['amount_usd'] = amount_usd
            rows.append(clean_row)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return len(rows)

barber_dir = r'E:\Projects\Barberia\tomerge'
barber_files = ['Alejandro.csv', 'Andres.csv', 'David.csv', 'Genesis.csv']

print("Updating barber files with dollar prices and USD amounts...\n")

for filename in barber_files:
    filepath = os.path.join(barber_dir, filename)
    if os.path.exists(filepath):
        rows_processed = process_barber_file(filepath)
        print(f"[OK] {filename}: {rows_processed} rows processed")
    else:
        print(f"[X] {filename}: File not found")

print("\nDone!")