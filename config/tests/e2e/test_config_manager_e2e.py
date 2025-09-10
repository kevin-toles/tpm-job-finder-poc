import os
from config.config_manager import ConfigManager

def test_e2e_config_manager_usage():
    # Simulate full workflow: set, get, toggle
    os.environ['E2E_API_KEY'] = 'e2e-key'
    os.environ['E2E_FEATURE'] = 'on'
    assert ConfigManager.get('E2E_API_KEY') == 'e2e-key'
    assert ConfigManager.is_feature_enabled('E2E_FEATURE') is True
    del os.environ['E2E_API_KEY']
    del os.environ['E2E_FEATURE']
