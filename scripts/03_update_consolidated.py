import csv
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

input_file = r'E:\Projects\Barberia\payment-chart-app\consolidatedPayments.csv'
output_file = r'E:\Projects\Barberia\payment-chart-app\consolidatedPayments_with_dollar.csv'

rows = []
with open(input_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames) + ['dollar_price', 'amount_usd']
    
    for row in reader:
        date = parse_date(row['date'])
        dollar_price = get_nearest_dollar_price(date)
        amount = float(row['amount'])
        amount_usd = round(amount / dollar_price, 2)
        
        row['dollar_price'] = dollar_price
        row['amount_usd'] = amount_usd
        rows.append(row)

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done! Processed {len(rows)} rows.")
print(f"Output saved to: {output_file}")