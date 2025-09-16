# LLM Provider Component

The LLM Provider is a sophisticated abstraction layer that provides unified access to multiple Large Language Model providers for job-related AI tasks including scoring, analysis, parsing, and enrichment. It enables seamless multi-provider LLM integration with automatic fallback, error handling, and configuration management.

## Architecture Overview

The llm_provider follows an adapter pattern with clean separation between the orchestration layer and individual provider implementations:

```
llm_provider/
├── adapter.py                  # Main LLM adapter with provider orchestration
├── base.py                     # Abstract base class and common interface
├── openai_provider.py          # OpenAI GPT integration (GPT-3.5/GPT-4)
├── anthropic_provider.py       # Anthropic Claude integration
├── gemini_provider.py          # Google Gemini integration
├── deepseek_provider.py        # DeepSeek model integration
├── ollama_provider.py          # Local Ollama integration
├── health.py                   # Provider health monitoring and diagnostics
├── requirements.txt            # Component dependencies
└── Dockerfile                  # Containerization config
```

## Core Components

### 1. LLMAdapter (adapter.py)
**Purpose**: Main orchestration service coordinating multiple LLM providers
- **Auto-discovery**: Automatically detects available providers based on API keys
- **Multi-provider scoring**: Parallel execution across multiple LLM providers
- **Error handling**: Graceful degradation when individual providers fail
- **Configuration management**: Environment-based provider configuration
- **Result aggregation**: Combines responses from multiple providers

### 2. LLMProvider Base Class (base.py)
**Purpose**: Abstract interface ensuring consistent provider implementations
- **Standardized interface**: Common `get_signals()` method for all providers
- **API key management**: Secure credential handling pattern
- **Type safety**: Strong typing for provider responses
- **Extensibility**: Easy addition of new LLM providers

### 3. Provider Implementations
**Purpose**: Individual LLM service integrations with provider-specific optimizations

#### OpenAI Provider (openai_provider.py)
- **Models**: GPT-3.5-turbo, GPT-4 support
- **Features**: Chat completions API, configurable parameters
- **Error handling**: Rate limiting, quota management
- **Configuration**: Temperature, max tokens, timeout settings

#### Anthropic Provider (anthropic_provider.py)
- **Models**: Claude-3 Sonnet and other Claude variants
- **Features**: Messages API integration, advanced reasoning
- **Safety**: Built-in safety settings and content filtering
- **Configuration**: Anthropic-specific parameters and versioning

#### Gemini Provider (gemini_provider.py)
- **Models**: Gemini Pro and other Google AI models
- **Features**: Generative Language API integration
- **Capabilities**: Multi-modal support for advanced analysis
- **Configuration**: Safety settings, candidate count management

#### DeepSeek Provider (deepseek_provider.py)
- **Models**: DeepSeek Chat and reasoning models
- **Features**: Cost-effective alternative for high-volume processing
- **Performance**: Optimized for speed and efficiency
- **Configuration**: Custom endpoint and parameter management

#### Ollama Provider (ollama_provider.py)
- **Models**: Local LLM deployment support
- **Features**: Privacy-conscious local processing
- **Flexibility**: Support for various open-source models
- **Configuration**: Local endpoint management

### 4. Health Monitoring (health.py)
**Purpose**: Real-time provider availability and performance tracking
- **Provider status**: Live availability checks for all providers
- **Performance metrics**: Response time and success rate tracking
- **Error monitoring**: Provider-specific error analysis
- **Alerting**: Configurable alerts for provider failures

## Public API

### LLMAdapter

```python
from tpm_job_finder_poc.llm_provider.adapter import LLMAdapter

class LLMAdapter:
    def __init__(self)
    
    def score_job(self, prompt: str) -> Dict[str, Any]
    
    def _load_providers(self) -> List[LLMProvider]
```

### LLMProvider (Base Class)

```python
from tpm_job_finder_poc.llm_provider.base import LLMProvider

class LLMProvider(abc.ABC):
    def __init__(self, api_key: Optional[str] = None)
    
    @abc.abstractmethod
    def get_signals(self, prompt: str) -> Dict[str, Any]
```

### Individual Providers

