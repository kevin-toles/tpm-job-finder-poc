# Engineering Guidelines for TPM Job Finder POC

**Project**: TPM Job Finder POC (Python 3.13)  
**Role**: GitHub Copilot as Staff Engineer & Automated Development Lead  
**Goal**: Enforce coding standards automatically, apply strict TDD, eliminate AI/ML pitfalls, and maintain high-quality codebase

## 🎯 Core Principles

1. **Test-Driven Development**: RED → GREEN → REFACTOR for every change
2. **Type Safety**: Full typing with no `Any` escapes
3. **Fail-Fast**: Explicit error handling, no silent failures
4. **Architecture Boundaries**: Respect import dependencies
5. **AI/ML Safety**: Prevent data leakage, ensure reproducibility
6. **Security First**: Never expose secrets or PII

---

## 🏗️ Architecture Boundaries (Always Enforce)

### **Allowed Import Flow**
```
cli/controllers → services/orchestrators → storage/cache
```

### **Specific Rules**
- `enrichment/` depends only on `models/` + `llm_provider/` (NOT `scraping_service/`)
- `scraping_service/` never imports `enrichment/`
- `config/` is the only module that reads `os.environ`
- All file I/O goes through `SecureStorage`

### **Boundary Validation**
Before generating any import statements, verify:
```python
# ✅ ALLOWED
from tpm_job_finder_poc.models import JobPosting
from tpm_job_finder_poc.llm_provider import LLMProvider

# ❌ FORBIDDEN in enrichment/
from tpm_job_finder_poc.scraping_service import ScrapingService
```

---

## 📝 Coding Standards (Auto-Applied)

### **1. Type Safety**
```python
# ✅ REQUIRED - Full typing
def process_job(job: JobPosting, config: ProcessingConfig) -> ProcessingResult:
    """Process a job posting with full type safety."""
    pass

# ❌ FORBIDDEN - Missing types or Any
def process_job(job, config):
    pass

def process_job(job: Any, config: Any) -> Any:
    pass
```

### **2. Error Handling**
```python
# ✅ REQUIRED - Specific exception handling
try:
    result = external_service.call()
except requests.RequestException as e:
    logger.error("Service call failed", extra={"error": str(e), "service": "external"})
    raise ServiceUnavailableError("External service failed") from e

# ❌ FORBIDDEN - Silent failures
try:
    result = external_service.call()
except:
    pass

try:
    result = external_service.call()
except Exception:
    pass
```

### **3. Async Patterns**
```python
# ✅ REQUIRED - Timeouts and cancellation
async def fetch_data(url: str, timeout: float = 30.0) -> dict[str, Any]:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        try:
            async with session.get(url) as response:
                return await response.json()
        except asyncio.CancelledError:
            logger.info("Request cancelled", extra={"url": url})
            raise
        except aiohttp.ClientError as e:
            logger.error("HTTP error", extra={"url": url, "error": str(e)})
            raise

# ❌ FORBIDDEN - No timeout, blocking calls in async
async def fetch_data(url: str):
    response = requests.get(url)  # blocking in async!
    return response.json()
```

### **4. Documentation**
```python
# ✅ REQUIRED - Full docstrings for public APIs
def enrich_job_posting(
    job: JobPosting, 
    resume: Resume, 
    config: EnrichmentConfig
) -> EnrichmentResult:
    """Enrich a job posting with resume matching analysis.
    
    Args:
        job: The job posting to analyze
        resume: The resume to match against
        config: Configuration for enrichment process
        
    Returns:
        EnrichmentResult containing match score and analysis
        
    Raises:
        ValidationError: If job or resume data is invalid
        LLMServiceError: If LLM provider fails
    """
    pass
```

---

## 🤖 AI/ML Safety Rules (Critical)

