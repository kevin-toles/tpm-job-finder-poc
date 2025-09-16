"""
LLM Provider Service Contract - Interface definition.

Defines the interface for LLM provider service operations including
provider management, signal extraction, and health monitoring.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Protocol
import asyncio


class ProviderType(Enum):
    """Types of LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class ProviderStatus(Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RATE_LIMITED = "rate_limited"


@dataclass
class LLMRequest:
    """Request for LLM processing."""
    prompt: str
    provider: Optional[ProviderType] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    model: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "prompt": self.prompt,
            "provider": self.provider.value if self.provider else None,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model": self.model
        }


@dataclass
class LLMResponse:
    """Response from LLM processing."""
    signals: Dict[str, Any]
    provider: ProviderType
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "signals": self.signals,
            "provider": self.provider.value,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class ProviderInfo:
    """Information about an LLM provider."""
    name: str
    type: ProviderType
    status: ProviderStatus
    models: List[str]
    rate_limit: Optional[int] = None
    cost_per_token: Optional[float] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "models": self.models,
            "rate_limit": self.rate_limit,
            "cost_per_token": self.cost_per_token,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error
        }


# Exception classes
class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class ProviderUnavailableError(LLMProviderError):
    """Raised when a provider is unavailable."""
    pass


class RateLimitExceededError(LLMProviderError):
    """Raised when rate limits are exceeded."""
    pass


class InvalidRequestError(LLMProviderError):
    """Raised when request is invalid."""
    pass


class AuthenticationError(LLMProviderError):
    """Raised when authentication fails."""
    pass


# Service interface
class ILLMProviderService(Protocol):
    """Interface for LLM provider service operations."""
    
    async def get_signals(self, request: LLMRequest) -> LLMResponse:
        """
        Get structured signals from LLM provider.
        
        Args:
            request: LLM processing request
            
        Returns:
            LLMResponse with structured signals
            
        Raises:
            InvalidRequestError: If request is invalid
            ProviderUnavailableError: If provider is unavailable
            RateLimitExceededError: If rate limit exceeded
            AuthenticationError: If authentication fails
        """
        ...
    
    async def get_providers(self) -> List[ProviderInfo]:
        """
        Get information about all configured providers.
        
        Returns:
            List of provider information
        """
        ...
    
    async def get_provider_status(self, provider: ProviderType) -> ProviderInfo:
        """
        Get status of a specific provider.
        
        Args:
            provider: Provider type to check
            
        Returns:
            Provider information and status
            
        Raises:
            ProviderUnavailableError: If provider not found
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform service health check.
        
        Returns:
            Health status information
        """
        ...


# Storage interface
class ILLMProviderStorage(Protocol):
    """Interface for LLM provider storage operations."""
    
    async def store_request(self, request: LLMRequest, response: LLMResponse) -> None:
        """Store LLM request and response."""
        ...
    
    async def get_usage_stats(self, 
                            provider: Optional[ProviderType] = None,
                            days: int = 30) -> Dict[str, Any]:
        """Get usage statistics."""
        ...