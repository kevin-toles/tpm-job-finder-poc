"""
Config Management Service TDD Tests

This module contains comprehensive TDD tests for the ConfigManagementServiceTDD.
These tests define the requirements and expected behavior for the config management 
microservice before implementation (RED phase).

Test Categories:
1. Configuration Loading and Saving
2. Environment Variable Integration
3. Hierarchical Configuration Management
4. Configuration Validation and Schema
5. Credential and Secret Management
6. Hot Reloading and Dynamic Updates
7. Feature Flag Management
8. Multi-Environment Support
9. Configuration Caching and Performance
10. Error Handling and Resilience
"""

import asyncio
import json
import os
import tempfile
import pytest
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import patch, mock_open, AsyncMock
from datetime import datetime, timezone

# Will be implemented in GREEN phase
try:
    from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
except ImportError:
    # Expected during RED phase - tests should fail
    ConfigManagementServiceTDD = None


@pytest.fixture
def config_service_config():
    """Fixture providing configuration for ConfigManagementServiceTDD."""
    return {
        "service_name": "config_management_service",
        "environment": "test",
        "config_base_path": "./config",
        "enable_hot_reload": True,
        "enable_caching": True,
        "cache_ttl_seconds": 300,
        "enable_validation": True,
        "enable_encryption": False,
        "max_config_size_mb": 10,
        "backup_configs": True,
        "audit_changes": True,
        "feature_flags": {
            "enable_remote_config": False,
            "enable_config_api": True,
            "enable_config_ui": False
        }
    }


@pytest.fixture
def sample_global_config():
    """Fixture providing sample global configuration."""
    return {
        "app": {
            "name": "TPM Job Finder",
            "version": "1.0.0",
            "debug": False
        },
        "database": {
            "url": "sqlite:///jobs.db",
            "pool_size": 10,
            "timeout": 30
        },
        "llm_provider": {
            "primary": "openai",
            "fallbacks": ["anthropic", "google"],
            "timeout_seconds": 30,
            "max_retries": 3
        },
        "job_sources": {
            "enabled": ["indeed", "linkedin", "remoteok"],
            "max_jobs_per_source": 100,
            "rate_limit_enabled": True
        },
        "feature_flags": {
            "enable_multi_resume": True,
            "enable_advanced_scoring": True,
            "enable_auto_apply": False
        }
    }


@pytest.fixture
def sample_environment_configs():
    """Fixture providing environment-specific configurations."""
    return {
        "development": {
            "app": {"debug": True},
            "database": {"url": "sqlite:///dev.db"},
            "llm_provider": {"timeout_seconds": 60},
            "feature_flags": {"enable_debug_mode": True}
        },
        "staging": {
            "app": {"debug": False},
            "database": {"url": "postgresql://staging-db:5432/jobs"},
            "llm_provider": {"timeout_seconds": 45},
            "feature_flags": {"enable_debug_mode": False}
        },
        "production": {
            "app": {"debug": False},
            "database": {"url": "postgresql://prod-db:5432/jobs"},
            "llm_provider": {"timeout_seconds": 30},
            "feature_flags": {"enable_debug_mode": False}
        }
    }


@pytest.fixture
def sample_credentials():
    """Fixture providing sample credential configuration."""
    return {
        "openai": {
            "api_key": "sk-test-openai-key",
            "organization": "org-test",
            "base_url": "https://api.openai.com/v1"
        },
        "anthropic": {
            "api_key": "sk-ant-test-key",
            "base_url": "https://api.anthropic.com"
        },
        "database": {
            "username": "test_user",
            "password": "test_password"
        }
    }


