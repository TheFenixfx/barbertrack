import csv

input_file = r'E:\Projects\Barberia\payment-chart-app\consolidatedPayments_with_dollar.csv'
output_file = r'E:\Projects\Barberia\payment-chart-app\consolidatedPayments_with_dollar.csv'

rows = []
with open(input_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    # Add new column after dollar_price
    new_fieldnames = list(fieldnames)
    dollar_price_idx = new_fieldnames.index('dollar_price')
    new_fieldnames.insert(dollar_price_idx + 1, 'amount_usd')
    
    for row in reader:
        amount = float(row['amount'])
        dollar_price = float(row['dollar_price'])
        amount_usd = round(amount / dollar_price, 2)
        row['amount_usd'] = amount_usd
        rows.append(row)

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=new_fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done! Processed {len(rows)} rows.")
print(f"Output saved to: {output_file}")