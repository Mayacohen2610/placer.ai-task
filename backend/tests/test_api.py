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


# Venue list and pagination
# tests the /api/venues endpoint for correct response structure and pagination.
def test_venues_list_and_pagination():
    # basic list endpoint
    r = client.get('/api/venues')
    assert r.status_code == 200
    data = r.json()
    assert 'items' in data and 'total' in data and 'page' in data
    assert isinstance(data['items'], list)
    # per-item shape if any
    if data['items']:
        sample = data['items'][0]
        expected = {'id', 'entity_id', 'name', 'chain_name', 'category', 'dma', 'city', 'state', 'foot_traffic'}
        assert expected.issubset(set(sample.keys()))

# Venue summary
# tests the /api/venues/summary endpoint for correct response structure.
def test_venues_summary_shape():
    r = client.get('/api/venues/summary')
    assert r.status_code == 200
    data = r.json()
    assert 'venues' in data and 'total_foot_traffic' in data
        
