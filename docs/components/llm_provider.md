
# LLM Provider Service

Production-ready multi-provider LLM integration service for job scoring, analysis, and enrichment with comprehensive provider support and intelligent fallback mechanisms.

## Overview

The LLM Provider Service is a sophisticated adapter layer that provides unified access to multiple Large Language Model providers for job-related AI tasks including scoring, analysis, parsing, and enrichment.

## Features

### 🤖 Multi-Provider Support
- **OpenAI**: GPT-3.5/GPT-4 models for job analysis and scoring
- **Anthropic**: Claude models for comprehensive job evaluation
- **Google Gemini**: Advanced reasoning for job match analysis
- **DeepSeek**: Cost-effective scoring and analysis
- **Ollama**: Local LLM support for privacy-conscious deployments

### 🔒 Security & Configuration
- **Secure API Key Management**: Environment variables and secure file handling
- **Auto-Discovery**: Automatic provider detection based on available credentials
- **Graceful Degradation**: Continues operation when providers are unavailable
- **Rate Limiting**: Built-in rate limiting per provider

### 🎯 Use Cases
- **Job Scoring**: Multi-dimensional job fit scoring
- **Resume Analysis**: Resume parsing and feedback generation
- **Job Enrichment**: Enhanced job descriptions and metadata
- **Match Analysis**: Job-resume compatibility scoring

## Architecture

```
llm_provider/
├── adapter.py              # Main LLM adapter with provider orchestration
├── base.py                 # Base provider interface and common functionality
├── openai_provider.py      # OpenAI GPT integration
├── anthropic_provider.py   # Anthropic Claude integration
├── gemini_provider.py      # Google Gemini integration
├── deepseek_provider.py    # DeepSeek model integration
├── ollama_provider.py      # Local Ollama integration
├── health.py              # Provider health monitoring
└── tests/                 # Comprehensive test suite
```

## Configuration

### API Key Setup

#### Method 1: Environment Variables (Recommended)
```bash
export OPENAI_API_KEY="sk-xxxxxx"
export ANTHROPIC_API_KEY="sk-ant-xxxxxx"
export GOOGLE_API_KEY="your-gemini-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
export OLLAMA_API_KEY=""  # Leave blank for local Ollama
```

#### Method 2: Configuration File
Add to `llm_keys.txt` in project root:
```
OPENAI_API_KEY=sk-xxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxx
GOOGLE_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key
OLLAMA_API_KEY=  # leave blank for local
```

### Provider Configuration
```python
# Provider-specific configurations
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
        'temperature': 0.1
    },
    'gemini': {
        'model': 'gemini-pro',
        'temperature': 0.1,
        'safety_settings': 'block_few'
    }
}
```

## Usage

### Basic Job Scoring
```python
from tpm_job_finder_poc.llm_provider.adapter import LLMAdapter

# Initialize adapter (auto-detects available providers)
adapter = LLMAdapter()

# Score a job posting
job_text = "Senior Software Engineer position..."
results = adapter.score_job(job_text)

print(f"Available providers: {results['providers']}")
print(f"Aggregate score: {results['aggregate_score']}")
```

### Advanced Usage with Resume Matching
```python
# Score job against resume
resume_text = "Software engineer with 5 years experience..."
match_results = adapter.score_job_resume_match(
    job_text=job_text,
    resume_text=resume_text
)

print(f"Match score: {match_results['match_score']}")
print(f"Recommendations: {match_results['recommendations']}")
```

### Provider-Specific Scoring
```python
# Use specific provider
openai_result = adapter.score_with_provider(
    provider='openai',
    prompt=job_text
)

# Fallback handling
all_results = adapter.score_with_fallback(
    prompt=job_text,
    preferred_providers=['openai', 'anthropic', 'gemini']
)
```

## API Reference

### LLMAdapter Class