```python
# OpenAI Provider
from tpm_job_finder_poc.llm_provider.openai_provider import OpenAIProvider

class OpenAIProvider(LLMProvider):
    def get_signals(self, prompt: str) -> Dict[str, Any]

# Anthropic Provider
from tpm_job_finder_poc.llm_provider.anthropic_provider import AnthropicProvider

class AnthropicProvider(LLMProvider):
    def get_signals(self, prompt: str) -> Dict[str, Any]

# Similar pattern for Gemini, DeepSeek, and Ollama providers
```

## Configuration

### Environment Variables (Recommended)
```bash
# Core provider API keys
export OPENAI_API_KEY="sk-xxxxxx"
export ANTHROPIC_API_KEY="sk-ant-xxxxxx"
export GOOGLE_API_KEY="your-gemini-key"
export DEEPSEEK_API_KEY="your-deepseek-key"

# Local LLM configuration
export OLLAMA_ENABLED="true"
export OLLAMA_API_KEY=""  # Leave blank for local deployment

# Provider-specific settings
export OPENAI_MODEL="gpt-4"
export ANTHROPIC_MODEL="claude-3-sonnet-20240229"
export GEMINI_MODEL="gemini-pro"
```

### Configuration File (Alternative)
Create `llm_keys.txt` in project root:
```
OPENAI_API_KEY=sk-xxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxx
GOOGLE_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key
OLLAMA_ENABLED=true
```

### Provider-Specific Configuration
```python
# Provider configurations
PROVIDER_CONFIG = {
    'openai': {
        'model': 'gpt-4',
        'temperature': 0.1,
        'max_tokens': 2000,
        'timeout': 30
    },
    'anthropic': {
        'model': 'claude-3-sonnet-20240229',
        'max_tokens': 4000,
        'temperature': 0.1,
        'anthropic_version': '2023-06-01'
    },
    'gemini': {
        'model': 'gemini-pro',
        'temperature': 0.1,
        'safety_settings': 'block_few',
        'candidate_count': 1
    },
    'deepseek': {
        'model': 'deepseek-chat',
        'temperature': 0.1,
        'max_tokens': 1024
    },
    'ollama': {
        'model': 'llama2',
        'temperature': 0.1,
        'base_url': 'http://localhost:11434'
    }
}
```

## Usage Examples

### 1. Basic Multi-Provider Scoring
```python
from tpm_job_finder_poc.llm_provider.adapter import LLMAdapter

# Initialize adapter (auto-discovers available providers)
adapter = LLMAdapter()

# Score a job posting across all providers
job_prompt = """
Analyze this job posting for a Technical Product Manager role:

Title: Senior Technical Product Manager
Company: Tech Startup
Location: San Francisco, Remote OK
Salary: $150k-$200k

Requirements:
- 5+ years product management experience
- Technical background in software engineering
- Experience with API products
- Strong analytical and communication skills

Rate this job on a scale of 1-10 for fit with a TPM profile.
Provide rationale for the score.
"""

results = adapter.score_job(job_prompt)

# Results contain responses from all available providers
for provider_name, response in results.items():
    if 'error' in response:
        print(f"{provider_name}: Error - {response['error']}")
    else:
        print(f"{provider_name}: {response['response']}")
```

### 2. Provider-Specific Usage
```python
from tpm_job_finder_poc.llm_provider.openai_provider import OpenAIProvider
from tpm_job_finder_poc.llm_provider.anthropic_provider import AnthropicProvider

# Use specific provider
openai_provider = OpenAIProvider(api_key="your-openai-key")
result = openai_provider.get_signals(job_prompt)

# Fallback pattern
providers = [
    OpenAIProvider(api_key="openai-key"),
    AnthropicProvider(api_key="anthropic-key")
]

for provider in providers:
    result = provider.get_signals(job_prompt)
    if 'error' not in result:
        print(f"Success with {provider.__class__.__name__}: {result}")
        break
    else:
        print(f"Failed with {provider.__class__.__name__}: {result['error']}")
```

### 3. Integration with Job Enrichment
```python
from tpm_job_finder_poc.llm_provider.adapter import LLMAdapter
from tpm_job_finder_poc.enrichment.orchestrators.multi_resume_intelligence_orchestrator import MultiResumeIntelligenceOrchestrator

async def enrich_jobs_with_llm_analysis(jobs):
    """Enrich job postings with multi-provider LLM analysis."""
    llm_adapter = LLMAdapter()
    enriched_jobs = []
    
    for job in jobs:
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze this job posting for key insights:
        
        Title: {job.get('title')}
        Company: {job.get('company')}
        Description: {job.get('description')}
        
        Provide:
        1. Job quality score (1-10)
        2. Required skills extraction
        3. Experience level assessment
        4. Remote work compatibility
        5. Salary estimation
        """
        
        # Get multi-provider analysis
        llm_results = llm_adapter.score_job(analysis_prompt)
        
        # Add LLM insights to job data
        job['llm_analysis'] = llm_results
        enriched_jobs.append(job)
    
    return enriched_jobs
```

