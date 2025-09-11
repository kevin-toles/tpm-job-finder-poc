import requests
import threading
import time
from tpm_job_finder_poc.webhook.deploy import app

def run_flask():
    app.run(port=5004)

def test_webhook_e2e_rollforward_and_rollback():
    import os
    os.environ["WEBHOOK_TEST_MODE"] = "1"
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    time.sleep(1)
    url = 'http://127.0.0.1:5004/webhook/deploy'
    # Roll-forward
    resp1 = requests.post(url, json={"version": "v2.0.0", "action": "roll-forward", "source": "github"})
    assert resp1.status_code == 200
    assert "Rolled forward to v2.0.0" in resp1.json()["result"]
    # Rollback
    resp2 = requests.post(url, json={"version": "v1.0.0", "action": "rollback", "source": "admin"})
    assert resp2.status_code == 200
    assert "Rolled back to v1.0.0" in resp2.json()["result"]