#### Core Methods
```python
def score_job(self, prompt: str, job_data: dict = None) -> dict:
    """Score a job using all available providers"""

def score_job_resume_match(self, job_text: str, resume_text: str) -> dict:
    """Score job-resume compatibility"""

def score_with_provider(self, provider: str, prompt: str) -> dict:
    """Score using specific provider"""

def score_with_fallback(self, prompt: str, preferred_providers: list) -> dict:
    """Score with provider fallback logic"""

def get_available_providers(self) -> list:
    """Get list of available/configured providers"""

def health_check(self) -> dict:
    """Check health status of all providers"""
```

#### Response Format
```python
{
    'providers': ['openai', 'anthropic'],
    'aggregate_score': 8.5,
    'detailed_scores': {
        'openai': {'score': 8.7, 'rationale': '...'},
        'anthropic': {'score': 8.3, 'rationale': '...'}
    },
    'confidence': 0.95,
    'processing_time': 2.3,
    'recommendations': ['...']
}
```

### Provider Base Class
```python
class BaseLLMProvider:
    def score_job(self, prompt: str) -> dict:
        """Core scoring method - implement in providers"""
    
    def health_check(self) -> bool:
        """Provider health check"""
    
    def get_model_info(self) -> dict:
        """Provider and model information"""
```

## Health Monitoring

### Provider Health Checks
```python
# Check all provider health
health_status = adapter.health_check()
print(health_status)
# Output:
{
    'overall_health': 'healthy',
    'providers': {
        'openai': {'status': 'healthy', 'latency': 1.2},
        'anthropic': {'status': 'healthy', 'latency': 0.8},
        'gemini': {'status': 'degraded', 'latency': 3.5}
    }
}
```

### Monitoring Integration
```python
from tpm_job_finder_poc.llm_provider.health import LLMHealthMonitor

monitor = LLMHealthMonitor()
monitor.start_monitoring(interval=60)  # Check every minute
```

## Testing

### Test Categories
- **Unit Tests**: Individual provider functionality
- **Integration Tests**: Multi-provider workflows
- **Mock Tests**: Testing without API calls
- **Health Tests**: Provider availability and performance

### Running Tests
```bash
# Run all LLM provider tests
python -m pytest tpm_job_finder_poc/llm_provider/tests/ -v

# Run with API key validation (requires valid keys)
python -m pytest tpm_job_finder_poc/llm_provider/tests/ -v --api-tests

# Run without external API calls (mocked)
python -m pytest tpm_job_finder_poc/llm_provider/tests/ -v --mock-only
```

### Test Skipping Behavior
- Tests automatically skip when required API keys are missing
- Ollama tests skip when local server is not running
- Integration tests run only when multiple providers are available

## Error Handling

### Graceful Degradation
```python
# Adapter continues working even if some providers fail
try:
    results = adapter.score_job(job_text)
    if not results['providers']:
        # All providers failed - use fallback scoring
        results = fallback_scoring_logic(job_text)
except Exception as e:
    logger.error(f"LLM scoring failed: {e}")
    # Continue with non-LLM workflow
```

### Rate Limiting
```python
# Built-in rate limiting per provider
from tpm_job_finder_poc.llm_provider.adapter import RateLimitError

try:
    results = adapter.score_job(job_text)
except RateLimitError:
    # Wait and retry, or use different provider
    time.sleep(60)
    results = adapter.score_with_fallback(job_text, ['gemini', 'deepseek'])
```

## Performance Optimization

### Caching
```python
# Enable response caching for repeated queries
adapter = LLMAdapter(enable_cache=True, cache_ttl=3600)

# Cache key based on prompt hash
cached_result = adapter.score_job(job_text)  # Cached for 1 hour
```

### Batch Processing
```python
# Batch multiple jobs for efficiency
job_texts = ["Job 1...", "Job 2...", "Job 3..."]
batch_results = adapter.batch_score_jobs(job_texts)
```

### Async Support
```python
import asyncio

# Async job scoring
async def score_jobs_async(job_texts):
    adapter = LLMAdapter()
    tasks = [adapter.score_job_async(text) for text in job_texts]
    return await asyncio.gather(*tasks)
```

## Security Best Practices

