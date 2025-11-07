Follow these steps in order to ensure accurate CSV population, image handling, and amount calculations.

Step 1: Validate Required Inputs
Check for CSV file: Ensure the user has attached the CSV file to update. If missing, prompt: "Please attach the CSV file you want me to update."
Check for transaction image: Ensure the user has attached a JPEG/PNG image of the transaction. If missing, prompt: "Please attach the transaction image (JPEG/PNG)."
Confirm barber selection: If not specified, ask which barber CSV to update. Options: Alejandro, Andres V, David, Genesis.
Confirm date input: Pick a provided single date or a date range. If a range, request start and end dates in DD/MM/YYYY format.
Confirm amount: If not provided directly in USD, ask: "What rate change (divisor) should I use to convert the Amount?" (Note: Assume USD input from the user.)
Step 2: Extract Data from the Transaction Image
Perform OCR: Use OCR on the attached image to extract the Operation number.
Mocve the image:
Locate the image in e:\Projects\Barberia\payment-chart-app\unorganized\*.
Move it to the appropriate barber folder using the extracted Operation number as the filename (e.g., <OPERATION NUMBER>.jpg).
Use PowerShell command: Move-Item -LiteralPath "e:\Projects\Barberia\payment-chart-app\unorganized\*" -Destination "e:\Projects\Barberia\payment-chart-app\<BarberName>\<OPERATION NUMBER>.jpg".
Ensure the move is successful before proceeding.
Prepare link column: Use the new image path (e.g., e:\Projects\Barberia\payment-chart-app\<BarberName>\<OPERATION NUMBER>.jpg) for the "link" column in each added row.
Step 3: Populate CSV Columns for Each Date
Fill Operación column: Use the extracted Operation number for every row added. (Leave empty if the user provides a correction.)
Handle dates:
Convert user-provided dates from DD/MM/YYYY to YYYY-MM-DD for CSV.
For date ranges: Add a row for each date in the range, but skip Sundays (use Zeller's congruence to check day of week).
Calculate amounts:
Start with the user-provided USD amount for the first date.
For each subsequent day, discount 7 USD (e.g., Day 1: full amount, Day 2: amount - 7, Day 3: amount - 14, etc., until zero or negative).
Amounts are always in USD; do not convert unless specified.
Step 4: Add Final Summary Row
Add extra row: After the last date in the range, add one more row with:
Date: Next day after the end date (in YYYY-MM-DD format).
Link: Empty.
Operación: Empty.
Amount: Last discounted amount minus 7 USD (even if negative).
Step 5: Deliver and Validate Output
Output the updated CSV: Provide the modified CSV with all new rows added.
Verify: Ensure dates are in YYYY-MM-DD, amounts are discounted correctly, links point to moved images, and Sundays are skipped in ranges.
Handle errors: If OCR fails or amounts go negative unexpectedly, notify the user and request clarification.
Additional Notes
Date normalization: Always confirm CSV date format with the user if unsure.
Image handling: Only one image should be in unorganized; process it immediately after extraction.
User prompts: Use the specified prompts exactly when requesting missing information.
Dependencies: Ensure PowerShell is available for image moves; validate file paths before execution.
