"""generate_csvs.py

Reads `data.json` in the repository root and writes one CSV per team member
into a folder named `barbers/`. Each CSV filename is the member name (sanitized)
and contains rows for each record (startDate, endDate, link).
"""
import os
import json
import csv
import re

ROOT = os.path.dirname(__file__)
DATA_FILE = os.path.join(ROOT, "data.json")
OUT_DIR = os.path.join(ROOT, "barbers")

ILLEGAL_RE = re.compile(r'[<>:"/\\|?*]')
TRAILING_DOTS_SPACES_RE = re.compile(r'[\.\s]+$')

def sanitize_filename(name: str) -> str:
    # Keep the name visually similar but remove characters that are illegal on Windows
    if not name:
        return "unnamed"
    s = ILLEGAL_RE.sub("_", name)
    s = TRAILING_DOTS_SPACES_RE.sub("", s)
    # If filename becomes empty, fallback
    return s or "unnamed"


def main():
    if not os.path.exists(DATA_FILE):
        print(f"data.json not found at {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("teams", {})
    os.makedirs(OUT_DIR, exist_ok=True)

    written = 0
    for name, records in teams.items():
        filename = sanitize_filename(name) + ".csv"
        path = os.path.join(OUT_DIR, filename)
        # Determine fieldnames from all records, preserving a sensible order when possible
        if records and isinstance(records, list):
            # prefer common known fields order
            preferred = ["startDate", "endDate", "link"]
            keys = []
            for r in records:
                for k in r.keys():
                    if k not in keys:
                        keys.append(k)
            # Merge preferred with discovered keys
            fieldnames = [k for k in preferred if k in keys] + [k for k in keys if k not in preferred]
        else:
            fieldnames = []

        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            if fieldnames:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for rec in records:
                    # Ensure only stringifiable values are written
                    row = {k: (rec.get(k, "") if rec.get(k, None) is not None else "") for k in fieldnames}
                    writer.writerow(row)
            else:
                # Write an empty file for members with no records
                csvfile.write("")
        written += 1
        print(f"Wrote {path} ({len(records)} rows)")

    print(f"Done. Wrote {written} files to {OUT_DIR}")


if __name__ == "__main__":
    main()
