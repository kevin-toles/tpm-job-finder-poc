"""
LLM Provider Service TDD Contract - Enhanced interface definition.

This module defines the complete interface contract for the LLM Provider Service
following Test-Driven Development methodology. It provides comprehensive
models, interfaces, and error handling for multi-provider LLM operations.

Following established microservice patterns from scraping_service_tdd.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Protocol
from pydantic import BaseModel, Field, field_validator
import uuid


# Enums
class ProviderType(str, Enum):
    """Types of LLM providers supported by the service."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class ProviderStatus(str, Enum):
    """Provider health and availability status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RATE_LIMITED = "rate_limited"
    OFFLINE = "offline"
    AUTHENTICATING = "authenticating"


class SignalType(str, Enum):
    """Types of signals that can be extracted from LLM responses."""
    SCORE = "score"
    ANALYSIS = "analysis"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    GENERATION = "generation"
    REASONING = "reasoning"


class RequestPriority(str, Enum):
    """Priority levels for LLM requests."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Pydantic Models
class LLMProviderConfig(BaseModel):
    """Configuration for LLM Provider Service."""
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    # Provider Settings
    default_provider: ProviderType = ProviderType.OPENAI
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: float = Field(default=1.0, ge=0.1, le=60.0)
    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, le=1000)
    rate_limit_tokens_per_minute: int = Field(default=10000, ge=100, le=100000)
    
    # Provider Configuration
    openai_config: Dict[str, Any] = Field(default_factory=dict)
    anthropic_config: Dict[str, Any] = Field(default_factory=dict)
    gemini_config: Dict[str, Any] = Field(default_factory=dict)
    deepseek_config: Dict[str, Any] = Field(default_factory=dict)
    ollama_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Features
    enable_fallback: bool = True
    enable_cost_tracking: bool = True
    enable_usage_analytics: bool = True
    enable_caching: bool = False
    cache_ttl_seconds: int = Field(default=3600, ge=0, le=86400)
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0 or v > 10:
            raise ValueError("max_retries must be between 0 and 10")
        return v


class LLMRequest(BaseModel):
    """Request for LLM processing with comprehensive configuration."""
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    # Required fields
    prompt: str = Field(..., min_length=1, max_length=50000)
    signal_type: SignalType = SignalType.ANALYSIS
    
    # Provider selection
    provider: Optional[ProviderType] = None
    model: Optional[str] = None
    fallback_providers: List[ProviderType] = Field(default_factory=list)
    
    # Model parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8000)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    
    # Request metadata
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    priority: RequestPriority = RequestPriority.NORMAL
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing options
    stream: bool = False
    enable_logging: bool = True
    enable_caching: bool = False
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("prompt cannot be empty or whitespace only")
        return v.strip()
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v < 0.0 or v > 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v


class LLMResponse(BaseModel):
    """Response from LLM processing with comprehensive metadata."""
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    # Response data
    signals: Dict[str, Any]
    raw_response: Optional[str] = None
    
    # Request metadata
    request_id: str
    signal_type: SignalType
    
    # Provider information
    provider: ProviderType
    model: str
    provider_request_id: Optional[str] = None
    
    # Usage and cost tracking
    tokens_used: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost: Optional[float] = None
    
    # Performance metrics
    processing_time: float
    queue_time: Optional[float] = None
    provider_response_time: Optional[float] = None
    
    # Timestamps
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Quality and confidence
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Error information
    warnings: List[str] = Field(default_factory=list)
    provider_warnings: List[str] = Field(default_factory=list)


class ProviderInfo(BaseModel):
    """Comprehensive information about an LLM provider."""
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    # Basic information
    name: str = Field(..., min_length=1)
    type: ProviderType
    status: ProviderStatus
    
    # Capabilities
    models: List[str] = Field(default_factory=list)
    supported_signals: List[SignalType] = Field(default_factory=list)
    max_tokens: Optional[int] = None
    supports_streaming: bool = False
    supports_function_calling: bool = False
    
    # Performance and limits
    rate_limit_rpm: Optional[int] = None  # Requests per minute
    rate_limit_tpm: Optional[int] = None  # Tokens per minute
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None
    
    # Health metrics
    uptime_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    average_response_time: Optional[float] = None
    success_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Status tracking
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    
    # Configuration
    enabled: bool = True
    priority: int = Field(default=5, ge=1, le=10)  # Lower number = higher priority
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()


class LLMServiceStatistics(BaseModel):
    """Service-level statistics for LLM Provider Service."""
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    # Request statistics
    total_requests_processed: int = 0
    total_successful_requests: int = 0
    total_failed_requests: int = 0
    total_cached_responses: int = 0
    
    # Token usage
    total_tokens_used: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    
    # Cost tracking
    total_cost: float = 0.0
    cost_by_provider: Dict[str, float] = Field(default_factory=dict)
    
    # Performance metrics
    average_response_time: float = 0.0
    average_queue_time: float = 0.0
    requests_per_minute: float = 0.0
    
    # Provider statistics
    requests_by_provider: Dict[str, int] = Field(default_factory=dict)
    success_rate_by_provider: Dict[str, float] = Field(default_factory=dict)
    
    # Signal type statistics
    requests_by_signal_type: Dict[str, int] = Field(default_factory=dict)
    
    # Time tracking
    first_request_time: Optional[datetime] = None
    last_request_time: Optional[datetime] = None
    uptime_seconds: float = 0.0


