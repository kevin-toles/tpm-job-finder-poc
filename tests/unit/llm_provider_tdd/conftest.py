"""
Test configuration for LLM Provider TDD tests.

Provides shared fixtures and test configuration for the LLM Provider Service
TDD test suite.
"""

import pytest
import os
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# Import our contracts and models
from tpm_job_finder_poc.shared.contracts.llm_provider_service_tdd import (
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
    RequestPriority
)


@pytest.fixture
def sample_config():
    """Sample LLM provider configuration for testing."""
    return LLMProviderConfig(
        default_provider=ProviderType.OPENAI,
        max_retries=3,
        retry_delay_seconds=1.0,
        request_timeout_seconds=30,
        rate_limit_requests_per_minute=60,
        rate_limit_tokens_per_minute=10000,
        enable_fallback=True,
        enable_cost_tracking=True,
        enable_usage_analytics=True,
        openai_config={
            "api_key": "test-openai-key",
            "model": "gpt-4",
            "temperature": 0.1,
            "max_tokens": 2000
        },
        anthropic_config={
            "api_key": "test-anthropic-key", 
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.1
        },
        gemini_config={
            "api_key": "test-gemini-key",
            "model": "gemini-pro",
            "temperature": 0.1
        }
        # Note: deepseek_config and ollama_config intentionally omitted 
        # to test non-existent provider scenarios
    )


@pytest.fixture
def sample_request():
    """Sample LLM request for testing."""
    return LLMRequest(
        prompt="Analyze this job posting for a Technical Product Manager role",
        signal_type=SignalType.ANALYSIS,
        provider=ProviderType.OPENAI,
        temperature=0.7,
        max_tokens=1000,
        priority=RequestPriority.NORMAL,
        tags=["job_analysis", "tpm"],
        metadata={"test": True}
    )


@pytest.fixture
def sample_batch_requests():
    """Sample batch of LLM requests for testing."""
    return [
        LLMRequest(
            prompt=f"Analyze job posting {i}",
            signal_type=SignalType.ANALYSIS,
            provider=ProviderType.OPENAI,
            tags=[f"batch-{i}"]
        )
        for i in range(3)
    ]


@pytest.fixture
def sample_provider_info():
    """Sample provider information for testing."""
    return ProviderInfo(
        name="OpenAI",
        type=ProviderType.OPENAI,
        status=ProviderStatus.HEALTHY,
        models=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
        supported_signals=[SignalType.ANALYSIS, SignalType.SCORE, SignalType.CLASSIFICATION],
        max_tokens=8000,
        supports_streaming=True,
        supports_function_calling=True,
        rate_limit_rpm=60,
        rate_limit_tpm=10000,
        cost_per_input_token=0.00003,
        cost_per_output_token=0.00006,
        uptime_percentage=99.5,
        average_response_time=1.2,
        success_rate=0.995,
        last_success=datetime.now(timezone.utc),
        consecutive_failures=0,
        enabled=True,
        priority=1
    )


@pytest.fixture
def sample_response():
    """Sample LLM response for testing."""
    return LLMResponse(
        signals={
            "score": 0.85,
            "rationale": "Strong match for TPM role with relevant experience",
            "tags": ["technical", "product_management", "api_experience"],
            "confidence": 0.9,
            "skills_match": ["API design", "Product strategy", "Technical leadership"],
            "experience_level": "senior",
            "salary_range": "$150k-$200k"
        },
        raw_response="This job posting shows a strong match for a Technical Product Manager...",
        request_id="test-request-123",
        signal_type=SignalType.ANALYSIS,
        provider=ProviderType.OPENAI,
        model="gpt-4",
        provider_request_id="openai-req-456",
        tokens_used=150,
        prompt_tokens=80,
        completion_tokens=70,
        cost=0.005,
        processing_time=1.25,
        queue_time=0.05,
        provider_response_time=1.2,
        timestamp=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        confidence_score=0.9,
        quality_score=0.95
    )


@pytest.fixture
def sample_provider_health():
    """Sample provider health information for testing."""
    return ProviderHealth(
        provider=ProviderType.OPENAI,
        status=ProviderStatus.HEALTHY,
        response_time_ms=1200.0,
        last_check=datetime.now(timezone.utc),
        success_rate_1h=0.99,
        success_rate_24h=0.995,
        average_response_time_1h=1.1,
        rate_limit_status="normal"
    )