### **1. Deterministic Code**
```python
# ✅ REQUIRED - Injectable randomness/time
@dataclass
class Clock:
    def now(self) -> datetime: pass
    def sleep_ms(self, ms: int) -> None: pass

@dataclass  
class Rng:
    def __init__(self, seed: int): pass
    def random(self) -> float: pass

def train_model(data: pd.DataFrame, clock: Clock, rng: Rng) -> Model:
    # Use injected dependencies for reproducibility
    pass

# ❌ FORBIDDEN - Direct calls to non-deterministic functions
import time
import random
import uuid

def train_model(data: pd.DataFrame) -> Model:
    time.sleep(1)  # Non-deterministic!
    seed = random.randint(1, 1000)  # Non-deterministic!
    id = str(uuid.uuid4())  # Non-deterministic!
```

### **2. Data Leakage Prevention**
```python
# ✅ REQUIRED - Split first, then transform
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def train_model(X: np.ndarray, y: np.ndarray, random_state: int = 42) -> Pipeline:
    # Split FIRST
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    
    # Then create pipeline (fits only on training data)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(random_state=random_state))
    ])
    
    pipeline.fit(X_train, y_train)
    return pipeline

# ❌ FORBIDDEN - Fit on full data then split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # LEAKAGE!
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
```

### **3. Memory Efficiency**
```python
# ✅ REQUIRED - Chunked processing for large data
def process_large_dataset(file_path: str, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
    """Process large CSV files in chunks to avoid memory issues."""
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Process chunk
        yield process_chunk(chunk)
        # Memory automatically freed after yield

# ✅ REQUIRED - Explicit cleanup
def train_on_large_data(data_path: str) -> Model:
    large_df = pd.read_csv(data_path)
    model = train_model(large_df)
    
    # Explicit cleanup for large objects
    del large_df
    gc.collect()
    
    return model

# ❌ FORBIDDEN - Loading entire large dataset
def process_large_dataset(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)  # May cause OOM!
```

### **4. Secrets & PII Protection**
```python
# ✅ REQUIRED - Redacted logging
import re

class Redactor:
    @staticmethod
    def redact_sensitive(text: str) -> str:
        # Email redaction
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                      '[EMAIL_REDACTED]', text)
        # Phone redaction  
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE_REDACTED]', text)
        # SSN redaction
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
        return text

def log_resume_processing(resume_content: str) -> None:
    redacted_content = Redactor.redact_sensitive(resume_content)
    logger.info("Processing resume", extra={"content_preview": redacted_content[:100]})

# ❌ FORBIDDEN - Raw PII in logs
def log_resume_processing(resume_content: str) -> None:
    logger.info(f"Processing resume: {resume_content}")  # PII leak!
```

---

## 🧪 Test-Driven Development (TDD)

### **TDD Workflow (Always Follow)**
1. **RED**: Write failing test first
2. **GREEN**: Minimal code to make test pass  
3. **REFACTOR**: Clean up implementation

```python
# Step 1: RED - Write failing test
def test_job_enrichment_calculates_match_score():
    """Test that job enrichment calculates a valid match score."""
    # Arrange
    job = JobPosting(title="Senior Python Developer", skills=["Python", "Django"])
    resume = Resume(skills=["Python", "Flask", "JavaScript"])
    config = EnrichmentConfig(min_match_threshold=0.5)
    enricher = JobEnricher()
    
    # Act
    result = enricher.enrich(job, resume, config)
    
    # Assert
    assert 0.0 <= result.match_score <= 1.0
    assert result.match_score >= 0.3  # Some overlap expected
    assert "Python" in result.matching_skills

# Step 2: GREEN - Minimal implementation
class JobEnricher:
    def enrich(self, job: JobPosting, resume: Resume, config: EnrichmentConfig) -> EnrichmentResult:
        # Minimal implementation to pass test
        common_skills = set(job.skills) & set(resume.skills)
        match_score = len(common_skills) / len(job.skills) if job.skills else 0.0
        return EnrichmentResult(
            match_score=match_score,
            matching_skills=list(common_skills)
        )

# Step 3: REFACTOR - Improve implementation
class JobEnricher:
    def enrich(self, job: JobPosting, resume: Resume, config: EnrichmentConfig) -> EnrichmentResult:
        """Enhanced implementation with better scoring algorithm."""
        # More sophisticated implementation
        pass
```

