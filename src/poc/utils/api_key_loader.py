"""
API Key Loader Utility

Checks for API keys in the repo config file first. If not found, loads from an external file at ~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json.
"""
import os
import json

REPO_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'api_keys.json')
EXTERNAL_CONFIG_PATH = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')


def load_api_keys():
    # Try repo config first
    if os.path.exists(REPO_CONFIG_PATH):
        with open(REPO_CONFIG_PATH, 'r') as f:
            keys = json.load(f)
            if keys:
                return keys
    # Fallback to external config
    if os.path.exists(EXTERNAL_CONFIG_PATH):
        with open(EXTERNAL_CONFIG_PATH, 'r') as f:
            keys = json.load(f)
            if keys:
                return keys
    raise FileNotFoundError("No API keys found in repo or external location.")

# Example usage:
# api_keys = load_api_keys()
# print(api_keys)