class TestConfigurationLoadingAndSaving:
    """Test configuration loading and saving capabilities."""
    
    @pytest.mark.asyncio
    async def test_load_global_configuration(self, config_service_config, sample_global_config):
        """Test loading global configuration from file."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Mock file loading
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                config = await service.load_config("global")
                
                assert config is not None
                assert config["app"]["name"] == "TPM Job Finder"
                assert config["database"]["url"] == "sqlite:///jobs.db"
                assert config["llm_provider"]["primary"] == "openai"
                assert len(config["job_sources"]["enabled"]) == 3
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_save_configuration(self, config_service_config, sample_global_config):
        """Test saving configuration to file."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Test saving configuration
            result = await service.save_config("test_config", sample_global_config)
            
            assert result.success is True
            assert result.config_name == "test_config"
            assert result.file_path is not None
            assert result.backup_created is True
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_config_returns_default(self, config_service_config):
        """Test loading non-existent configuration returns defaults."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            config = await service.load_config("nonexistent")
            
            # Should return empty dict or default config
            assert config is not None
            assert isinstance(config, dict)
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_load_component_specific_config(self, config_service_config):
        """Test loading component-specific configuration."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            llm_config = {
                "primary": "openai",
                "fallbacks": ["anthropic"],
                "timeout_seconds": 30,
                "max_retries": 3,
                "enable_streaming": True
            }
            
            with patch('builtins.open', mock_open(read_data=json.dumps(llm_config))):
                config = await service.load_config("llm_provider")
                
                assert config["primary"] == "openai"
                assert config["timeout_seconds"] == 30
                assert config["enable_streaming"] is True
                
        finally:
            await service.stop()


