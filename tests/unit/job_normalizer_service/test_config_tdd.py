"""TDD Test Suite for Job Normalizer Service Configuration

Tests for configuration management, validation, and behavior modification.
"""

import pytest
from pydantic import ValidationError

from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig
from tpm_job_finder_poc.shared.contracts.job_normalizer_service import JobNormalizationConfig


class TestJobNormalizerServiceConfig:
    """Test service configuration class."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        # Act
        config = JobNormalizerServiceConfig()
        
        # Assert
        assert config.enable_deduplication is True
        assert config.enable_field_normalization is True
        assert config.enable_statistics is True
        assert config.max_batch_size == 1000
        assert config.processing_timeout_seconds == 300
        assert config.duplicate_detection_similarity_threshold == 0.8
        assert config.normalize_titles is True
        assert config.normalize_salaries is True
        assert config.normalize_locations is True
        assert config.preserve_original_data is True
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        # Act
        config = JobNormalizerServiceConfig(
            enable_deduplication=False,
            enable_field_normalization=False,
            max_batch_size=500,
            processing_timeout_seconds=60,
            duplicate_detection_similarity_threshold=0.9,
            normalize_titles=False
        )
        
        # Assert
        assert config.enable_deduplication is False
        assert config.enable_field_normalization is False
        assert config.max_batch_size == 500
        assert config.processing_timeout_seconds == 60
        assert config.duplicate_detection_similarity_threshold == 0.9
        assert config.normalize_titles is False
        # Other fields should remain default
        assert config.enable_statistics is True
        assert config.normalize_salaries is True
    
    def test_invalid_configuration_values(self):
        """Test that invalid configuration values raise errors."""
        # Test negative max_batch_size
        with pytest.raises(ValidationError):
            JobNormalizerServiceConfig(max_batch_size=-1)
        
        # Test zero max_batch_size
        with pytest.raises(ValidationError):
            JobNormalizerServiceConfig(max_batch_size=0)
        
        # Test negative timeout
        with pytest.raises(ValidationError):
            JobNormalizerServiceConfig(processing_timeout_seconds=-1)
        
        # Test invalid similarity threshold (< 0)
        with pytest.raises(ValidationError):
            JobNormalizerServiceConfig(duplicate_detection_similarity_threshold=-0.1)
        
        # Test invalid similarity threshold (> 1)
        with pytest.raises(ValidationError):
            JobNormalizerServiceConfig(duplicate_detection_similarity_threshold=1.1)
    
    def test_configuration_dict_conversion(self):
        """Test configuration can be converted to/from dict."""
        # Arrange
        config = JobNormalizerServiceConfig(
            enable_deduplication=False,
            max_batch_size=250
        )
        
        # Act
        config_dict = config.model_dump()
        reconstructed_config = JobNormalizerServiceConfig(**config_dict)
        
        # Assert
        assert reconstructed_config.enable_deduplication == config.enable_deduplication
        assert reconstructed_config.max_batch_size == config.max_batch_size
        assert reconstructed_config == config


class TestJobNormalizationConfig:
    """Test operation-level configuration class."""
    
    def test_default_operation_configuration(self):
        """Test default operation configuration values."""
        # Act
        config = JobNormalizationConfig()
        
        # Assert
        assert config.enable_deduplication is True
        assert config.enable_field_normalization is True
        assert config.preserve_original_data is True
        assert config.normalize_titles is True
        assert config.normalize_salaries is True
        assert config.normalize_locations is True
        assert config.duplicate_detection_method == "fuzzy"
        assert config.similarity_threshold == 0.8
    
    def test_custom_operation_configuration(self):
        """Test custom operation configuration values."""
        # Act
        config = JobNormalizationConfig(
            enable_deduplication=False,
            normalize_titles=False,
            duplicate_detection_method="exact",
            similarity_threshold=0.95
        )
        
        # Assert
        assert config.enable_deduplication is False
        assert config.normalize_titles is False
        assert config.duplicate_detection_method == "exact"
        assert config.similarity_threshold == 0.95
        # Other fields should remain default
        assert config.enable_field_normalization is True
        assert config.normalize_salaries is True
    
    def test_invalid_operation_configuration(self):
        """Test that invalid operation configuration values raise errors."""
        # Test invalid duplicate detection method
        with pytest.raises(ValidationError):
            JobNormalizationConfig(duplicate_detection_method="invalid_method")
        
        # Test invalid similarity threshold
        with pytest.raises(ValidationError):
            JobNormalizationConfig(similarity_threshold=1.5)
        
        with pytest.raises(ValidationError):
            JobNormalizationConfig(similarity_threshold=-0.1)
    
    def test_operation_config_inheritance_behavior(self):
        """Test how operation config inherits from service config."""
        # This test will verify that operation config properly overrides
        # service config values when provided
        pass  # Will be implemented during GREEN phase


class TestConfigurationIntegration:
    """Test configuration integration with service behavior."""
    
    def test_configuration_affects_service_behavior(self):
        """Test that configuration changes actually affect service behavior."""
        # This test will be implemented during GREEN phase to ensure
        # configuration actually modifies service behavior
        pass
    
    def test_runtime_configuration_updates(self):
        """Test updating configuration at runtime."""
        # This test will verify if configuration can be updated
        # after service initialization
        pass