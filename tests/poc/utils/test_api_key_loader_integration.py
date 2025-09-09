import os
import json
from src.poc.utils.api_key_loader import load_api_keys
from src.llm_provider.openai_provider import OpenAIProvider

def setup_module(module):
    external_path = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')
    os.makedirs(os.path.dirname(external_path), exist_ok=True)
    with open(external_path, 'w') as f:
        json.dump({"OPENAI_API_KEY": "integration-key"}, f)

def teardown_module(module):
    external_path = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')
    if os.path.exists(external_path):
        os.remove(external_path)

def test_provider_receives_key():
    keys = load_api_keys()
    provider = OpenAIProvider(api_key=keys["OPENAI_API_KEY"])
    assert provider.api_key == "integration-key"
