import pytest
from src.health import app

def test_health_endpoint():
    with app.test_client() as client:
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'

def test_status_endpoint():
    with app.test_client() as client:
        resp = client.get('/status')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
        assert 'export_metadata' in data
