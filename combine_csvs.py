"""combine_csvs.py

Reads all CSV files in `barbers/` and produces `combined.json` in repo root.
The output format will be a JSON object with a `teams` key mapping original names to
an array of records. The original filename is used to recover the name (replacing
underscores back to spaces is attempted but not guaranteed). Files that are empty
are skipped or produce an empty list for that person.
"""
import os
import json
import csv

ROOT = os.path.dirname(__file__)
BARBERS_DIR = os.path.join(ROOT, "barbers")
OUT_FILE = os.path.join(ROOT, "combined.json")


def name_from_filename(filename: str) -> str:
    base = os.path.splitext(filename)[0]
    # reverse simple sanitization: underscores -> spaces
    return base.replace("_", " ")


def main():
    if not os.path.isdir(BARBERS_DIR):
        print(f"Directory not found: {BARBERS_DIR}")
        return

    teams = {}
    for fname in os.listdir(BARBERS_DIR):
        if not fname.lower().endswith('.csv'):
            continue
        path = os.path.join(BARBERS_DIR, fname)
        name = name_from_filename(fname)
        records = []
        with open(path, "r", encoding="utf-8") as f:
            # If file is empty, skip reading
            first = f.read(1)
            if not first:
                teams[name] = []
                continue
            f.seek(0)
            reader = csv.DictReader(f)
            for row in reader:
                # convert empty strings to null for cleanliness
                clean = {k: (v if v != "" else None) for k, v in row.items()} if row else {}
                records.append(clean)
        teams[name] = records
        print(f"Read {len(records)} records from {path}")

    out = {"teams": teams}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote combined JSON to {OUT_FILE}")


if __name__ == "__main__":
    main()
