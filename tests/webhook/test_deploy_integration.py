import requests
import subprocess
import threading
import time
from webhook.deploy import app

def run_flask():
    app.run(port=5002)

def test_webhook_deploy_integration(monkeypatch):
    # Start Flask app in a thread
    import os
    os.environ["WEBHOOK_TEST_MODE"] = "1"
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    time.sleep(1)  # Wait for server to start
    url = 'http://127.0.0.1:5002/webhook/deploy'
    payload = {"version": "v1.2.3", "action": "roll-forward", "source": "admin"}
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert "Rolled forward to v1.2.3" in resp.json()["result"]
