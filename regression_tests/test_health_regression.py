import json
from src.health import app
from pathlib import Path

def test_regression_status_endpoint_missing_metadata(tmp_path):
    # No metadata file present
    app.config['TESTING'] = True
    app.config['EXPORT_METADATA_PATH'] = str(tmp_path / "missing.json")
    with app.test_client() as client:
        resp = client.get('/status')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
        assert data['export_metadata'] == {}
