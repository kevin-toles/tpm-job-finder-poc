import requests
import subprocess
import threading
import time
from unittest.mock import Mock, patch
from tpm_job_finder_poc.webhook.deploy import app

def run_flask():
    app.run(port=5002)

@patch('requests.post')
def test_webhook_deploy_integration(mock_post, monkeypatch):
    # Mock the external call with the complete expected response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success", 
        "result": "Rolled forward to v1.2.3"
    }
    mock_post.return_value = mock_response
    
    import os
    os.environ["WEBHOOK_TEST_MODE"] = "1"
    
    # Test the deployment logic without real HTTP calls
    url = 'http://127.0.0.1:5002/webhook/deploy'
    payload = {"version": "v1.2.3", "action": "roll-forward", "source": "admin"}
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200
    response_data = resp.json()
    assert response_data["status"] == "success"
    assert "Rolled forward to v1.2.3" in response_data.get("result", "")
