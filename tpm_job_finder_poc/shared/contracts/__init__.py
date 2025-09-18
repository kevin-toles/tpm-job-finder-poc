"""
Shared Contracts Package

This package contains interface contracts and shared models for all microservices
in the TPM Job Finder POC application. These contracts define the boundaries
between services and ensure consistent APIs across the system.
"""

# Version information for contracts
__version__ = "1.0.0"

# Import all contracts for easy access
from .scraping_service import (
    IScrapingService,
    ScrapingConfig,
    ScrapingQuery,
    ScrapingResult,
    ScrapingStatistics,
    SourceHealth,
    ServiceNotStartedError,
    SourceNotFoundError,
    ScrapingTimeoutError,
    ServiceError,
    ConfigurationError
)

from .llm_provider_service_tdd import (
    ILLMProviderService,
    LLMProviderConfig,
    LLMRequest,
    LLMResponse,
    ProviderInfo,
    ProviderHealth,
    LLMServiceStatistics,
    ProviderType,
    ProviderStatus,
    SignalType,
    RequestPriority,
    LLMProviderError,
    ServiceNotStartedError as LLMServiceNotStartedError,
    ProviderNotFoundError,
    ProviderUnavailableError,
    RateLimitExceededError,
    InvalidRequestError,
    AuthenticationError,
    ConfigurationError as LLMConfigurationError,
    LLMTimeoutError,
    ModelNotFoundError
)

__all__ = [
    # Scraping Service
    "IScrapingService",
    "ScrapingConfig",
    "ScrapingQuery", 
    "ScrapingResult",
    "ScrapingStatistics",
    "SourceHealth",
    "ServiceNotStartedError",
    "SourceNotFoundError",
    "ScrapingTimeoutError",
    "ServiceError",
    "ConfigurationError",
    
    # LLM Provider Service
    "ILLMProviderService",
    "LLMProviderConfig",
    "LLMRequest",
    "LLMResponse",
    "ProviderInfo",
    "ProviderHealth", 
    "LLMServiceStatistics",
    "ProviderType",
    "ProviderStatus",
    "SignalType",
    "RequestPriority",
    "LLMProviderError",
    "LLMServiceNotStartedError",
    "ProviderNotFoundError",
    "ProviderUnavailableError",
    "RateLimitExceededError",
    "InvalidRequestError",
    "AuthenticationError",
    "LLMConfigurationError",
    "LLMTimeoutError",
    "ModelNotFoundError"
]