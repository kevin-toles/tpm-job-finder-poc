"""
TDD Unit tests for API Gateway configuration management.

Tests configuration loading, validation, and management including:
- Configuration schema validation
- Environment variable loading
- Configuration file parsing
- Dynamic configuration updates
- Configuration validation and defaults
"""

import pytest
import os
import tempfile
import json
import yaml
from unittest.mock import patch, Mock
from pathlib import Path

class TestAPIGatewayConfigurationModel:
    """Test configuration data model."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        from tpm_job_finder_poc.api_gateway_service.config import APIGatewayConfig
        
        config = APIGatewayConfig()
        
        assert config.service_name == "api_gateway_service"
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.require_authentication is True
        assert config.enable_rate_limiting is True
        assert config.default_rate_limit_requests == 1000
        assert config.default_rate_limit_window_seconds == 3600
        assert config.max_concurrent_requests == 1000
        assert config.request_timeout_seconds == 30.0
        assert config.enable_cors is True
        assert config.cors_origins == ["*"]
        assert config.enable_metrics is True
        assert config.log_level == "INFO"
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        from tpm_job_finder_poc.api_gateway_service.config import APIGatewayConfig
        
        config = APIGatewayConfig(
            service_name="custom_gateway",
            port=9090,
            auth_service_url="http://auth:8001",
            enable_rate_limiting=False,
            max_concurrent_requests=500,
            cors_origins=["https://example.com"],
            log_level="DEBUG"
        )
        
        assert config.service_name == "custom_gateway"
        assert config.port == 9090
        assert config.auth_service_url == "http://auth:8001"
        assert config.enable_rate_limiting is False
        assert config.max_concurrent_requests == 500
        assert config.cors_origins == ["https://example.com"]
        assert config.log_level == "DEBUG"
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        from tpm_job_finder_poc.api_gateway_service.config import APIGatewayConfig
        
        # Invalid port
        with pytest.raises(ValueError):
            APIGatewayConfig(port=-1)
        
        # Invalid timeout
        with pytest.raises(ValueError):
            APIGatewayConfig(request_timeout_seconds=-1.0)
        
        # Invalid rate limit values
        with pytest.raises(ValueError):
            APIGatewayConfig(default_rate_limit_requests=0)
        
        # Invalid log level
        with pytest.raises(ValueError):
            APIGatewayConfig(log_level="INVALID")

class TestConfigurationLoader:
    """Test configuration loading from various sources."""
    
    @pytest.fixture
    def config_loader(self):
        """Create configuration loader for testing."""
        from tpm_job_finder_poc.api_gateway_service.config import ConfigurationLoader
        return ConfigurationLoader()
    
    def test_load_from_environment_variables(self, config_loader):
        """Test loading configuration from environment variables."""
        env_vars = {
            "GATEWAY_SERVICE_NAME": "env_gateway",
            "GATEWAY_PORT": "9000",
            "GATEWAY_ENABLE_RATE_LIMITING": "false",
            "GATEWAY_AUTH_SERVICE_URL": "http://env-auth:8001",
            "GATEWAY_LOG_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars):
            config = config_loader.load_from_environment()
            
            assert config.service_name == "env_gateway"
            assert config.port == 9000
            assert config.enable_rate_limiting is False
            assert config.auth_service_url == "http://env-auth:8001"
            assert config.log_level == "DEBUG"
    
    def test_load_from_json_file(self, config_loader):
        """Test loading configuration from JSON file."""
        config_data = {
            "service_name": "json_gateway",
            "port": 8888,
            "enable_cors": False,
            "cors_origins": ["https://trusted.com"],
            "max_concurrent_requests": 2000
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = config_loader.load_from_file(temp_path)
            
            assert config.service_name == "json_gateway"
            assert config.port == 8888
            assert config.enable_cors is False
            assert config.cors_origins == ["https://trusted.com"]
            assert config.max_concurrent_requests == 2000
        finally:
            os.unlink(temp_path)
    
    def test_load_from_yaml_file(self, config_loader):
        """Test loading configuration from YAML file."""
        config_data = {
            "service_name": "yaml_gateway",
            "port": 7777,
            "auth_service_url": "http://yaml-auth:8001",
            "rate_limiting": {
                "enabled": True,
                "default_requests": 500,
                "default_window_seconds": 1800
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = config_loader.load_from_file(temp_path)
            
            assert config.service_name == "yaml_gateway"
            assert config.port == 7777
            assert config.auth_service_url == "http://yaml-auth:8001"
            # Note: nested structure would need custom parsing
        finally:
            os.unlink(temp_path)
    
    def test_load_configuration_file_not_found(self, config_loader):
        """Test handling of missing configuration file."""
        with pytest.raises(FileNotFoundError):
            config_loader.load_from_file("/nonexistent/config.json")
    
    def test_load_invalid_json_file(self, config_loader):
        """Test handling of invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                config_loader.load_from_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_merge_configurations(self, config_loader):
        """Test merging configurations from multiple sources."""
        # Base configuration
        base_config = {
            "service_name": "base_gateway",
            "port": 8080,
            "enable_rate_limiting": True
        }
        
        # Override configuration
        override_config = {
            "port": 9090,
            "auth_service_url": "http://override-auth:8001"
        }
        
        merged = config_loader.merge_configurations(base_config, override_config)
        
        assert merged["service_name"] == "base_gateway"  # From base
        assert merged["port"] == 9090  # Overridden
        assert merged["enable_rate_limiting"] is True  # From base
        assert merged["auth_service_url"] == "http://override-auth:8001"  # From override