@pytest.fixture
def sample_statistics():
    """Sample service statistics for testing."""
    return LLMServiceStatistics(
        total_requests_processed=100,
        total_successful_requests=95,
        total_failed_requests=5,
        total_cached_responses=10,
        total_tokens_used=15000,
        total_prompt_tokens=8000,
        total_completion_tokens=7000,
        total_cost=0.45,
        cost_by_provider={
            "openai": 0.30,
            "anthropic": 0.15
        },
        average_response_time=1.25,
        average_queue_time=0.05,
        requests_per_minute=5.2,
        requests_by_provider={
            "openai": 60,
            "anthropic": 40
        },
        success_rate_by_provider={
            "openai": 0.95,
            "anthropic": 0.97
        },
        requests_by_signal_type={
            "analysis": 70,
            "score": 20,
            "classification": 10
        },
        first_request_time=datetime.now(timezone.utc),
        last_request_time=datetime.now(timezone.utc),
        uptime_seconds=3600.0
    )


@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider for testing."""
    mock = AsyncMock()
    mock.name = "OpenAI"
    mock.type = ProviderType.OPENAI
    mock.status = ProviderStatus.HEALTHY
    mock.models = ["gpt-4", "gpt-3.5-turbo"]
    mock.process_request = AsyncMock(return_value={
        "score": 0.85,
        "rationale": "Mock OpenAI response",
        "tags": ["mock", "openai"]
    })
    return mock


@pytest.fixture
def mock_anthropic_provider():
    """Mock Anthropic provider for testing."""
    mock = AsyncMock()
    mock.name = "Anthropic"
    mock.type = ProviderType.ANTHROPIC
    mock.status = ProviderStatus.HEALTHY
    mock.models = ["claude-3-sonnet", "claude-3-haiku"]
    mock.process_request = AsyncMock(return_value={
        "score": 0.80,
        "rationale": "Mock Anthropic response",
        "tags": ["mock", "anthropic"]
    })
    return mock


@pytest.fixture
def mock_llm_service():
    """Mock LLM service implementation for testing."""
    mock = Mock()
    mock.is_running = Mock(return_value=True)
    mock.start = AsyncMock()
    mock.stop = AsyncMock()
    mock.process_request = AsyncMock()
    mock.process_batch = AsyncMock()
    mock.get_providers = AsyncMock(return_value=[])
    mock.get_provider_info = AsyncMock()
    mock.enable_provider = AsyncMock(return_value=True)
    mock.disable_provider = AsyncMock(return_value=True)
    mock.test_provider = AsyncMock()
    mock.health_check = AsyncMock(return_value={"status": "healthy"})
    mock.get_provider_health = AsyncMock()
    mock.get_statistics = AsyncMock()
    mock.reset_statistics = AsyncMock(return_value=True)
    mock.get_usage_report = AsyncMock(return_value={})
    mock.get_configuration = AsyncMock()
    mock.update_configuration = AsyncMock(return_value=True)
    return mock


# Test utilities
class MockLLMProvider:
    """Mock implementation of a single LLM provider for testing."""
    
    def __init__(self, provider_type: ProviderType, name: str):
        self.type = provider_type
        self.name = name
        self.status = ProviderStatus.HEALTHY
        self.models = ["mock-model-1", "mock-model-2"]
        self.enabled = True
        
    async def process_request(self, request: LLMRequest) -> Dict[str, Any]:
        """Mock request processing."""
        return {
            "score": 0.8,
            "rationale": f"Mock response from {self.name}",
            "tags": ["mock", self.type.value],
            "confidence": 0.9
        }
    
    async def health_check(self) -> ProviderHealth:
        """Mock health check."""
        return ProviderHealth(
            provider=self.type,
            status=self.status,
            response_time_ms=1000.0
        )


class MockLLMProviderService:
    """Mock implementation of ILLMProviderService for testing."""
    
    def __init__(self):
        self.running = False
        self.providers = {
            ProviderType.OPENAI: MockLLMProvider(ProviderType.OPENAI, "OpenAI"),
            ProviderType.ANTHROPIC: MockLLMProvider(ProviderType.ANTHROPIC, "Anthropic")
        }
        self.statistics = LLMServiceStatistics()
        self.config = LLMProviderConfig()
        
    async def start(self):
        """Start the mock service."""
        self.running = True
        
    async def stop(self):
        """Stop the mock service."""
        self.running = False
        
    def is_running(self):
        """Check if service is running."""
        return self.running
        
    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """Mock request processing."""
        if not self.running:
            raise ServiceNotStartedError("Service not started")
            
        # Simulate processing
        await asyncio.sleep(0.01)
        
        return LLMResponse(
            signals={"score": 0.8, "rationale": "Mock response"},
            request_id=request.request_id,
            signal_type=request.signal_type,
            provider=request.provider or ProviderType.OPENAI,
            model="mock-model",
            processing_time=0.1
        )


# Environment setup
def pytest_configure(config):
    """Configure test environment."""
    # Ensure we don't accidentally hit real APIs during tests
    os.environ["LLM_TEST_MODE"] = "1"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    
    
def pytest_unconfigure(config):
    """Clean up test environment."""
    if "LLM_TEST_MODE" in os.environ:
        del os.environ["LLM_TEST_MODE"]