### 4. Custom Provider Implementation
```python
from tpm_job_finder_poc.llm_provider.base import LLMProvider
import requests

class CustomLLMProvider(LLMProvider):
    """Custom provider for internal or specialized LLM services."""
    
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key)
        self.base_url = base_url
    
    def get_signals(self, prompt: str) -> dict:
        """Implement custom provider logic."""
        if not self.api_key:
            return {"provider": "Custom", "error": "No API key provided"}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "custom-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "provider": "Custom",
                "response": result["choices"][0]["message"]["content"]
            }
            
        except Exception as e:
            return {"provider": "Custom", "error": str(e)}

# Register custom provider
from tpm_job_finder_poc.llm_provider.adapter import LLMAdapter

# Extend adapter to include custom provider
class ExtendedLLMAdapter(LLMAdapter):
    def _load_providers(self):
        providers = super()._load_providers()
        
        # Add custom provider if configured
        custom_key = Config.get("CUSTOM_LLM_API_KEY")
        custom_url = Config.get("CUSTOM_LLM_BASE_URL")
        if custom_key and custom_url:
            providers.append(CustomLLMProvider(custom_key, custom_url))
        
        return providers
```

## Architecture Decisions

### 1. Adapter Pattern Implementation
- **Unified interface**: Single entry point for all LLM interactions
- **Provider abstraction**: Clean separation between orchestration and implementation
- **Auto-discovery**: Dynamic provider loading based on configuration
- **Extensibility**: Easy addition of new providers without changing core logic

### 2. Error Handling Strategy
- **Graceful degradation**: Continue operation when individual providers fail
- **Provider isolation**: Errors in one provider don't affect others
- **Comprehensive logging**: Detailed error tracking for debugging
- **Fallback mechanisms**: Automatic retry and alternative provider usage

### 3. Configuration Management
- **Environment-first**: Prioritize environment variables for security
- **Auto-detection**: Automatically detect available providers
- **Flexible configuration**: Support for both environment and file-based config
- **Provider-specific settings**: Granular control over individual providers

### 4. Response Format Standardization
- **Consistent interface**: All providers return standardized response format
- **Error handling**: Uniform error reporting across providers
- **Metadata inclusion**: Provider identification and performance metrics
- **Extensible format**: Easy addition of new response fields

## Performance Characteristics

### Throughput
- **Parallel processing**: Concurrent requests to multiple providers
- **Async support**: Non-blocking provider operations
- **Rate limiting**: Built-in respect for provider rate limits
- **Connection pooling**: Optimized HTTP connection management

### Scalability
- **Stateless design**: No shared state between provider instances
- **Provider isolation**: Independent scaling of individual providers
- **Configuration flexibility**: Easy provider addition/removal
- **Resource optimization**: Efficient memory and connection usage

### Reliability
- **Fault tolerance**: Graceful handling of provider failures
- **Retry mechanisms**: Automatic retry with exponential backoff
- **Health monitoring**: Real-time provider availability tracking
- **Circuit breakers**: Automatic provider disabling during outages

## Error Handling

### Common Error Scenarios
```python
# Rate limiting handling
try:
    result = adapter.score_job(prompt)
except Exception as e:
    if "rate limit" in str(e).lower():
        print("Rate limited, implementing backoff...")
        time.sleep(60)  # Wait before retry

# API key validation
for provider_name, response in results.items():
    if response.get("error") == "No API key provided":
        print(f"Configure API key for {provider_name}")
    elif "quota exceeded" in response.get("error", ""):
        print(f"Quota exceeded for {provider_name}")

# Network connectivity
if all("error" in response for response in results.values()):
    print("All providers failed - check network connectivity")
```

