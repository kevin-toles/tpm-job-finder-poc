"""
LLM Provider Service Implementation
Manages LLM providers and request processing following contract interface
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ..shared.contracts.llm_provider_service import (
    ILLMProviderService, 
    LLMRequest, 
    LLMResponse, 
    ProviderInfo,
    ProviderType,
    ProviderStatus,
    LLMProviderError,
    ProviderUnavailableError,
    InvalidRequestError,
    RateLimitExceededError
)

logger = logging.getLogger(__name__)


class LLMProviderService(ILLMProviderService):
    """
    LLM Provider Service implementation
    Minimal implementation to pass TDD tests
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self._providers: Dict[ProviderType, ProviderInfo] = {}
        self._request_counts: Dict[ProviderType, int] = {}
        self._is_healthy = True
        
        # Initialize default providers based on config
        self._setup_default_providers()
    
    def _setup_default_providers(self):
        """Set up default providers for testing and basic functionality"""
        # Set up OpenAI provider
        openai_provider = ProviderInfo(
            name="openai",
            type=ProviderType.OPENAI,
            status=ProviderStatus.HEALTHY,
            models=["gpt-4", "gpt-3.5-turbo"]
        )
        self._providers[ProviderType.OPENAI] = openai_provider
        self._request_counts[ProviderType.OPENAI] = 0
        
        # Set up Anthropic provider
        anthropic_provider = ProviderInfo(
            name="anthropic",
            type=ProviderType.ANTHROPIC,
            status=ProviderStatus.HEALTHY,
            models=["claude-3", "claude-2"]
        )
        self._providers[ProviderType.ANTHROPIC] = anthropic_provider
        self._request_counts[ProviderType.ANTHROPIC] = 0
    
    @property
    def providers(self):
        """Get providers dictionary for backward compatibility"""
        return self._providers
    
    async def get_signals(self, request: LLMRequest) -> LLMResponse:
        """Get structured signals from LLM provider with validation and error handling"""
        # Validation
        if not request.prompt.strip():
            raise InvalidRequestError("Prompt cannot be empty")
        
        if request.max_tokens and request.max_tokens <= 0:
            raise InvalidRequestError("max_tokens must be positive")
        
        if request.temperature and (request.temperature < 0 or request.temperature > 2):
            raise InvalidRequestError("temperature must be between 0 and 2")
        
        # Provider check
        provider_type = request.provider or ProviderType.OPENAI  # Default provider
        if provider_type not in self._providers:
            raise ProviderUnavailableError(f"Provider '{provider_type.value}' not found")
        
        provider = self._providers[provider_type]
        if provider.status != ProviderStatus.HEALTHY:
            raise ProviderUnavailableError(f"Provider '{provider_type.value}' is not available")
        
        # Rate limiting simulation
        current_count = self._request_counts.get(provider_type, 0)
        if current_count >= 10:  # Simple rate limit
            raise RateLimitExceededError("Rate limit exceeded for provider")
        
        # Update request count
        self._request_counts[provider_type] = current_count + 1
        
        # Simulate LLM processing
        await asyncio.sleep(0.1)  # Minimal delay
        
        # Generate mock structured signals using internal provider call
        try:
            signals = await self._call_provider(request, provider)
        except Exception as e:
            error_msg = str(e)
            if "offline" in error_msg.lower() or "unavailable" in error_msg.lower():
                raise ProviderUnavailableError(f"Provider '{provider_type.value}' is unavailable: {error_msg}")
            elif "rate limit" in error_msg.lower():
                raise RateLimitExceededError(f"Rate limit exceeded for provider '{provider_type.value}': {error_msg}")
            else:
                raise ProviderUnavailableError(f"Provider error: {error_msg}")
        
        return LLMResponse(
            signals=signals,
            provider=provider_type,
            model=request.model or (provider.models[0] if provider.models else "default-model"),
            tokens_used=len(request.prompt.split()) + 10,
            cost=0.001,
            processing_time=0.1
        )
    
    async def _call_provider(self, request: LLMRequest, provider: ProviderInfo) -> Dict[str, Any]:
        """Internal method to call the actual provider (mockable for testing)"""
        # Default mock implementation
        return {
            'score': 0.85,
            'rationale': f'Analyzed prompt: {request.prompt[:50]}...',
            'tags': ['analyzed', 'mock'],
            'confidence': 0.9
        }
    
    async def get_providers(self) -> List[ProviderInfo]:
        """Get list of available providers"""
        return list(self._providers.values())
    
    async def add_provider(self, provider: ProviderInfo) -> bool:
        """Add new provider"""
        if not provider.name.strip():
            return False
        
        self._providers[provider.type] = provider
        self._request_counts[provider.type] = 0
        logger.info(f"Added provider: {provider.name}")
        return True
    
    async def remove_provider(self, provider_type: ProviderType) -> bool:
        """Remove provider"""
        if provider_type in self._providers:
            del self._providers[provider_type]
            if provider_type in self._request_counts:
                del self._request_counts[provider_type]
            logger.info(f"Removed provider: {provider_type.value}")
            return True
        return False
    
    async def get_provider_status(self, provider: ProviderType) -> ProviderInfo:
        """Get status of specific provider"""
        if provider not in self._providers:
            raise ProviderUnavailableError(f"Provider '{provider.value}' not found")
        return self._providers[provider]
    
    async def health_check(self) -> Dict[str, any]:
        """Health check for service"""
        provider_count = len(self._providers)
        available_providers = sum(1 for p in self._providers.values() if p.status == ProviderStatus.HEALTHY)
        
        return {
            "status": "healthy" if self._is_healthy else "unhealthy",
            "providers_total": provider_count,
            "providers_available": available_providers,
            "providers": {provider_type.value: provider.status.value 
                         for provider_type, provider in self._providers.items()},
            "service_name": "llm_provider",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def reset_rate_limits(self) -> bool:
        """Reset rate limits for all providers"""
        self._request_counts.clear()
        logger.info("Rate limits reset for all providers")
        return True
    
    def _set_health_status(self, healthy: bool):
        """Internal method to set health status for testing"""
        self._is_healthy = healthy