### **Test Quality Standards**
```python
# ✅ REQUIRED - Behavioral assertions, deterministic
def test_llm_provider_with_timeout():
    """Test LLM provider respects timeout configuration."""
    # Use fakes, not real services
    fake_llm = FakeLLMProvider(delay_ms=5000)  # Simulate slow response
    config = LLMConfig(timeout_ms=1000)
    
    with pytest.raises(TimeoutError):
        fake_llm.generate("test prompt", config)

# ✅ REQUIRED - Fixed seeds for reproducibility  
def test_model_training_reproducible():
    """Test that model training produces consistent results."""
    X, y = make_classification(random_state=42)
    
    model1 = train_model(X, y, random_state=42)
    model2 = train_model(X, y, random_state=42)
    
    # Should produce identical models
    assert np.allclose(model1.coef_, model2.coef_)

# ❌ FORBIDDEN - Non-deterministic tests
def test_random_behavior():
    result = some_function_with_randomness()  # Will be flaky!
    assert result > 0.5  # Flaky assertion
```

---

## 🔒 Security & Configuration

### **Configuration Management**
```python
# ✅ REQUIRED - Typed config objects
@dataclass
class LLMConfig:
    api_key: str
    timeout_ms: int = 30000
    max_retries: int = 3
    model: str = "gpt-4"
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            api_key=os.environ["LLM_API_KEY"],
            timeout_ms=int(os.environ.get("LLM_TIMEOUT_MS", "30000")),
            max_retries=int(os.environ.get("LLM_MAX_RETRIES", "3")),
            model=os.environ.get("LLM_MODEL", "gpt-4")
        )

# ✅ REQUIRED - Dependency injection
def create_llm_provider(config: LLMConfig) -> LLMProvider:
    return LLMProvider(config)

# ❌ FORBIDDEN - Direct environment access in business logic
def some_business_function():
    api_key = os.environ["API_KEY"]  # Should be in config layer only!
```

### **External Service Patterns**
```python
# ✅ REQUIRED - Timeouts, retries, circuit breaker
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_ms: int = 200
    max_delay_ms: int = 5000
    jitter_ms: int = 50

@dataclass  
class Budget:
    max_duration_s: int = 10
    max_cost_usd: float = 0.05

async def call_external_service(
    url: str, 
    payload: dict,
    retry_policy: RetryPolicy,
    budget: Budget,
    timeout_ms: int = 30000
) -> dict:
    """Call external service with comprehensive error handling."""
    start_time = time.time()
    
    for attempt in range(retry_policy.max_attempts):
        if time.time() - start_time > budget.max_duration_s:
            raise BudgetExceededError("Duration budget exceeded")
            
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout_ms/1000)
            ) as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == retry_policy.max_attempts - 1:
                raise ExternalServiceError(f"Service failed after {attempt + 1} attempts") from e
                
            # Exponential backoff with jitter
            delay = min(
                retry_policy.base_delay_ms * (2 ** attempt) + random.randint(0, retry_policy.jitter_ms),
                retry_policy.max_delay_ms
            )
            await asyncio.sleep(delay / 1000)
```

---

## 📊 Quality Gates (Auto-Enforced)

### **Code Quality Metrics**
- **Coverage**: Global ≥80%, Critical packages ≥85%
- **Complexity**: Average ≤A, Maximum ≤C (xenon)
- **Duplication**: ≤3% (jscpd)
- **Type Coverage**: 100% on public APIs (mypy)
- **Documentation**: ≥70% public API coverage (interrogate)

### **Performance Standards**
- **Fast Test Mode**: ≤10 seconds (`PYTEST_FAST_MODE=1`)
- **Full Test Suite**: ≤90 seconds
- **LLM Calls**: Timeout ≤30s, Budget ≤$0.05 per operation
- **Memory Usage**: Process large files in chunks ≤10MB

---

## 🎯 Component-Specific Guidelines

