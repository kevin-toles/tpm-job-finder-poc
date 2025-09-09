
import requests
import threading
import time
from src.webhook.deploy import app
from werkzeug.serving import make_server

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 0, app)
        self.port = self.srv.server_port
        self.daemon = True
    def run(self):
        self.srv.serve_forever()
    def shutdown(self):
        self.srv.shutdown()

def run_test_with_server(test_func):
    server = ServerThread(app)
    server.start()
    time.sleep(0.5)
    try:
        test_func(server.port)
    finally:
        server.shutdown()
        time.sleep(0.2)

def test_webhook_missing_fields():
    def inner(port):
        url = f'http://127.0.0.1:{port}/webhook/deploy'
        resp = requests.post(url, json={"action": "roll-forward"})
        assert resp.status_code == 400
        assert "Missing version or action" in resp.json()["error"]
    run_test_with_server(inner)

def test_webhook_unknown_action():
    def inner(port):
        url = f'http://127.0.0.1:{port}/webhook/deploy'
        resp = requests.post(url, json={"version": "v1.2.3", "action": "unknown", "source": "admin"})
        assert resp.status_code == 400
        assert "Unknown action" in resp.json()["error"]
    run_test_with_server(inner)
