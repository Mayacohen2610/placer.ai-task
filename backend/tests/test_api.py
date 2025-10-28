import sys
import os

# Ensure src is importable when tests run from backend/
HERE = os.path.dirname(__file__)
SRC = os.path.abspath(os.path.join(HERE, '..', 'src'))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from fastapi.testclient import TestClient
from app import app


client = TestClient(app)

# Basic tests to verify API endpoints are reachable and return expected structures.
def test_pois_ok():
    r = client.get('/api/pois')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

# Verify /api/summary returns expected keys
def test_summary_shape():
    r = client.get('/api/summary')
    assert r.status_code == 200
    data = r.json()
    # expected keys present
    assert 'rows' in data and 'total_visitors' in data and 'avg_visitors' in data

# Verify /api/visits returns a list of visit records
def test_visits_shape():
    r = client.get('/api/visits')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        sample = data[0]
        expected_keys = {'poi', 'date', 'visitors', 'cbg', 'dma', 'dwell'}
        assert expected_keys.issubset(sample.keys())    
        
