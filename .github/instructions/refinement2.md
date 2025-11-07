Follow instructions by reading /.github/instructions/Anotar cuentas.instructions.md and Genesis.md to ensure correct amount decrements ($5 for Genesis and 7$ for someone else) and workflow requirements (image move, Sunday skips, final empty row).
Inspected the existing ledger in barbers/<Name>.csv around the targeted dates to locate where new rows must be inserted.
Examined the provided receipt image on route unorganized\<image name>.jpg to OCR the operation number (visible on the slip, no conversion needed), and noted the payment date range <START DATE NUMBER>–<END DATE NUMBER> plus the USD <AMOUNT> provided.
Relocated the receipt into the backup archive using PowerShell so the CSV’s link column can point to a stable path:
Move-Item -LiteralPath "e:\Projects\Barberia\payment-chart-app\unorganized\<IMAGE NAME>.jpg" -Destination "e:\Projects\Barberia\payment-chart-app\backups\Genesis\<OPERATION NUMBER>.jpg"
Verified the new location with Test-Path "e:\Projects\Barberia\payment-chart-app\backups\<Name>\<OPERATION NUMBER>.jpg", which returned True.
Calculated amounts per instruction: first date keeps the provided $10, second weekday (17 Sept) subtracts $5 → $5, and determined the mandatory follow-up row (18 Sept, even though not in range) should hold previous amount minus $5 → $0 with empty link/operation. Sundays didn’t appear in this window, so no skips were needed.
Updated <NOMBRE>.csv by adding:
2025-09-16,2025-09-16,backups\Genesis\<OPERATION NUMBER>.jpg,<OPERATION NUMBER>,<AMOUNT>
(final instruction-mandated row with blank link/operation).
Re-read the CSV segment to confirm ordering, formatting (YYYY-MM-DD), and amounts, ensuring headers unchanged and commas consistent.