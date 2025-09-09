import json
from src.health import app
from pathlib import Path

def test_e2e_health_status_workflow(tmp_path):
    # Simulate a full workflow: create metadata, check endpoints
    meta_path = tmp_path / "last_export.json"
    meta = {"last_export_time": "2025-09-08T15:00:00Z", "status": "success"}
    meta_path.write_text(json.dumps(meta))
    app.config['TESTING'] = True
    app.config['EXPORT_METADATA_PATH'] = str(meta_path)
    with app.test_client() as client:
        health_resp = client.get('/health')
        assert health_resp.status_code == 200
        assert health_resp.get_json()['status'] == 'ok'
        status_resp = client.get('/status')
        assert status_resp.status_code == 200
        data = status_resp.get_json()
        assert data['status'] == 'ok'
        assert data['export_metadata'] == meta