class ProviderHealth(BaseModel):
    """Health status information for a provider."""
    model_config = {"extra": "forbid", "validate_assignment": True}
    
    provider: ProviderType
    status: ProviderStatus
    response_time_ms: Optional[float] = None
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    
    # Health metrics
    success_rate_1h: Optional[float] = None
    success_rate_24h: Optional[float] = None
    average_response_time_1h: Optional[float] = None
    rate_limit_status: Optional[str] = None


# Custom Exceptions
class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    def __init__(self, message: str, provider: Optional[ProviderType] = None, 
                 request_id: Optional[str] = None):
        super().__init__(message)
        self.provider = provider
        self.request_id = request_id


class ServiceNotStartedError(LLMProviderError):
    """Raised when service operations are attempted before service is started."""
    pass


class ProviderNotFoundError(LLMProviderError):
    """Raised when a specified provider is not found or configured."""
    pass


class ProviderUnavailableError(LLMProviderError):
    """Raised when a provider is temporarily unavailable."""
    pass


class RateLimitExceededError(LLMProviderError):
    """Raised when rate limits are exceeded."""
    pass


class InvalidRequestError(LLMProviderError):
    """Raised when request parameters are invalid."""
    pass


class AuthenticationError(LLMProviderError):
    """Raised when authentication with a provider fails."""
    pass


class ConfigurationError(LLMProviderError):
    """Raised when service configuration is invalid."""
    pass


class LLMTimeoutError(LLMProviderError):
    """Raised when LLM request times out."""
    pass


class ModelNotFoundError(LLMProviderError):
    """Raised when requested model is not available."""
    pass


# Service Interface
class ILLMProviderService(ABC):
    """
    Abstract interface for LLM Provider Service operations.
    
    This interface defines the complete contract for LLM provider service
    operations including request processing, provider management, health
    monitoring, and statistics tracking.
    """
    
    # Core LLM Operations
    @abstractmethod
    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """
        Process an LLM request and return structured signals.
        
        Args:
            request: LLM processing request with configuration
            
        Returns:
            LLMResponse with structured signals and metadata
            
        Raises:
            InvalidRequestError: If request parameters are invalid
            ProviderUnavailableError: If no providers are available
            RateLimitExceededError: If rate limits are exceeded
            AuthenticationError: If authentication fails
            LLMTimeoutError: If request times out
            ServiceNotStartedError: If service is not started
        """
        pass
    
    @abstractmethod
    async def process_batch(self, requests: List[LLMRequest]) -> List[LLMResponse]:
        """
        Process multiple LLM requests in batch.
        
        Args:
            requests: List of LLM requests to process
            
        Returns:
            List of LLMResponse objects in same order as requests
        """
        pass
    
    # Provider Management
    @abstractmethod
    async def get_providers(self) -> List[ProviderInfo]:
        """Get information about all configured providers."""
        pass
    
    @abstractmethod
    async def get_provider_info(self, provider: ProviderType) -> ProviderInfo:
        """Get detailed information about a specific provider."""
        pass
    
    @abstractmethod
    async def enable_provider(self, provider: ProviderType) -> bool:
        """Enable a specific provider."""
        pass
    
    @abstractmethod
    async def disable_provider(self, provider: ProviderType) -> bool:
        """Disable a specific provider."""
        pass
    
    @abstractmethod
    async def test_provider(self, provider: ProviderType) -> ProviderHealth:
        """Test connectivity and health of a specific provider."""
        pass
    
    # Health and Monitoring
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive service health check."""
        pass
    
    @abstractmethod
    async def get_provider_health(self, provider: Optional[ProviderType] = None) -> Union[ProviderHealth, List[ProviderHealth]]:
        """Get health status for one or all providers."""
        pass
    
    # Statistics and Analytics
    @abstractmethod
    async def get_statistics(self) -> LLMServiceStatistics:
        """Get comprehensive service statistics."""
        pass
    
    @abstractmethod
    async def reset_statistics(self) -> bool:
        """Reset service statistics."""
        pass
    
    @abstractmethod
    async def get_usage_report(self, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              provider: Optional[ProviderType] = None) -> Dict[str, Any]:
        """Get detailed usage report for specified period."""
        pass
    
    # Service Lifecycle
    @abstractmethod
    async def start(self) -> None:
        """Start the LLM provider service."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the LLM provider service."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if service is currently running."""
        pass
    
    # Configuration Management
    @abstractmethod
    async def get_configuration(self) -> LLMProviderConfig:
        """Get current service configuration."""
        pass
    
    @abstractmethod
    async def update_configuration(self, config: LLMProviderConfig) -> bool:
        """Update service configuration."""
        pass


# Storage Interface (for future implementation)
class ILLMProviderStorage(Protocol):
    """Interface for LLM provider storage operations."""
    
    async def store_request(self, request: LLMRequest, response: LLMResponse) -> None:
        """Store LLM request and response for analytics."""
        ...
    
    async def get_usage_stats(self, 
                            provider: Optional[ProviderType] = None,
                            days: int = 30) -> Dict[str, Any]:
        """Get usage statistics from storage."""
        ...
    
    async def get_cached_response(self, request_hash: str) -> Optional[LLMResponse]:
        """Get cached response if available."""
        ...
    
    async def store_cached_response(self, request_hash: str, response: LLMResponse) -> None:
        """Store response in cache."""
        ...