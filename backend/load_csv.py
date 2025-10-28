#!/usr/bin/env python3
"""
Load the Bigbox Stores Metrics CSV into the backend SQLite database used by the app.

Usage:
  python load_csv.py [--csv PATH] [--db PATH] [--dry-run] [--clear]

Defaults:
  csv: ../Bigbox Stores Metrics.csv  (relative to backend/)
  db:  src/data.db

This script inserts rows into the `venues` table. If --clear is provided the table
will be truncated before inserting.
"""
import csv
import argparse
import sqlite3
import os
import sys


FIELD_ORDER = [
    'entity_id','entity_type','name','foot_traffic','sales','avg_dwell_time_min','area_sqft','ft_per_sqft',
    'geolocation','country','state_code','state_name','city','postal_code','formatted_city','street_address',
    'sub_category','dma','cbsa','chain_id','chain_name','store_id','date_opened','date_closed'
]


def parse_int(v):
    if v is None or v == '':
        return None
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return None


def parse_float(v):
    if v is None or v == '':
        return None
    try:
        return float(v)
    except Exception:
        return None


def normalize_row(r):
    # normalize keys to lower/strip and map to FIELD_ORDER names
    row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
    out = []
    for key in FIELD_ORDER:
        val = row.get(key, '')
        # numeric conversions for known fields
        if key in ('foot_traffic',):
            out.append(parse_int(val))
        elif key in ('sales','avg_dwell_time_min','area_sqft','ft_per_sqft'):
            out.append(parse_float(val))
        else:
            out.append(val if val != '' else None)
    return out


def ensure_table(conn):
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT,
        entity_type TEXT,
        name TEXT,
        foot_traffic INTEGER,
        sales REAL,
        avg_dwell_time_min REAL,
        area_sqft REAL,
        ft_per_sqft REAL,
        geolocation TEXT,
        country TEXT,
        state_code TEXT,
        state_name TEXT,
        city TEXT,
        postal_code TEXT,
        formatted_city TEXT,
        street_address TEXT,
        sub_category TEXT,
        dma TEXT,
        cbsa TEXT,
        chain_id TEXT,
        chain_name TEXT,
        store_id TEXT,
        date_opened TEXT,
        date_closed TEXT
    );''')
    conn.commit()


def load_into_db(csv_path, db_path, dry_run=False, clear=False):
    if not os.path.exists(csv_path):
        print('CSV not found:', csv_path)
        return 1

    conn = sqlite3.connect(db_path)
    ensure_table(conn)
    cur = conn.cursor()

    if clear:
        cur.execute('DELETE FROM venues;')
        conn.commit()

    to_insert = []
    errors = []
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for i, r in enumerate(reader, start=1):
            try:
                row = normalize_row(r)
                to_insert.append(row)
            except Exception as e:
                errors.append((i, r, str(e)))

    print(f'Read {len(to_insert)} rows, {len(errors)} errors')
    if errors:
        for e in errors[:5]:
            print('Err row', e[0], e[2])

    if dry_run:
        # show sample
        import json
        print(json.dumps([dict(zip(FIELD_ORDER, r)) for r in to_insert[:10]], indent=2, ensure_ascii=False))
        return 0

    placeholders = ','.join('?' for _ in FIELD_ORDER)
    sql = f'INSERT INTO venues ({",".join(FIELD_ORDER)}) VALUES ({placeholders})'
    cur.executemany(sql, to_insert)
    conn.commit()
    conn.close()
    print('Inserted', len(to_insert), 'rows into', db_path)
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', default=os.path.join(os.path.dirname(__file__), '..', 'Bigbox Stores Metrics.csv'))
    p.add_argument('--db', default=os.path.join(os.path.dirname(__file__), 'src', 'data.db'))
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--clear', action='store_true', help='Clear venues table before inserting')
    args = p.parse_args()

    csv_path = os.path.abspath(args.csv)
    db_path = os.path.abspath(args.db)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    rc = load_into_db(csv_path, db_path, dry_run=args.dry_run, clear=args.clear)
    if rc != 0:
        sys.exit(rc)


if __name__ == '__main__':
    main()
