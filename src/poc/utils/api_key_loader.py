"""
API Key Loader Utility

Checks for API keys in the repo config file first. If not found, loads from an external file at ~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json.
"""
import os
import json

REPO_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../api_keys.txt'))





def load_api_keys():
    # Try repo config first (project root)
    print(f"DEBUG: Checking for API keys at {REPO_CONFIG_PATH}")
    if os.path.exists(REPO_CONFIG_PATH):
        keys = {}
        with open(REPO_CONFIG_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    k, v = line.split('=', 1)
                    keys[k.strip()] = v.strip()
        if keys:
            return keys
    # Fallback to environment variables
    env_keys = {}
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "OLLAMA_API_KEY"]:
        value = os.environ.get(key)
        if value:
            env_keys[key] = value
    if env_keys:
        return env_keys
    raise FileNotFoundError("No API keys found in repo or environment variables.")

# Example usage:
# api_keys = load_api_keys()
# print(api_keys)