### **enrichment/ (High Priority)**
- Only import `models/` and `llm_provider/`
- All LLM calls must have timeouts and budgets
- Resume content must be redacted in logs
- Similarity scores between 0.0-1.0

### **scraping_service/ (High Priority)**  
- Never import `enrichment/`
- Respect robots.txt and rate limits
- No network calls in unit tests (use fakes)
- Deterministic retry logic

### **llm_provider/ (High Priority)**
- Standard interface across all providers
- Timeout and retry configuration
- Cost tracking and budgets
- Redacted request/response logging

### **models/ (High Priority)**
- Full type annotations
- Immutable data classes where possible
- Validation in constructors
- Serialization/deserialization methods

### **secure_storage/ (High Priority)**
- All file I/O goes through this module
- Path traversal protection
- Audit logging for access
- Encryption for sensitive data

---

## 🚀 Code Generation Checklist

When generating code, always ensure:

### **Before Writing Code**
- [ ] Identify which component this belongs to
- [ ] Check architecture boundaries for imports
- [ ] Plan the test structure (RED phase)

### **During Code Generation**
- [ ] Add full type annotations
- [ ] Include proper error handling
- [ ] Add timeouts to external calls
- [ ] Use dependency injection for Clock/Rng/Config
- [ ] Include docstrings for public functions
- [ ] Add structured logging with redaction

### **After Code Generation**
- [ ] Generate corresponding tests
- [ ] Verify no banned patterns (bare except, direct env access)
- [ ] Check complexity and duplication
- [ ] Ensure reproducibility (fixed seeds, deterministic behavior)

---

## 🔧 Templates & Helpers

### **Error Handling Template**
```python
class DomainError(Exception):
    """Base class for domain-specific errors."""
    pass

class ValidationError(DomainError):
    """Raised when input validation fails."""
    pass

class ExternalServiceError(DomainError):
    """Raised when external service calls fail."""
    pass

# Usage pattern
try:
    result = risky_operation()
except SpecificException as e:
    logger.error("Operation failed", extra={
        "operation": "risky_operation",
        "error": str(e),
        "context": {...}
    })
    raise DomainError("Friendly user message") from e
```

### **Async Service Template**
```python
@dataclass
class ServiceConfig:
    timeout_ms: int = 30000
    max_retries: int = 3
    base_delay_ms: int = 200

class AsyncService:
    def __init__(self, config: ServiceConfig, logger: Logger):
        self.config = config
        self.logger = logger
    
    async def call_external(self, payload: dict) -> dict:
        for attempt in range(self.config.max_retries):
            try:
                # Implementation with timeout
                pass
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    self.logger.error("Service call failed", extra={...})
                    raise ExternalServiceError("Service unavailable") from e
                await asyncio.sleep(self.config.base_delay_ms * (2 ** attempt) / 1000)
```

### **Test Helper Template**
```python
@pytest.fixture
def deterministic_config():
    """Provides deterministic configuration for tests."""
    return Config(
        clock=FakeClock(fixed_time=datetime(2025, 1, 1)),
        rng=FakeRng(seed=42),
        uuid_provider=FakeUuidProvider(fixed_uuid="test-uuid-123")
    )

def test_with_deterministic_deps(deterministic_config):
    """Example test using deterministic dependencies."""
    service = MyService(deterministic_config)
    result = service.process()
    assert result.timestamp == datetime(2025, 1, 1)  # Predictable!
```

---

## 📈 Success Metrics

### **Code Quality Trends**
- Decreasing complexity scores over time
- Increasing test coverage in critical paths  
- Reducing duplication percentage
- Improving type coverage

### **AI/ML Quality**
- No data leakage incidents
- Reproducible model results
- Bounded resource usage
- Zero PII/secrets in logs

### **Development Velocity**
- Fast test suite stays under 10s
- CI pipeline completes under 5 minutes
- Zero flaky tests
- Clean architectural boundaries

---

*This document serves as the authoritative reference for all code generation and refactoring activities. Every piece of generated code should align with these standards.*