class TestEnvironmentVariableIntegration:
    """Test environment variable integration capabilities."""
    
    @pytest.mark.asyncio
    async def test_load_config_from_environment_variables(self, config_service_config):
        """Test loading configuration from environment variables."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Mock environment variables
            with patch.dict(os.environ, {
                'APP_DEBUG': 'true',
                'DATABASE_URL': 'postgresql://test:5432/db',
                'LLM_TIMEOUT_SECONDS': '45',
                'FEATURE_ENABLE_AUTO_APPLY': 'true'
            }):
                config = await service.load_config_from_env()
                
                assert config["app"]["debug"] is True
                assert config["database"]["url"] == "postgresql://test:5432/db"
                assert config["llm_provider"]["timeout_seconds"] == 45
                assert config["feature_flags"]["enable_auto_apply"] is True
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_environment_variable_override(self, config_service_config, sample_global_config):
        """Test environment variables override file configuration."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Mock environment variables that override config
            with patch.dict(os.environ, {'APP_DEBUG': 'true', 'LLM_TIMEOUT_SECONDS': '60'}):
                with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                    config = await service.load_config("global", apply_env_overrides=True)
                    
                    # Environment should override file values
                    assert config["app"]["debug"] is True  # Overridden from False
                    assert config["llm_provider"]["timeout_seconds"] == 60  # Overridden from 30
                    assert config["app"]["name"] == "TPM Job Finder"  # Not overridden
                    
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_environment_variable_type_conversion(self, config_service_config):
        """Test automatic type conversion for environment variables."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            with patch.dict(os.environ, {
                'BOOL_VALUE': 'true',
                'INT_VALUE': '42',
                'FLOAT_VALUE': '3.14',
                'LIST_VALUE': 'item1,item2,item3',
                'JSON_VALUE': '{"key": "value"}'
            }):
                result = await service.parse_env_variable('BOOL_VALUE', 'bool')
                assert result is True
                assert isinstance(result, bool)
                
                result = await service.parse_env_variable('INT_VALUE', 'int')
                assert result == 42
                assert isinstance(result, int)
                
                result = await service.parse_env_variable('FLOAT_VALUE', 'float')
                assert result == 3.14
                assert isinstance(result, float)
                
                result = await service.parse_env_variable('LIST_VALUE', 'list')
                assert result == ['item1', 'item2', 'item3']
                assert isinstance(result, list)
                
                result = await service.parse_env_variable('JSON_VALUE', 'json')
                assert result == {"key": "value"}
                assert isinstance(result, dict)
                
        finally:
            await service.stop()


class TestHierarchicalConfigurationManagement:
    """Test hierarchical configuration management capabilities."""
    
    @pytest.mark.asyncio
    async def test_get_nested_setting_with_dot_notation(self, config_service_config, sample_global_config):
        """Test getting nested configuration settings using dot notation."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Test dot notation access
                app_name = await service.get_setting("app.name")
                assert app_name == "TPM Job Finder"
                
                db_url = await service.get_setting("database.url")
                assert db_url == "sqlite:///jobs.db"
                
                primary_llm = await service.get_setting("llm_provider.primary")
                assert primary_llm == "openai"
                
                # Test with default value
                missing_value = await service.get_setting("missing.key", "default")
                assert missing_value == "default"
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_set_nested_setting_with_dot_notation(self, config_service_config, sample_global_config):
        """Test setting nested configuration values using dot notation."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Test setting values
                await service.set_setting("app.version", "2.0.0")
                await service.set_setting("database.pool_size", 20)
                await service.set_setting("new.nested.value", "test")
                
                # Verify values were set
                assert await service.get_setting("app.version") == "2.0.0"
                assert await service.get_setting("database.pool_size") == 20
                assert await service.get_setting("new.nested.value") == "test"
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_inheritance(self, config_service_config, sample_global_config, sample_environment_configs):
        """Test configuration inheritance between global and environment configs."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Load global config
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
            
            # Load development environment config
            dev_config = sample_environment_configs["development"]
            with patch('builtins.open', mock_open(read_data=json.dumps(dev_config))):
                merged_config = await service.load_config_with_inheritance("development", base_config="global")
                
                # Should inherit from global and override with environment-specific
                assert merged_config["app"]["name"] == "TPM Job Finder"  # From global
                assert merged_config["app"]["debug"] is True  # From dev environment
                assert merged_config["database"]["url"] == "sqlite:///dev.db"  # From dev environment
                assert merged_config["llm_provider"]["primary"] == "openai"  # From global
                assert merged_config["llm_provider"]["timeout_seconds"] == 60  # From dev environment
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_multi_level_configuration_merge(self, config_service_config):
        """Test merging configurations from multiple levels."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Test merging multiple configuration sources
            base_config = {"app": {"name": "Test", "debug": False}, "db": {"host": "localhost"}}
            env_config = {"app": {"debug": True}, "db": {"port": 5432}}
            user_config = {"app": {"theme": "dark"}, "new_setting": "value"}
            
            merged = await service.merge_configurations([base_config, env_config, user_config])
            
            # Should merge all levels
            assert merged["app"]["name"] == "Test"  # From base
            assert merged["app"]["debug"] is True  # From env (overrides base)
            assert merged["app"]["theme"] == "dark"  # From user
            assert merged["db"]["host"] == "localhost"  # From base
            assert merged["db"]["port"] == 5432  # From env
            assert merged["new_setting"] == "value"  # From user
            
        finally:
            await service.stop()


class TestConfigurationValidationAndSchema:
    """Test configuration validation and schema capabilities."""
    
    @pytest.mark.asyncio
    async def test_validate_configuration_schema(self, config_service_config):
        """Test configuration validation against schema."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Valid configuration
            valid_config = {
                "app": {"name": "Test App", "debug": True},
                "database": {"url": "sqlite:///test.db", "pool_size": 10},
                "llm_provider": {"timeout_seconds": 30, "max_retries": 3}
            }
            
            validation_result = await service.validate_config(valid_config, schema_name="global")
            
            assert validation_result.valid is True
            assert len(validation_result.errors) == 0
            assert len(validation_result.warnings) == 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_validate_invalid_configuration(self, config_service_config):
        """Test validation of invalid configuration."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Invalid configuration
            invalid_config = {
                "app": {"name": "", "debug": "not_boolean"},  # Invalid values
                "database": {"pool_size": -1},  # Invalid negative value
                "llm_provider": {"timeout_seconds": "invalid"}  # Invalid type
            }
            
            validation_result = await service.validate_config(invalid_config, schema_name="global")
            
            assert validation_result.valid is False
            assert len(validation_result.errors) > 0
            assert "app.name" in str(validation_result.errors)
            assert "app.debug" in str(validation_result.errors)
            assert "database.pool_size" in str(validation_result.errors)
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_type_validation(self, config_service_config):
        """Test configuration type validation."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Test various type validations
            type_tests = [
                {"value": "test_string", "expected_type": "string", "should_pass": True},
                {"value": 42, "expected_type": "integer", "should_pass": True},
                {"value": 3.14, "expected_type": "number", "should_pass": True},
                {"value": True, "expected_type": "boolean", "should_pass": True},
                {"value": ["a", "b"], "expected_type": "array", "should_pass": True},
                {"value": {"key": "value"}, "expected_type": "object", "should_pass": True},
                {"value": "not_number", "expected_type": "integer", "should_pass": False},
                {"value": 42, "expected_type": "string", "should_pass": False}
            ]
            
            for test in type_tests:
                result = await service.validate_type(test["value"], test["expected_type"])
                assert result == test["should_pass"]
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_constraint_validation(self, config_service_config):
        """Test configuration constraint validation."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Test constraint validations
            constraints = {
                "database.pool_size": {"min": 1, "max": 100},
                "llm_provider.timeout_seconds": {"min": 1, "max": 300},
                "app.name": {"min_length": 1, "max_length": 100}
            }
            
            # Valid values
            assert await service.validate_constraint(10, constraints["database.pool_size"]) is True
            assert await service.validate_constraint(30, constraints["llm_provider.timeout_seconds"]) is True
            assert await service.validate_constraint("Test App", constraints["app.name"]) is True
            
            # Invalid values
            assert await service.validate_constraint(0, constraints["database.pool_size"]) is False
            assert await service.validate_constraint(500, constraints["llm_provider.timeout_seconds"]) is False
            assert await service.validate_constraint("", constraints["app.name"]) is False
            
        finally:
            await service.stop()


class TestCredentialAndSecretManagement:
    """Test credential and secret management capabilities."""
    
    @pytest.mark.asyncio
    async def test_load_credentials_from_environment(self, config_service_config):
        """Test loading credentials from environment variables."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            with patch.dict(os.environ, {
                'OPENAI_API_KEY': 'sk-test-openai-key',
                'ANTHROPIC_API_KEY': 'sk-ant-test-key',
                'DATABASE_PASSWORD': 'secret_password'
            }):
                credentials = await service.get_credentials("openai")
                
                assert "api_key" in credentials
                assert credentials["api_key"] == "sk-test-openai-key"
                
                db_creds = await service.get_credentials("database")
                assert "password" in db_creds
                assert db_creds["password"] == "secret_password"
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_secure_credential_storage(self, config_service_config, sample_credentials):
        """Test secure credential storage and retrieval."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Store credentials securely
            for provider, creds in sample_credentials.items():
                result = await service.store_credentials(provider, creds)
                assert result.success is True
                assert result.encrypted is True  # Should be encrypted
            
            # Retrieve credentials
            openai_creds = await service.get_credentials("openai")
            assert openai_creds["api_key"] == "sk-test-openai-key"
            assert openai_creds["organization"] == "org-test"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_credential_rotation(self, config_service_config):
        """Test credential rotation functionality."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Initial credentials
            old_creds = {"api_key": "old-key", "secret": "old-secret"}
            await service.store_credentials("test_provider", old_creds)
            
            # Rotate credentials
            new_creds = {"api_key": "new-key", "secret": "new-secret"}
            rotation_result = await service.rotate_credentials("test_provider", new_creds)
            
            assert rotation_result.success is True
            assert rotation_result.old_credentials_backed_up is True
            assert rotation_result.new_credentials_active is True
            
            # Verify new credentials are active
            current_creds = await service.get_credentials("test_provider")
            assert current_creds["api_key"] == "new-key"
            assert current_creds["secret"] == "new-secret"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_credential_validation(self, config_service_config):
        """Test credential validation."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Valid credentials
            valid_creds = {
                "api_key": "sk-1234567890abcdef",
                "organization": "org-test"
            }
            validation = await service.validate_credentials("openai", valid_creds)
            assert validation.valid is True
            
            # Invalid credentials
            invalid_creds = {
                "api_key": "",  # Empty API key
                "invalid_field": "value"
            }
            validation = await service.validate_credentials("openai", invalid_creds)
            assert validation.valid is False
            assert len(validation.errors) > 0
            
        finally:
            await service.stop()


class TestHotReloadingAndDynamicUpdates:
    """Test hot reloading and dynamic update capabilities."""
    
    @pytest.mark.asyncio
    async def test_hot_reload_configuration_file(self, config_service_config, sample_global_config):
        """Test hot reloading configuration when file changes."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Initial load
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                initial_value = await service.get_setting("app.version")
                assert initial_value == "1.0.0"
            
            # Simulate file change
            updated_config = sample_global_config.copy()
            updated_config["app"]["version"] = "2.0.0"
            
            # Trigger hot reload
            with patch('builtins.open', mock_open(read_data=json.dumps(updated_config))):
                reload_result = await service.reload_config("global")
                
                assert reload_result.success is True
                assert reload_result.changes_detected is True
                assert "app.version" in reload_result.changed_keys
                
                # Verify value updated
                new_value = await service.get_setting("app.version")
                assert new_value == "2.0.0"
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_file_watcher_hot_reload(self, config_service_config):
        """Test automatic hot reload via file watcher."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Enable file watching
            await service.enable_file_watching("global")
            
            # Verify file watcher is active
            watcher_status = await service.get_file_watcher_status("global")
            assert watcher_status.active is True
            assert watcher_status.file_path is not None
            
            # Simulate file change notification
            change_event = {
                "file_path": "/config/global.json",
                "event_type": "modified",
                "timestamp": datetime.now(timezone.utc)
            }
            
            reload_triggered = await service.handle_file_change_event(change_event)
            assert reload_triggered is True
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_change_notifications(self, config_service_config):
        """Test configuration change notifications."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            notifications = []
            
            # Register change listener
            def change_listener(change_event):
                notifications.append(change_event)
            
            await service.register_change_listener("global", change_listener)
            
            # Make configuration change
            await service.set_setting("app.debug", True)
            
            # Verify notification was sent
            assert len(notifications) == 1
            assert notifications[0]["config_name"] == "global"
            assert notifications[0]["key"] == "app.debug"
            assert notifications[0]["new_value"] is True
            assert notifications[0]["change_type"] == "update"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_rollback_configuration_changes(self, config_service_config, sample_global_config):
        """Test rollback of configuration changes."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Load initial config
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Create checkpoint
                checkpoint_id = await service.create_checkpoint("global")
                assert checkpoint_id is not None
                
                # Make changes
                await service.set_setting("app.version", "2.0.0")
                await service.set_setting("app.debug", True)
                
                # Verify changes
                assert await service.get_setting("app.version") == "2.0.0"
                assert await service.get_setting("app.debug") is True
                
                # Rollback to checkpoint
                rollback_result = await service.rollback_to_checkpoint("global", checkpoint_id)
                
                assert rollback_result.success is True
                assert rollback_result.checkpoint_id == checkpoint_id
                assert len(rollback_result.restored_keys) == 2
                
                # Verify rollback
                assert await service.get_setting("app.version") == "1.0.0"
                assert await service.get_setting("app.debug") is False
                
        finally:
            await service.stop()


class TestFeatureFlagManagement:
    """Test feature flag management capabilities."""
    
    @pytest.mark.asyncio
    async def test_get_feature_flag_status(self, config_service_config, sample_global_config):
        """Test getting feature flag status."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Test feature flag access
                multi_resume_enabled = await service.is_feature_enabled("enable_multi_resume")
                assert multi_resume_enabled is True
                
                auto_apply_enabled = await service.is_feature_enabled("enable_auto_apply")
                assert auto_apply_enabled is False
                
                # Test non-existent flag (should default to False)
                unknown_flag = await service.is_feature_enabled("unknown_feature")
                assert unknown_flag is False
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_toggle_feature_flag(self, config_service_config, sample_global_config):
        """Test toggling feature flags."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Initial state
                assert await service.is_feature_enabled("enable_auto_apply") is False
                
                # Toggle feature flag
                toggle_result = await service.toggle_feature_flag("enable_auto_apply")
                
                assert toggle_result.success is True
                assert toggle_result.flag_name == "enable_auto_apply"
                assert toggle_result.previous_value is False
                assert toggle_result.new_value is True
                
                # Verify toggle
                assert await service.is_feature_enabled("enable_auto_apply") is True
                
                # Toggle back
                toggle_result = await service.toggle_feature_flag("enable_auto_apply")
                assert toggle_result.new_value is False
                assert await service.is_feature_enabled("enable_auto_apply") is False
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_feature_flag_with_conditions(self, config_service_config):
        """Test feature flags with conditional logic."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Set up conditional feature flag
            feature_config = {
                "enable_beta_features": {
                    "default": False,
                    "conditions": [
                        {"environment": "development", "value": True},
                        {"user_group": "beta_testers", "value": True}
                    ]
                }
            }
            
            await service.load_feature_flags(feature_config)
            
            # Test default value
            context = {"environment": "production", "user_group": "regular"}
            enabled = await service.is_feature_enabled("enable_beta_features", context)
            assert enabled is False
            
            # Test environment condition
            context = {"environment": "development", "user_group": "regular"}
            enabled = await service.is_feature_enabled("enable_beta_features", context)
            assert enabled is True
            
            # Test user group condition
            context = {"environment": "production", "user_group": "beta_testers"}
            enabled = await service.is_feature_enabled("enable_beta_features", context)
            assert enabled is True
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_feature_flag_analytics(self, config_service_config):
        """Test feature flag usage analytics."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Simulate feature flag usage
            await service.is_feature_enabled("feature_a")
            await service.is_feature_enabled("feature_a")
            await service.is_feature_enabled("feature_b")
            await service.is_feature_enabled("feature_a")
            
            # Get analytics
            analytics = await service.get_feature_flag_analytics()
            
            assert analytics["feature_a"]["check_count"] == 3
            assert analytics["feature_b"]["check_count"] == 1
            assert "last_checked" in analytics["feature_a"]
            assert "enabled_count" in analytics["feature_a"]
            
        finally:
            await service.stop()


class TestMultiEnvironmentSupport:
    """Test multi-environment configuration support."""
    
    @pytest.mark.asyncio
    async def test_load_environment_specific_config(self, config_service_config, sample_environment_configs):
        """Test loading environment-specific configuration."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Test development environment
            dev_config = sample_environment_configs["development"]
            with patch('builtins.open', mock_open(read_data=json.dumps(dev_config))):
                config = await service.load_environment_config("development")
                
                assert config["app"]["debug"] is True
                assert config["database"]["url"] == "sqlite:///dev.db"
                assert config["feature_flags"]["enable_debug_mode"] is True
            
            # Test production environment
            prod_config = sample_environment_configs["production"]
            with patch('builtins.open', mock_open(read_data=json.dumps(prod_config))):
                config = await service.load_environment_config("production")
                
                assert config["app"]["debug"] is False
                assert "postgresql" in config["database"]["url"]
                assert config["feature_flags"]["enable_debug_mode"] is False
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_environment_detection(self, config_service_config):
        """Test automatic environment detection."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Test explicit environment variable
            with patch.dict(os.environ, {'ENVIRONMENT': 'staging'}):
                env = await service.detect_environment()
                assert env == "staging"
            
            # Test NODE_ENV fallback
            with patch.dict(os.environ, {'NODE_ENV': 'production'}, clear=True):
                env = await service.detect_environment()
                assert env == "production"
            
            # Test default environment
            with patch.dict(os.environ, {}, clear=True):
                env = await service.detect_environment()
                assert env == "development"  # Default
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_environment_specific_overrides(self, config_service_config, sample_global_config, sample_environment_configs):
        """Test environment-specific configuration overrides."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Load base configuration
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
            
            # Apply environment overrides
            with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
                dev_overrides = sample_environment_configs["development"]
                with patch('builtins.open', mock_open(read_data=json.dumps(dev_overrides))):
                    final_config = await service.get_effective_config()
                    
                    # Base values should be preserved
                    assert final_config["app"]["name"] == "TPM Job Finder"
                    assert final_config["llm_provider"]["primary"] == "openai"
                    
                    # Environment overrides should be applied
                    assert final_config["app"]["debug"] is True
                    assert final_config["database"]["url"] == "sqlite:///dev.db"
                    assert final_config["llm_provider"]["timeout_seconds"] == 60
                    
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_environment_configuration_validation(self, config_service_config):
        """Test validation of environment-specific configurations."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            environments = ["development", "staging", "production"]
            
            for env in environments:
                validation = await service.validate_environment_config(env)
                
                # Should validate successfully for known environments
                assert validation.valid is True
                assert validation.environment == env
                assert len(validation.required_settings) > 0
                
            # Test invalid environment
            validation = await service.validate_environment_config("invalid_env")
            assert validation.valid is False
            assert len(validation.errors) > 0
            
        finally:
            await service.stop()


class TestConfigurationCachingAndPerformance:
    """Test configuration caching and performance capabilities."""
    
    @pytest.mark.asyncio
    async def test_configuration_caching(self, config_service_config, sample_global_config):
        """Test configuration caching functionality."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # First load should cache the configuration
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))) as mock_file:
                config1 = await service.load_config("global")
                initial_calls = mock_file.call_count
                
                # Second load should use cache
                config2 = await service.load_config("global")
                cached_calls = mock_file.call_count
                
                # File should not be read again
                assert cached_calls == initial_calls
                assert config1 == config2
                
                # Verify cache hit
                cache_stats = await service.get_cache_statistics()
                assert cache_stats["global"]["hits"] >= 1
                assert cache_stats["global"]["misses"] == 1
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, config_service_config, sample_global_config):
        """Test cache expiration functionality."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        # Set short cache TTL for testing
        config_service_config["cache_ttl_seconds"] = 1
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Load configuration
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Wait for cache expiration
                await asyncio.sleep(1.1)
                
                # Check cache status
                cache_info = await service.get_cache_info("global")
                assert cache_info.expired is True
                
                # Next load should bypass cache
                with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))) as mock_file:
                    await service.load_config("global")
                    assert mock_file.call_count > 0  # File was read again
                    
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, config_service_config, sample_global_config):
        """Test cache invalidation functionality."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Load and cache configuration
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Verify cached
                cache_info = await service.get_cache_info("global")
                assert cache_info.cached is True
                
                # Invalidate cache
                invalidation_result = await service.invalidate_cache("global")
                assert invalidation_result.success is True
                assert invalidation_result.config_name == "global"
                
                # Verify cache cleared
                cache_info = await service.get_cache_info("global")
                assert cache_info.cached is False
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, config_service_config, sample_global_config):
        """Test performance metrics collection."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Perform various operations
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                await service.get_setting("app.name")
                await service.set_setting("test.value", "test")
                await service.save_config("global", sample_global_config)
            
            # Get performance metrics
            metrics = await service.get_performance_metrics()
            
            assert "load_config" in metrics
            assert "get_setting" in metrics
            assert "set_setting" in metrics
            assert "save_config" in metrics
            
            # Each metric should have timing information
            for operation, metric in metrics.items():
                assert "total_calls" in metric
                assert "average_time_ms" in metric
                assert "total_time_ms" in metric
                assert metric["total_calls"] > 0
                
        finally:
            await service.stop()


class TestErrorHandlingAndResilience:
    """Test error handling and resilience capabilities."""
    
    @pytest.mark.asyncio
    async def test_handle_corrupted_configuration_file(self, config_service_config):
        """Test handling of corrupted configuration files."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Mock corrupted JSON file
            corrupted_data = '{"app": {"name": "Test", "debug": true, invalid_json}'
            
            with patch('builtins.open', mock_open(read_data=corrupted_data)):
                result = await service.load_config("global")
                
                # Should return default/empty config and log error
                assert result is not None
                assert isinstance(result, dict)
                
                # Check error was logged
                error_log = await service.get_error_log()
                assert len(error_log) > 0
                assert "JSON decode error" in str(error_log[-1])
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_handle_missing_configuration_file(self, config_service_config):
        """Test handling of missing configuration files."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Mock file not found
            with patch('builtins.open', side_effect=FileNotFoundError("Config file not found")):
                result = await service.load_config("missing_config")
                
                # Should return default config
                assert result is not None
                assert isinstance(result, dict)
                
                # Should create default file if configured
                if config_service_config.get("create_missing_configs", True):
                    file_created = await service.was_default_config_created("missing_config")
                    assert file_created is True
                    
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_backup_and_recovery(self, config_service_config, sample_global_config):
        """Test configuration backup and recovery."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Load initial configuration
            with patch('builtins.open', mock_open(read_data=json.dumps(sample_global_config))):
                await service.load_config("global")
                
                # Create backup
                backup_result = await service.create_backup("global")
                assert backup_result.success is True
                assert backup_result.backup_id is not None
                assert backup_result.backup_path is not None
                
                # Simulate configuration corruption
                corrupted_config = {"corrupted": True}
                await service.force_load_config("global", corrupted_config)
                
                # Verify corruption
                current_config = await service.get_current_config("global")
                assert current_config.get("corrupted") is True
                
                # Restore from backup
                restore_result = await service.restore_from_backup("global", backup_result.backup_id)
                assert restore_result.success is True
                
                # Verify restoration
                restored_config = await service.get_current_config("global")
                assert restored_config["app"]["name"] == "TPM Job Finder"
                assert "corrupted" not in restored_config
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_validation_recovery(self, config_service_config):
        """Test recovery from configuration validation failures."""
        from tpm_job_finder_poc.config_management_tdd.service import ConfigManagementServiceTDD
        
        service = ConfigManagementServiceTDD(config_service_config)
        await service.start()
        
        try:
            # Attempt to load invalid configuration
            invalid_config = {
                "app": {"debug": "not_boolean"},
                "database": {"pool_size": -1}
            }
            
            load_result = await service.load_config_with_validation("global", invalid_config)
            
            # Should fail validation but provide recovery options
            assert load_result.success is False
            assert load_result.validation_failed is True
            assert len(load_result.validation_errors) > 0
            assert load_result.recovery_options is not None
            
            # Test automatic recovery
            recovery_result = await service.apply_automatic_recovery("global", load_result.recovery_options)
            assert recovery_result.success is True
            assert recovery_result.errors_corrected > 0
            
            # Verify recovered configuration is valid
            recovered_config = await service.get_current_config("global")
            validation = await service.validate_config(recovered_config)
            assert validation.valid is True
            
        finally:
            await service.stop()