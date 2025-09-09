import os
import json
import pytest
from src.poc.utils.api_key_loader import load_api_keys

def setup_module(module):
    external_path = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')
    os.makedirs(os.path.dirname(external_path), exist_ok=True)
    with open(external_path, 'w') as f:
        json.dump({"OPENAI_API_KEY": "regression-key"}, f)

def teardown_module(module):
    external_path = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')
    if os.path.exists(external_path):
        os.remove(external_path)

def test_fallback_logic():
    # Remove repo config if present
    repo_path = os.path.join(os.path.dirname(__file__), 'api_keys.json')
    if os.path.exists(repo_path):
        os.remove(repo_path)
    keys = load_api_keys()
    assert keys["OPENAI_API_KEY"] == "regression-key"

def test_no_keys_loaded():
    external_path = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')
    if os.path.exists(external_path):
        os.remove(external_path)
    with pytest.raises(FileNotFoundError):
        load_api_keys()
