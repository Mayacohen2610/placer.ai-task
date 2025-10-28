# This file implements a FastAPI backend for managing and querying foot traffic data. It defines
# endpoints to retrieve points of interest (POIs), visit records, summary statistics, and to
# ingest new visit data. 

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sqlite3
import os
import csv

# Path to the SQLite database file.
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

# Initialize FastAPI app with CORS middleware to allow all origins.
# Purpose: sets up the web server and enables cross-origin requests for frontend access.
app = FastAPI(title="Foot Traffic API", version="0.1.0")

# CORS middleware configuration to allow all origins, methods, and headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Return a new SQLite connection for local DB access.
# Purpose: centralizes DB connection creation so other functions can open the DB consistently.
# Interaction: used by all route handlers and init_db() to access backend/src/data.db.
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Initialize the DB schema and seed sample data when empty.
# Purpose: ensures the 'venues' table exists and provides deterministic seed rows for development.
# Interaction: called on startup to prepare the SQLite file used by all routes; it writes to data.db.
# normalize and parse numeric fields
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Create venues table if it doesn't exist.
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
    # seed venues if empty and CSV exists at repo root
    cur.execute("SELECT COUNT(*) FROM venues;")
    if cur.fetchone()[0] == 0:
        # look for CSV in backend/ and in project root (repo root may contain the CSV)
        csv_candidates = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Bigbox Stores Metrics.csv'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Bigbox Stores Metrics.csv'),
        ]
        csv_path = None
        for c in csv_candidates:
            if os.path.exists(c):
                csv_path = c
                break
        # seed from CSV if found
        if csv_path:
            # seed venues from CSV
            try:
                with open(csv_path, newline='', encoding='utf-8') as fh:
                    reader = csv.DictReader(fh) 
                    to_insert = []
                    for r in reader:
                        # normalize and parse numeric fields
                        def ival(key):
                            v = r.get(key, '')
                            try:
                                return int(v) if v not in (None, '') else None
                            except Exception:
                                try:
                                    return int(float(v))
                                except Exception:
                                    return None
                        def fval(key):
                            v = r.get(key, '')
                            try:
                                return float(v) if v not in (None, '') else None
                            except Exception:
                                return None
                        to_insert.append((
                            r.get('entity_id'),
                            r.get('entity_type'),
                            r.get('name'),
                            ival('foot_traffic'),
                            fval('sales'),
                            fval('avg_dwell_time_min'),
                            fval('area_sqft'),
                            fval('ft_per_sqft'),
                            r.get('geolocation'),
                            r.get('country'),
                            r.get('state_code'),
                            r.get('state_name'),
                            r.get('city'),
                            r.get('postal_code'),
                            r.get('formatted_city'),
                            r.get('street_address'),
                            r.get('sub_category'),
                            r.get('dma'),
                            r.get('cbsa'),
                            r.get('chain_id'),
                            r.get('chain_name'),
                            r.get('store_id'),
                            r.get('date_opened'),
                            r.get('date_closed')
                        ))
                cur.executemany(
                    "INSERT INTO venues (entity_id, entity_type, name, foot_traffic, sales, avg_dwell_time_min, area_sqft, ft_per_sqft, geolocation, country, state_code, state_name, city, postal_code, formatted_city, street_address, sub_category, dma, cbsa, chain_id, chain_name, store_id, date_opened, date_closed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    to_insert
                )
                conn.commit()
            except Exception as e:
                # don't fail startup on CSV parse errors; leave venues empty
                print('Warning: failed to seed venues from CSV:', e)
    conn.close()

# Startup event handler to initialize DB on application boot.
@app.on_event("startup")
def on_startup():
    init_db()

# GET /api/pois
# Purpose: returns a sorted list of distinct POI names present in the visits table.
# Interaction: queries the visits table and returns a simple array consumed by the frontend filter UI.
# To modify: change the SQL if you want different ordering, filtering (e.g., only POIs with recent visits), or to include counts.
@app.get("/api/pois")
def get_pois():
    """Return distinct venue names (POIs) from the venues table.

    This replaces the older visits-based POI list and matches the new CSV-driven
    venues dataset.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM venues ORDER BY name;")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/api/venues")
def list_venues(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=500),
    chain: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    dma: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    open_status: Optional[str] = Query(default=None),  # 'open'|'closed'|'all'
):
    where = []
    params = []
    # Use case-insensitive partial matching so frontend text inputs work as expected.
    # If the user types part of a chain/category/DMA name we match it (LIKE '%value%')
    if chain and chain.lower() != 'all':
        where.append("chain_name LIKE ? COLLATE NOCASE")
        params.append(f"%{chain}%")
    if category and category.lower() != 'all':
        where.append("sub_category LIKE ? COLLATE NOCASE")
        params.append(f"%{category}%")
    if dma and dma.lower() != 'all':
        where.append("dma LIKE ? COLLATE NOCASE")
        params.append(f"%{dma}%")
    if city and city.lower() != 'all':
        where.append("city = ?")
        params.append(city)
    if state and state.lower() != 'all':
        where.append("state_name = ?")
        params.append(state)
    # filter by open/closed status
    if open_status:
        if open_status.lower() == 'open':
            where.append("(date_closed IS NULL OR date_closed = '')")
        elif open_status.lower() == 'closed':
            where.append("(date_closed IS NOT NULL AND date_closed <> '')")

    base_sql = "FROM venues"
    if where:
        base_sql += " WHERE " + " AND ".join(where)

    conn = get_conn()
    cur = conn.cursor()
    # total count for pagination
    count_sql = f"SELECT COUNT(*) {base_sql};"
    cur.execute(count_sql, params)
    total = cur.fetchone()[0]

    offset = (page - 1) * per_page
    select_sql = f"SELECT id, entity_id, name, chain_name, sub_category, dma, city, state_name, foot_traffic, date_opened, date_closed {base_sql} ORDER BY name COLLATE NOCASE ASC LIMIT ? OFFSET ?;"
    exec_params = list(params) + [per_page, offset]
    cur.execute(select_sql, exec_params)
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "entity_id": r[1],
            "name": r[2],
            "chain_name": r[3],
            "category": r[4],
            "dma": r[5],
            "city": r[6],
            "state": r[7],
            "foot_traffic": r[8] or 0,
            "date_opened": r[9],
            "date_closed": r[10],
        })

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "items": items,
    }


@app.get("/api/venues/summary")
def venues_summary(
    chain: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    dma: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    open_status: Optional[str] = Query(default=None),
):
    where = []
    params = []
    if chain and chain.lower() != 'all':
        where.append("chain_name = ?")
        params.append(chain)
    if category and category.lower() != 'all':
        where.append("sub_category = ?")
        params.append(category)
    if dma and dma.lower() != 'all':
        where.append("dma = ?")
        params.append(dma)
    if city and city.lower() != 'all':
        where.append("city = ?")
        params.append(city)
    if state and state.lower() != 'all':
        where.append("state_name = ?")
        params.append(state)
    if open_status:
        if open_status.lower() == 'open':
            where.append("(date_closed IS NULL OR date_closed = '')")
        elif open_status.lower() == 'closed':
            where.append("(date_closed IS NOT NULL AND date_closed <> '')")

    sql = "SELECT COUNT(*), COALESCE(SUM(foot_traffic),0) "
    sql += "FROM venues"
    if where:
        sql += " WHERE " + " AND ".join(where)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    cnt, total_ft = cur.fetchone()
    conn.close()
    return {"venues": cnt or 0, "total_foot_traffic": total_ft or 0}

    conn.close()