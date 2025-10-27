#!/usr/bin/env python3
"""
Simple CSV -> POST /api/ingest helper.

Usage:
  python load_csv.py path/to/file.csv [--dry-run] [--url http://localhost:8000/api/ingest]

Expects CSV header with columns: poi,date,visitors,cbg,dma,dwell
Date format: YYYY-MM-DD
"""
import csv
import json
import sys
import argparse
from datetime import datetime
from urllib import request, error


def validate_row(r):
    # basic validation and conversion
    try:
        datetime.strptime(r.get("date", ""), "%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Bad date '{r.get('date')}'")
    try:
        r["visitors"] = int(r.get("visitors", 0))
    except Exception:
        raise ValueError(f"Bad visitors '{r.get('visitors')}'")
    # dwell optional float
    if r.get("dwell") is not None and r.get("dwell") != "":
        try:
            r["dwell"] = float(r["dwell"])
        except Exception:
            raise ValueError(f"Bad dwell '{r.get('dwell')}'")
    return r


def load_csv(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for i, r in enumerate(reader):
            # normalize keys to expected names
            row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in r.items()}
            rows.append(row)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument('csv')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--url', default='http://localhost:8000/api/ingest')
    args = p.parse_args()

    rows = load_csv(args.csv)
    validated = []
    errors = []
    for r in rows:
        try:
            validated.append(validate_row(r))
        except Exception as e:
            errors.append((r, str(e)))

    print(f"Read {len(rows)} rows, {len(validated)} valid, {len(errors)} errors")
    if errors:
        for r, e in errors[:5]:
            print("Error:", e, "row:", r)

    if args.dry_run:
        print(json.dumps(validated[:10], indent=2, ensure_ascii=False))
        return

    data = json.dumps(validated).encode('utf-8')
    req = request.Request(args.url, data=data, headers={
        'Content-Type': 'application/json'
    }, method='POST')
    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            print('Response:', body)
    except error.HTTPError as e:
        print('HTTP Error:', e.code, e.reason)
        print(e.read().decode('utf-8'))
        sys.exit(1)
    except Exception as e:
        print('Error sending request:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
