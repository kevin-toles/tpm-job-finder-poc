import os
import pytest
from src.poc.utils.api_key_loader import load_api_keys
from tpm_job_finder_poc.llm_provider.openai_provider import OpenAIProvider

PROJECT_ROOT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../api_keys.txt'))

def setup_function(function):
    # Overwrite api_keys.txt with test values before each test
    with open(PROJECT_ROOT_CONFIG_PATH, 'w') as f:
        f.write("OPENAI_API_KEY=e2e-key\nANTHROPIC_API_KEY=e2e-anthropic\n")

def teardown_function(function):
    if os.path.exists(PROJECT_ROOT_CONFIG_PATH):
        os.remove(PROJECT_ROOT_CONFIG_PATH)

def test_e2e_app_startup_and_provider():
    keys = load_api_keys()
    provider = OpenAIProvider(api_key=keys["OPENAI_API_KEY"])
    # Simulate a call (mock actual API call)
    assert provider.api_key == "e2e-key"
