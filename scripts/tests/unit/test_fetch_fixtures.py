import os
import json
import tempfile
import pytest
from scripts import fetch_fixtures
import requests

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"Status {self.status_code}")

@pytest.fixture
def temp_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "sample.json")

def test_save_fixture_saves_file_correctly(temp_file):
    data = {"foo": "bar"}
    fetch_fixtures.save_fixture(data, temp_file)
    assert os.path.exists(temp_file)
    with open(temp_file) as f:
        loaded = json.load(f)
    assert loaded == data

def test_save_fixture_valid_json(temp_file):
    data = {"foo": [1, 2, 3]}
    fetch_fixtures.save_fixture(data, temp_file)
    with open(temp_file) as f:
        loaded = json.load(f)
    assert isinstance(loaded["foo"], list)

def test_fetch_remoteok_handles_failed_request(monkeypatch):
    def mock_get(*args, **kwargs):
        return DummyResponse({}, status_code=404)
    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(requests.HTTPError):
        fetch_fixtures.fetch_remoteok()

# Similar error handling tests can be written for fetch_greenhouse and fetch_lever