### API Key Management
- ✅ **Never hardcode API keys in source code**
- ✅ **Use environment variables in production**
- ✅ **Exclude `llm_keys.txt` from version control**
- ✅ **Rotate API keys regularly**
- ✅ **Use least-privilege API key permissions**

### Data Privacy
- ✅ **Job data is not stored by providers (configured)**
- ✅ **Local Ollama option for sensitive data**
- ✅ **Request/response logging can be disabled**
- ✅ **PII scrubbing before LLM processing**

## Troubleshooting

### Common Issues

#### Provider Not Available
```python
# Check provider status
if 'openai' not in adapter.get_available_providers():
    print("OpenAI not configured - check API key")
```

#### Rate Limiting
```python
# Handle rate limits gracefully
try:
    result = adapter.score_job(job_text)
except RateLimitError as e:
    print(f"Rate limited: {e.retry_after} seconds")
    time.sleep(e.retry_after)
```

#### Ollama Connection
```bash
# Start local Ollama server
ollama serve

# Verify connection
curl http://localhost:11434/api/tags
```

### Debug Mode
```python
# Enable detailed logging
import logging
logging.getLogger('llm_provider').setLevel(logging.DEBUG)

adapter = LLMAdapter(debug=True)
```

## Extending the Service

### Adding New Providers
1. **Create Provider Class**:
```python
# new_provider.py
from tpm_job_finder_poc.llm_provider.base import BaseLLMProvider

class NewProvider(BaseLLMProvider):
    def score_job(self, prompt: str) -> dict:
        # Implementation
        pass
```

2. **Register in Adapter**:
```python
# adapter.py
from .new_provider import NewProvider

self.providers['new_provider'] = NewProvider()
```

3. **Add Tests**:
```python
# tests/test_new_provider.py
def test_new_provider_scoring():
    provider = NewProvider()
    result = provider.score_job("test prompt")
    assert 'score' in result
```

### Custom Scoring Logic
```python
class CustomLLMAdapter(LLMAdapter):
    def custom_score_algorithm(self, job_data: dict) -> float:
        # Custom scoring implementation
        return calculated_score
```

## Integration Examples

### With Job Aggregator
```python
from tpm_job_finder_poc.job_aggregator.service import JobAggregatorService
from tpm_job_finder_poc.llm_provider.adapter import LLMAdapter

service = JobAggregatorService()
llm_adapter = LLMAdapter()

# Enrich jobs with LLM scores
jobs = service.collect_jobs()
for job in jobs:
    llm_result = llm_adapter.score_job(job['description'])
    job['llm_score'] = llm_result['aggregate_score']
    job['llm_analysis'] = llm_result['detailed_scores']
```

### With Enrichment Pipeline
```python
from tpm_job_finder_poc.enrichment.orchestrator import EnrichmentOrchestrator

orchestrator = EnrichmentOrchestrator()
enriched_jobs = orchestrator.enrich_jobs_with_llm(jobs)
```

## Monitoring & Observability

### Metrics Collection
```python
# Provider performance metrics
metrics = adapter.get_performance_metrics()
print(f"Average response time: {metrics['avg_response_time']}")
print(f"Success rate: {metrics['success_rate']}")
```

### Health Dashboard
```python
# Real-time provider health monitoring
health_dashboard = adapter.get_health_dashboard()
```

---

## Version History

- **v1.0.0**: Production-ready multi-provider LLM service
- **v0.8.0**: Added Gemini and DeepSeek provider support
- **v0.6.0**: Implemented health monitoring and fallback logic
- **v0.4.0**: Added Ollama local LLM support
- **v0.2.0**: Multi-provider architecture with OpenAI and Anthropic

---

## Related Documentation

- **[Enrichment Pipeline](../enrichment/README.md)**: Job enrichment using LLM providers
- **[Job Aggregator](../job_aggregator/README.md)**: Main service integration
- **[Configuration Guide](../../config/README.md)**: System configuration
- **[Security Guide](../../docs/security.md)**: Security best practices

---

_For the latest updates and API changes, refer to the [CHANGELOG.md](../../CHANGELOG.md)._
