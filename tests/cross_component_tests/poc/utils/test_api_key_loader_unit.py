import os
import json
import pytest
from tpm_job_finder_poc.poc.utils.api_key_loader import load_api_keys


# Use the actual project root path
PROJECT_ROOT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../api_keys.txt'))



def setup_function(function):
    # Overwrite api_keys.txt with test values before each test
    with open(PROJECT_ROOT_CONFIG_PATH, 'w') as f:
        f.write("OPENAI_API_KEY=repo-key\nANTHROPIC_API_KEY=repo-anthropic\n")

def teardown_function(function):
    if os.path.exists(PROJECT_ROOT_CONFIG_PATH):
        os.remove(PROJECT_ROOT_CONFIG_PATH)




def test_load_from_repo():
    keys = load_api_keys()
    assert keys["OPENAI_API_KEY"] == "repo-key"
    assert keys["ANTHROPIC_API_KEY"] == "repo-anthropic"




def test_load_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-anthropic")
    if os.path.exists(PROJECT_ROOT_CONFIG_PATH):
        os.remove(PROJECT_ROOT_CONFIG_PATH)
    keys = load_api_keys()
    assert keys["OPENAI_API_KEY"] == "env-key"
    assert keys["ANTHROPIC_API_KEY"] == "env-anthropic"




def test_error_if_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    if os.path.exists(PROJECT_ROOT_CONFIG_PATH):
        os.remove(PROJECT_ROOT_CONFIG_PATH)
    with pytest.raises(FileNotFoundError):
        load_api_keys()