### Error Recovery Patterns
```python
class RobustLLMAdapter(LLMAdapter):
    """Enhanced adapter with advanced error recovery."""
    
    def score_job_with_retry(self, prompt: str, max_retries: int = 3) -> dict:
        """Score job with automatic retry logic."""
        for attempt in range(max_retries):
            try:
                results = self.score_job(prompt)
                
                # Check if at least one provider succeeded
                if any("error" not in result for result in results.values()):
                    return results
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return {"error": "All retry attempts failed"}
```

## Testing

### Unit Tests
```bash
# Test individual providers
pytest tests/unit/test_llm_provider/test_providers/ -v

# Test adapter orchestration
pytest tests/unit/test_llm_provider/test_adapter.py -v

# Test error handling
pytest tests/unit/test_llm_provider/test_error_handling.py -v
```

### Integration Tests
```bash
# Test real API integration (requires API keys)
pytest tests/integration/test_llm_provider_apis.py -v

# Test provider health monitoring
pytest tests/integration/test_llm_provider_health.py -v

# Test configuration management
pytest tests/integration/test_llm_provider_config.py -v
```

### Mock Testing
```python
from unittest.mock import patch, MagicMock
import pytest

@patch('tpm_job_finder_poc.llm_provider.openai_provider.requests.post')
def test_openai_provider_success(mock_post):
    """Test successful OpenAI provider response."""
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Score: 8/10"}}]
    }
    mock_post.return_value = mock_response
    
    # Test provider
    provider = OpenAIProvider(api_key="test-key")
    result = provider.get_signals("Test prompt")
    
    assert result["provider"] == "ChatGPT"
    assert "Score: 8/10" in result["response"]

@patch('tpm_job_finder_poc.llm_provider.adapter.Config.get')
def test_adapter_auto_discovery(mock_config):
    """Test automatic provider discovery."""
    # Mock configuration
    mock_config.side_effect = lambda key, default=None: {
        "OPENAI_API_KEY": "openai-key",
        "ANTHROPIC_API_KEY": "anthropic-key",
        "OLLAMA_ENABLED": "false"
    }.get(key, default)
    
    # Test adapter initialization
    adapter = LLMAdapter()
    
    assert len(adapter.providers) == 2  # OpenAI and Anthropic
    assert any(isinstance(p, OpenAIProvider) for p in adapter.providers)
    assert any(isinstance(p, AnthropicProvider) for p in adapter.providers)
```

## Dependencies

### Core Dependencies
- **requests**: HTTP client for API integrations
- **abc**: Abstract base class support
- **typing**: Type hints and annotations
- **json**: Response parsing and serialization

### Internal Dependencies
- **config.config**: Configuration management system
- **error_handler**: Centralized error handling and logging

### External APIs
- **OpenAI API**: GPT-3.5/GPT-4 chat completions
- **Anthropic API**: Claude messages endpoint
- **Google AI API**: Gemini generative language API
- **DeepSeek API**: DeepSeek chat completions
- **Ollama API**: Local LLM inference server

## Security Considerations

### API Key Management
- **Environment variables**: Secure credential storage
- **No logging**: API keys never logged or exposed
- **Configuration isolation**: Separate dev/prod credentials
- **Key rotation**: Support for credential rotation

### Data Privacy
- **Prompt sanitization**: Remove sensitive information from prompts
- **Response filtering**: Filter sensitive information from responses
- **Audit logging**: Track LLM usage for compliance
- **Local options**: Ollama support for privacy-sensitive deployments

### Error Handling Security
- **Information disclosure**: Careful error message construction
- **Rate limiting**: Built-in protection against abuse
- **Timeout management**: Prevent hanging requests
- **Input validation**: Sanitize prompts before sending to providers

## Future Enhancements

### Planned Features
1. **Advanced prompt templates**: Reusable prompt management system
2. **Response caching**: Redis-based response caching for efficiency
3. **Load balancing**: Intelligent provider selection based on load
4. **Cost tracking**: Per-provider cost monitoring and optimization
5. **Model switching**: Dynamic model selection based on task requirements

### Performance Improvements
1. **Async/await support**: Full asynchronous provider operations
2. **Connection pooling**: HTTP connection reuse across requests
3. **Batch processing**: Bulk prompt processing capabilities
4. **Streaming responses**: Real-time response streaming support

### Integration Enhancements
1. **Webhook support**: Real-time provider status notifications
2. **Metrics export**: Prometheus metrics for monitoring
3. **OpenTelemetry**: Distributed tracing support
4. **GraphQL API**: Flexible LLM service querying