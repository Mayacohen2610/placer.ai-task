# This file implements a FastAPI backend for managing and querying foot traffic data. It defines
# endpoints to retrieve points of interest (POIs), visit records, summary statistics.

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import sqlite3
import os
import csv
import io

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
# Purpose: returns a sorted list of distinct POI names present in the venues table.
# NOTE: this endpoint is no longer used by the frontend. It is kept for
# backward-compatibility. 
@app.get("/api/pois", deprecated=True)
def get_pois():
    """Return distinct venue names (POIs) from the venues table.

    Deprecated: frontend uses `/api/venues` and `/api/distinct/{field}` instead.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM venues ORDER BY name;")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows

# GET /api/distinct/{field}
# Purpose: returns distinct values for specified fields with optional filtering.
# in used by frontend to populate filter dropdowns for chain, category, DMA.
@app.get("/api/distinct/{field}")
def get_distinct(field: str, q: Optional[str] = Query(default=None)):
    """Return distinct values for supported fields: 'chain', 'category', 'dma', 'name'.
    Optional query `q` filters suggestions using partial, case-insensitive match.
    """
    # supported suggestion fields for frontend filters
    mapping = {
        'chain': 'chain_name',
        'category': 'sub_category',
        'dma': 'dma',
    }
    col = mapping.get(field)
    if not col:
        raise HTTPException(status_code=400, detail='unsupported field')

    conn = get_conn()
    cur = conn.cursor()
    if q:
        sql = f"SELECT DISTINCT {col} FROM venues WHERE {col} IS NOT NULL AND {col} <> '' AND {col} LIKE ? COLLATE NOCASE ORDER BY {col} LIMIT 100;"
        cur.execute(sql, (f"%{q}%",))
    else:
        sql = f"SELECT DISTINCT {col} FROM venues WHERE {col} IS NOT NULL AND {col} <> '' ORDER BY {col} LIMIT 500;"
        cur.execute(sql)
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


# GET /api/venues
# Purpose: returns a paginated list of venues with optional filtering by chain, category, DMA.
@app.get("/api/venues")
def list_venues(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=500),
    chain: Optional[List[str]] = Query(default=None),
    category: Optional[List[str]] = Query(default=None),
    dma: Optional[List[str]] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    open_status: Optional[str] = Query(default=None),  # 'open'|'closed'|'all'
):
    where = []
    params = []
    # Support multiple selections for chain/category/dma. Each provided value will be
    # matched case-insensitively and partially (LIKE '%value%'). Multiple values per
    # field are ORed together and different fields are ANDed.
    def add_multi_like(field_vals, column_name):
        if not field_vals:
            return
        # ignore the sentinel 'all' entries
        vals = [v for v in field_vals if v and v.lower() != 'all']
        if not vals:
            return
        sub = []
        for v in vals:
            sub.append(f"{column_name} LIKE ? COLLATE NOCASE")
            params.append(f"%{v}%")
        where.append("(" + " OR ".join(sub) + ")")

    add_multi_like(chain, 'chain_name')
    add_multi_like(category, 'sub_category')
    add_multi_like(dma, 'dma')
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

    # paginated select
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


# GET /api/venues/summary
# Purpose: returns summary statistics about venues with optional filtering.
@app.get("/api/venues/summary")
def venues_summary(
    chain: Optional[List[str]] = Query(default=None),
    category: Optional[List[str]] = Query(default=None),
    dma: Optional[List[str]] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    open_status: Optional[str] = Query(default=None),
):
    where = []
    params = []
    # support multiple values (ORed) and partial case-insensitive matching
    def add_multi_like(field_vals, column_name):
        if not field_vals:
            return
        vals = [v for v in field_vals if v and v.lower() != 'all']
        if not vals:
            return
        sub = []
        for v in vals:
            sub.append(f"{column_name} LIKE ? COLLATE NOCASE")
            params.append(f"%{v}%")
        where.append("(" + " OR ".join(sub) + ")")

    add_multi_like(chain, 'chain_name')
    add_multi_like(category, 'sub_category')
    add_multi_like(dma, 'dma')
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



@app.get("/api/venues/export")
def export_venues(
    chain: Optional[List[str]] = Query(default=None),
    category: Optional[List[str]] = Query(default=None),
    dma: Optional[List[str]] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    open_status: Optional[str] = Query(default=None),
):
    """Export filtered venues as CSV. Uses the same filter semantics as /api/venues."""
    where = []
    params = []
    def add_multi_like(field_vals, column_name):
        if not field_vals:
            return
        vals = [v for v in field_vals if v and v.lower() != 'all']
        if not vals:
            return
        sub = []
        for v in vals:
            sub.append(f"{column_name} LIKE ? COLLATE NOCASE")
            params.append(f"%{v}%")
        where.append("(" + " OR ".join(sub) + ")")

    add_multi_like(chain, 'chain_name')
    add_multi_like(category, 'sub_category')
    add_multi_like(dma, 'dma')
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

    base_sql = "FROM venues"
    if where:
        base_sql += " WHERE " + " AND ".join(where)

    conn = get_conn()
    cur = conn.cursor()
    select_sql = f"SELECT id, entity_id, name, chain_name, sub_category, dma, city, state_name, foot_traffic, date_opened, date_closed {base_sql} ORDER BY name COLLATE NOCASE;"
    cur.execute(select_sql, params)
    rows = cur.fetchall()
    conn.close()

    def iter_csv():
        buf = io.StringIO()
        writer = csv.writer(buf)
        headers = ['id', 'entity_id', 'name', 'chain_name', 'category', 'dma', 'city', 'state', 'foot_traffic', 'date_opened', 'date_closed']
        writer.writerow(headers)
        yield buf.getvalue()
        buf.seek(0); buf.truncate(0)
        for r in rows:
            writer.writerow([
                r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8] or 0, r[9], r[10]
            ])
            yield buf.getvalue()
            buf.seek(0); buf.truncate(0)

    return StreamingResponse(iter_csv(), media_type='text/csv', headers={
        'Content-Disposition': 'attachment; filename="venues.csv"'
    })