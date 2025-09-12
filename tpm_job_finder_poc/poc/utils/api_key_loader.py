import os
import json

def load_api_keys():
    """
    Load API keys from environment variables, repo config, or external config.
    Priority: env vars -> repo config -> external config
    """
    keys = {}
    
    # Try environment variables first
    env_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "OLLAMA_API_KEY"]
    for key in env_keys:
        if key in os.environ:
            keys[key] = os.environ[key]
    
    if keys:
        return keys
    
    # Try repo config file
    repo_config_path = os.path.join(os.path.dirname(__file__), 'api_keys.json')
    if os.path.exists(repo_config_path):
        with open(repo_config_path, 'r') as f:
            return json.load(f)
    
    # Try external config file  
    external_config_path = os.path.expanduser('~/Desktop/tpm-job-finder-poc-API Keys/api_keys.json')
    if os.path.exists(external_config_path):
        with open(external_config_path, 'r') as f:
            return json.load(f)
    
    # Try api_keys.txt in project root (for cross_component_tests)
    project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../api_keys.txt'))
    if os.path.exists(project_root_path):
        keys = {}
        with open(project_root_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    keys[key.strip()] = value.strip()
        if keys:
            return keys
    
    # No keys found
    raise FileNotFoundError("No API keys found in environment, repo config, or external config")
