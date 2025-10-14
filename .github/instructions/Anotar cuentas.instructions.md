# Anotar cuentas - Instructions

Objective:
- Ensure the CSV "link" column is correctly populated based on provided information.
- Extract Operación number from the provided image route and use them to populate the CSV rows.
- Use the amount provided by the user in USD directly.
- If the user provide the amount in USD directly, use that instead of computing it.
- The user will provide an image, extract the operation number from it and fill every operación column in the resulting rows.
- Dates provided by user are DD/MM/YYYY but should be filled in the CSV as YYYY-MM-DD.

Step-by-step workflow:
1. Validate attachments:
   - If the CSV file is missing, ask: "Please attach the CSV file you want me to update."
   - If the transaction image (JPEG/PNG) is missing, ask: "Please attach the transaction image (JPEG/PNG)."
2. Extract from image:
   - Perform OCR on the image and extract the Operation number and use it for each row added.
   - Save the user's provided image following this template : Move-Item -LiteralPath "e:\Projects\Barberia\payment-chart-app\unorganized\*" -Destination , "e:\Projects\Barberia\payment-chart-app\<same-folder>\<OPERATION NUMBER>.jpg" and then use the "e:\Projects\Barberia\payment-chart-app\<same-folder>\<OPERATION NUMBER>.jpg" string in the CSV link column.
   - Use the only image in "e:\Projects\Barberia\payment-chart-app\unorganized\*"
   - Use the Destination path to add it to the link column for each date.
3. Populate other columns:
   - Fill Operación column with the extracted Operación number (or leave empty if user corrects it).
   - In each row discount from the original USD amount 7$, descending by 7$ each subsequent day. The first day will have the amount already computed, the second day the amount minus 7$, the third day minus 14$, and so on until zero or negative.
   - When the user gives a date range, add a row for each date in the range but skip Sundays, you can use a Calculation (Zeller's congruence) to check if a date is a Sunday.
4. Deliver output:


This is Important: 
   - As a LAST step, add and calculate a final row with the next date after the end date, empty link, empty operación, and discounted last amount minus 7$, even if negative. Example : 
    next date, next date, empty link, empty operación, ( last amount - 7$ )

Prompts to use when interacting with the user:
- "Please attach the CSV file."
- "What rate change (divisor) should I use to convert the Amount?"
- "Do you want a single date or a date range? If a range, provide start and end dates (DD/MM/YYYY)."

Notes and parsing details:
- Amounts are in USD.
- Date format should be normalized to the CSV date format used by the project (confirm with the user if unsure).
- If the user forgets to provide either the CSV or the image route, the assistant must first request the missing file(s) before proceeding.
- Ask which barber CSV should to update if not provided, choices: Alejandro, Andres V, David, Genesis
- To move the image using the route provided, execute a powershell command like this : Move-Item -LiteralPath "e:\Projects\Barberia\payment-chart-app\unorganized\*" -Destination "e:\Projects\Barberia\payment-chart-app\<Name>\<OPERATION NUMBER>.jpg"
- Ensure the image is moved