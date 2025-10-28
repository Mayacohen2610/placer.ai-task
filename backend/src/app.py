# This file implements a FastAPI backend for managing and querying foot traffic data. It defines
# endpoints to retrieve points of interest (POIs), visit records, summary statistics, and to
# ingest new visit data. 

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import sqlite3
import os
from datetime import datetime

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
# Purpose: ensures the 'visits' table exists and provides deterministic seed rows for development.
# Interaction: called on startup to prepare the SQLite file used by all routes; it writes to data.db.
# To modify: update the CREATE TABLE SQL to add/remove columns or edit the 'seed' list to change starter data.
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    ##### if the visits column will be deferent- change it here ######
    cur.execute('''CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poi TEXT NOT NULL,
        date TEXT NOT NULL,
        visitors INTEGER NOT NULL,
        cbg TEXT,
        dma TEXT,
        dwell REAL
    );''')
    # seed if empty
    cur.execute("SELECT COUNT(*) FROM visits;")
    if cur.fetchone()[0] == 0:
        # initial seed data, not a realistic dataset
        seed = [
            ("Mall A", "2025-10-18", 120, "060371001001", "NY DMA", 23.5),
            ("Mall A", "2025-10-19", 160, "060371001001", "NY DMA", 25.1),
            ("Mall A", "2025-10-20", 140, "060371001001", "NY DMA", 21.3),
            ("Cafe B", "2025-10-18", 60,  "060371002002", "NY DMA", 15.2),
            ("Cafe B", "2025-10-19", 72,  "060371002002", "NY DMA", 14.9),
            ("Gym C",  "2025-10-18", 90,  "060371003003", "NY DMA", 35.0),
            ("Gym C",  "2025-10-19", 88,  "060371003003", "NY DMA", 34.2),
            ("Store D","2025-10-18", 45,  "060371004004", "SF DMA",  10.0),
            ("Store D","2025-10-19", 52,  "060371004004", "SF DMA",  11.2),
            ("Store D","2025-10-20", 55,  "060371004004", "SF DMA",  11.8),
        ]
        ##### if the visits column will be deferent- change it here ######
        cur.executemany("INSERT INTO visits (poi, date, visitors, cbg, dma, dwell) VALUES (?,?,?,?,?,?)", seed)
        conn.commit()
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
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT poi FROM visits ORDER BY poi;")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows

# GET /api/visits
# filters function
# Purpose: returns visit rows filtered by optional poi, date_from and date_to query params; retains original row fields.
# Interaction: builds a parameterized SQL WHERE clause to prevent SQL injection and returns JSON the frontend expects.
# To modify: adjust the select list to include/exclude columns, change ordering, or extend validation on date formats before querying.
@app.get("/api/visits")
def get_visits(
    poi: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
):
    where = []
    params = []
    if poi and poi.lower() != "all":
        where.append("poi = ?")
        params.append(poi)
    if date_from:
        where.append("date >= ?")
        params.append(date_from)
    if date_to:
        where.append("date <= ?")
        params.append(date_to)
    sql = "SELECT poi, date, visitors, cbg, dma, dwell FROM visits"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY date ASC;"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [{
        "poi": r[0],
        "date": r[1],
        "visitors": r[2],
        "cbg": r[3],
        "dma": r[4],
        "dwell": r[5]
    } for r in rows]

# GET /api/summary
# Purpose: computes aggregate metrics (row count, sum, average visitors, average dwell) for given filters.
# Interaction: runs a single SQL aggregation query against visits and returns compact summary JSON consumed by the UI.
# To modify: change which aggregates are returned (e.g., median) or adjust rounding/formatting before returning.
@app.get("/api/summary")
def summary(
    poi: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
):
    where = []
    params = []
    if poi and poi.lower() != "all":
        where.append("poi = ?")
        params.append(poi)
    if date_from:
        where.append("date >= ?")
        params.append(date_from)
    if date_to:
        where.append("date <= ?")
        params.append(date_to)
    sql = "SELECT COUNT(*), SUM(visitors), AVG(visitors), AVG(dwell) FROM visits"
    if where:
        sql += " WHERE " + " AND ".join(where)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    count_, total, avg, avg_dwell = cur.fetchone()
    conn.close()
    return {
        "rows": count_ or 0,
        "total_visitors": total or 0,
        "avg_visitors": round(avg, 2) if avg else 0,
        "avg_dwell": round(avg_dwell, 2) if avg_dwell else 0,
    }

# POST /api/ingest
# Purpose: accepts a list of JSON rows and inserts them into the visits table after basic validation.
# Interaction: validates date format and visitor count, then performs parameterized inserts; errors roll back and return HTTP 400.
# To modify: extend validation rules (e.g., stricter date checks, required cbg/dma), batch-insert optimizations, or schema mapping.
@app.post("/api/ingest")
def ingest(csv_rows: List[Dict[str, Any]]):
    # Expecting rows like: { "poi": "...", "date": "YYYY-MM-DD", "visitors": 123, "cbg": "...", "dma": "...", "dwell": 12.3 }
    if not isinstance(csv_rows, list) or not csv_rows:
        raise HTTPException(status_code=400, detail="Expected non-empty list of rows")
    conn = get_conn()
    cur = conn.cursor()
    for r in csv_rows:
        try:
            # Basic validation
            _ = datetime.strptime(r.get("date"), "%Y-%m-%d")
            visitors = int(r.get("visitors", 0))
            cur.execute(
                "INSERT INTO visits (poi, date, visitors, cbg, dma, dwell) VALUES (?,?,?,?,?,?)",
                (r.get("poi","Unknown"), r["date"], visitors, r.get("cbg"), r.get("dma"), r.get("dwell")),
            )
        except Exception as e:
            conn.rollback()
            conn.close()
            raise HTTPException(status_code=400, detail=f"Bad row: {r}. Error: {e}")
    conn.commit()
    conn.close()
    return {"inserted": len(csv_rows)}