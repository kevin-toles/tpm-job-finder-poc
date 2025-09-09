import os
import pytest
from src.config.config_manager import ConfigManager

class TestConfigManager:
    def setup_method(self):
        # Set up test environment variables
        os.environ['TEST_KEY'] = 'test_value'
        os.environ['FEATURE_TOGGLE'] = 'true'
        os.environ['DISABLED_FEATURE'] = 'false'

    def teardown_method(self):
        # Clean up environment variables
        del os.environ['TEST_KEY']
        del os.environ['FEATURE_TOGGLE']
        del os.environ['DISABLED_FEATURE']

    def test_get_returns_value(self):
        assert ConfigManager.get('TEST_KEY') == 'test_value'

    def test_get_returns_default(self):
        assert ConfigManager.get('NON_EXISTENT_KEY', 'default') == 'default'

    def test_is_feature_enabled_true(self):
        assert ConfigManager.is_feature_enabled('FEATURE_TOGGLE') is True

    def test_is_feature_enabled_false(self):
        assert ConfigManager.is_feature_enabled('DISABLED_FEATURE') is False

    def test_is_feature_enabled_missing(self):
        assert ConfigManager.is_feature_enabled('MISSING_FEATURE') is False

    def test_all_returns_dict(self):
        env = ConfigManager.all()
        assert isinstance(env, dict)
        assert env['TEST_KEY'] == 'test_value'
