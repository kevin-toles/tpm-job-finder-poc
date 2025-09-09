import json
from src.health import app

def test_status_endpoint_with_metadata(tmp_path):
    # Create a fake export metadata file
    meta_path = tmp_path / "last_export.json"
    meta = {"last_export_time": "2025-09-08T12:00:00Z", "status": "success"}
    meta_path.write_text(json.dumps(meta))
    # Patch the app to use the test metadata path
    app.config['TESTING'] = True
    app.config['EXPORT_METADATA_PATH'] = str(meta_path)
    with app.test_client() as client:
        resp = client.get('/status')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
        assert data['export_metadata'] == meta
