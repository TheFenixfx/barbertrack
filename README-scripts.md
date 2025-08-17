This small helper provides two scripts to convert `data.json` into per-person CSVs
and then combine all CSVs back into a single JSON.

Usage (Windows PowerShell):

- Generate CSV files into `barbers/`:
  python .\generate_csvs.py

- Combine CSV files into `combined.json`:
  python .\combine_csvs.py

Files created:
- `barbers/` - directory with one CSV per team member.
- `combined.json` - merged JSON with structure {"teams": {name: [records...]}}
