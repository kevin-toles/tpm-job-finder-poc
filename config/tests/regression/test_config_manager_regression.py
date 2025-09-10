import os
import pytest
from config.config_manager import ConfigManager

def test_regression_env_toggle_behavior():
    os.environ['REGRESSION_FEATURE'] = 'yes'
    assert ConfigManager.is_feature_enabled('REGRESSION_FEATURE') is True
    os.environ['REGRESSION_FEATURE'] = 'no'
    assert ConfigManager.is_feature_enabled('REGRESSION_FEATURE') is False
    del os.environ['REGRESSION_FEATURE']
    assert ConfigManager.is_feature_enabled('REGRESSION_FEATURE') is False