class TestConfigurationManager:
    """Test configuration management functionality."""
    
    @pytest.fixture
    def config_manager(self):
        """Create configuration manager for testing."""
        from tpm_job_finder_poc.api_gateway_service.config import ConfigurationManager
        return ConfigurationManager()
    
    def test_get_current_configuration(self, config_manager):
        """Test getting current configuration."""
        config = config_manager.get_current_configuration()
        
        assert hasattr(config, 'service_name')
        assert hasattr(config, 'port')
        assert hasattr(config, 'enable_rate_limiting')
    
    def test_update_configuration(self, config_manager):
        """Test updating configuration."""
        updates = {
            "enable_rate_limiting": False,
            "default_rate_limit_requests": 2000,
            "log_level": "DEBUG"
        }
        
        result = config_manager.update_configuration(updates)
        assert result is True
        
        # Verify updates were applied
        config = config_manager.get_current_configuration()
        assert config.enable_rate_limiting is False
        assert config.default_rate_limit_requests == 2000
        assert config.log_level == "DEBUG"
    
    def test_update_configuration_validation_error(self, config_manager):
        """Test configuration update with validation errors."""
        invalid_updates = {
            "port": -1,
            "log_level": "INVALID"
        }
        
        with pytest.raises(ValueError):
            config_manager.update_configuration(invalid_updates)
    
    def test_reload_configuration(self, config_manager):
        """Test reloading configuration from file."""
        config_data = {
            "service_name": "reloaded_gateway",
            "port": 8888
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            result = config_manager.reload_configuration(temp_path)
            assert result is True
            
            config = config_manager.get_current_configuration()
            assert config.service_name == "reloaded_gateway"
            assert config.port == 8888
        finally:
            os.unlink(temp_path)
    
    def test_configuration_change_notification(self, config_manager):
        """Test configuration change notifications."""
        callback_called = False
        callback_data = None
        
        def config_change_callback(old_config, new_config):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = (old_config, new_config)
        
        config_manager.register_change_callback(config_change_callback)
        
        # Update configuration
        updates = {"port": 9999}
        config_manager.update_configuration(updates)
        
        assert callback_called is True
        assert callback_data is not None
        old_config, new_config = callback_data
        assert old_config.port != new_config.port
        assert new_config.port == 9999

class TestConfigurationValidation:
    """Test configuration validation rules."""
    
    def test_port_validation(self):
        """Test port number validation."""
        from tpm_job_finder_poc.api_gateway_service.config import validate_port
        
        # Valid ports
        assert validate_port(80) is True
        assert validate_port(8080) is True
        assert validate_port(65535) is True
        
        # Invalid ports
        assert validate_port(-1) is False
        assert validate_port(0) is False
        assert validate_port(65536) is False
        assert validate_port("8080") is False
    
    def test_url_validation(self):
        """Test URL validation."""
        from tpm_job_finder_poc.api_gateway_service.config import validate_url
        
        # Valid URLs
        assert validate_url("http://localhost:8001") is True
        assert validate_url("https://auth-service:8001") is True
        assert validate_url("http://192.168.1.100:8000") is True
        
        # Invalid URLs
        assert validate_url("invalid-url") is False
        assert validate_url("ftp://localhost:8001") is False
        assert validate_url("") is False
        assert validate_url(None) is False
    
    def test_cors_origins_validation(self):
        """Test CORS origins validation."""
        from tpm_job_finder_poc.api_gateway_service.config import validate_cors_origins
        
        # Valid origins
        assert validate_cors_origins(["*"]) is True
        assert validate_cors_origins(["https://example.com"]) is True
        assert validate_cors_origins(["https://app.com", "https://admin.com"]) is True
        
        # Invalid origins
        assert validate_cors_origins(["invalid-origin"]) is False
        assert validate_cors_origins([]) is False
        assert validate_cors_origins("https://example.com") is False  # Should be list
    
    def test_rate_limit_validation(self):
        """Test rate limit configuration validation."""
        from tpm_job_finder_poc.api_gateway_service.config import validate_rate_limit_config
        
        # Valid configurations
        assert validate_rate_limit_config(100, 3600) is True
        assert validate_rate_limit_config(1000, 60) is True
        
        # Invalid configurations
        assert validate_rate_limit_config(0, 3600) is False
        assert validate_rate_limit_config(-1, 3600) is False
        assert validate_rate_limit_config(100, 0) is False
        assert validate_rate_limit_config(100, -1) is False

class TestConfigurationDefaults:
    """Test configuration default values and fallbacks."""
    
    def test_service_discovery_defaults(self):
        """Test service discovery default configuration."""
        from tpm_job_finder_poc.api_gateway_service.config import get_service_discovery_defaults
        
        defaults = get_service_discovery_defaults()
        
        assert "enabled" in defaults
        assert "discovery_interval_seconds" in defaults
        assert "health_check_interval_seconds" in defaults
        assert "unhealthy_threshold" in defaults
        assert "healthy_threshold" in defaults
    
    def test_rate_limiting_defaults(self):
        """Test rate limiting default configuration."""
        from tpm_job_finder_poc.api_gateway_service.config import get_rate_limiting_defaults
        
        defaults = get_rate_limiting_defaults()
        
        assert "global_requests_per_window" in defaults
        assert "global_window_seconds" in defaults
        assert "user_requests_per_window" in defaults
        assert "user_window_seconds" in defaults
        assert "ip_requests_per_window" in defaults
        assert "ip_window_seconds" in defaults
    
    def test_security_defaults(self):
        """Test security default configuration."""
        from tpm_job_finder_poc.api_gateway_service.config import get_security_defaults
        
        defaults = get_security_defaults()
        
        assert "require_authentication" in defaults
        assert "enable_cors" in defaults
        assert "cors_origins" in defaults
        assert "max_request_size_bytes" in defaults
        assert "enable_request_logging" in defaults

class TestConfigurationPersistence:
    """Test configuration persistence functionality."""
    
    @pytest.fixture
    def config_persistence(self):
        """Create configuration persistence manager for testing."""
        from tpm_job_finder_poc.api_gateway_service.config import ConfigurationPersistence
        return ConfigurationPersistence()
    
    def test_save_configuration_to_file(self, config_persistence):
        """Test saving configuration to file."""
        from tpm_job_finder_poc.api_gateway_service.config import APIGatewayConfig
        
        config = APIGatewayConfig(
            service_name="test_save",
            port=8888,
            enable_rate_limiting=False
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            result = config_persistence.save_configuration(config, temp_path)
            assert result is True
            
            # Verify file was created and contains correct data
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
                assert saved_data["service_name"] == "test_save"
                assert saved_data["port"] == 8888
                assert saved_data["enable_rate_limiting"] is False
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_configuration_from_file(self, config_persistence):
        """Test loading configuration from file."""
        config_data = {
            "service_name": "test_load",
            "port": 9999,
            "auth_service_url": "http://test-auth:8001"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = config_persistence.load_configuration(temp_path)
            
            assert config.service_name == "test_load"
            assert config.port == 9999
            assert config.auth_service_url == "http://test-auth:8001"
        finally:
            os.unlink(temp_path)
    
    def test_backup_configuration(self, config_persistence):
        """Test configuration backup functionality."""
        from tpm_job_finder_poc.api_gateway_service.config import APIGatewayConfig
        
        config = APIGatewayConfig(service_name="backup_test")
        
        backup_path = config_persistence.create_backup(config)
        
        assert os.path.exists(backup_path)
        assert "backup" in backup_path
        assert backup_path.endswith(".json")
        
        # Verify backup contains correct data
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
            assert backup_data["service_name"] == "backup_test"
        
        # Cleanup
        os.unlink(backup_path)
    
    def test_restore_configuration_from_backup(self, config_persistence):
        """Test restoring configuration from backup."""
        from tpm_job_finder_poc.api_gateway_service.config import APIGatewayConfig
        
        # Create and backup a configuration
        original_config = APIGatewayConfig(service_name="restore_test", port=7777)
        backup_path = config_persistence.create_backup(original_config)
        
        try:
            # Restore from backup
            restored_config = config_persistence.restore_from_backup(backup_path)
            
            assert restored_config.service_name == "restore_test"
            assert restored_config.port == 7777
        finally:
            os.unlink(backup_path)