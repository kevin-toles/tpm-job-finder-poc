import os
import pytest
from src.poc.utils.api_key_loader import load_api_keys
from llm_provider.openai_provider import OpenAIProvider

PROJECT_ROOT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../api_keys.txt'))

def setup_function(function):
    # Overwrite api_keys.txt with test values before each test
    with open(PROJECT_ROOT_CONFIG_PATH, 'w') as f:
        f.write("OPENAI_API_KEY=integration-key\nANTHROPIC_API_KEY=integration-anthropic\n")

def teardown_function(function):
    if os.path.exists(PROJECT_ROOT_CONFIG_PATH):
        os.remove(PROJECT_ROOT_CONFIG_PATH)

def test_provider_receives_key():
    keys = load_api_keys()
    provider = OpenAIProvider(api_key=keys["OPENAI_API_KEY"])
    assert provider.api_key == "integration-key"
