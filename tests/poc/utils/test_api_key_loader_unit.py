import os
import json
import pytest
from src.poc.utils.api_key_loader import load_api_keys

REPO_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../../src/poc/utils/api_keys.json')
EXTERNAL_CONFIG_PATH = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')

def setup_module(module):
    # Create test files
    with open(REPO_CONFIG_PATH, 'w') as f:
        json.dump({"OPENAI_API_KEY": "repo-key"}, f)
    os.makedirs(os.path.dirname(EXTERNAL_CONFIG_PATH), exist_ok=True)
    with open(EXTERNAL_CONFIG_PATH, 'w') as f:
        json.dump({"OPENAI_API_KEY": "external-key"}, f)

def teardown_module(module):
    if os.path.exists(REPO_CONFIG_PATH):
        os.remove(REPO_CONFIG_PATH)
    if os.path.exists(EXTERNAL_CONFIG_PATH):
        os.remove(EXTERNAL_CONFIG_PATH)

def test_load_from_repo():
    keys = load_api_keys()
    assert keys["OPENAI_API_KEY"] == "repo-key"

def test_load_from_external(monkeypatch):
    if os.path.exists(REPO_CONFIG_PATH):
        os.remove(REPO_CONFIG_PATH)
    keys = load_api_keys()
    assert keys["OPENAI_API_KEY"] == "external-key"

def test_error_if_missing(monkeypatch):
    if os.path.exists(REPO_CONFIG_PATH):
        os.remove(REPO_CONFIG_PATH)
    if os.path.exists(EXTERNAL_CONFIG_PATH):
        os.remove(EXTERNAL_CONFIG_PATH)
    with pytest.raises(FileNotFoundError):
        load_api_keys()
