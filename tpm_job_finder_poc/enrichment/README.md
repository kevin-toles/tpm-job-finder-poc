# Enrichment Component

Advanced job analysis, enhancement, and multi-resume intelligence system for optimal candidate-job matching.

## Overview

The enrichment component is the core intelligence engine of the TPM Job Finder system, providing sophisticated job analysis, resume portfolio management, and intelligent matching capabilities. It combines traditional rule-based processing with modern LLM integration to deliver comprehensive job-resume analysis and enhancement generation.

This component orchestrates multiple specialized services to analyze job postings, intelligently select optimal resumes from portfolios, and generate relevant enhancements to improve application success rates. The system supports both deterministic scoring algorithms and AI-powered semantic analysis.

The enrichment pipeline handles everything from basic job description parsing to advanced multi-resume portfolio management with semantic similarity validation, making it suitable for both individual job applications and large-scale batch processing.

## Architecture

```
enrichment/
├── __init__.py                      # Package exports and public interface
├── interfaces.py                    # Service interfaces and contracts
├── multi_resume_orchestrator.py     # Main coordination service (Primary API)
├── resume_discovery_service.py      # Portfolio scanning and cataloging
├── hybrid_selection_engine.py       # Two-stage intelligent resume selection
├── enhanced_content_analyzer.py     # Semantic analysis and enhancement generation
├── orchestrator.py                  # Classic job processing workflows
├── jd_parser.py                     # Job description parsing and extraction
├── ml_scorer.py                     # Machine learning-based scoring
├── resume_parser.py                 # Resume content analysis
├── heuristic_scorer.py              # Rule-based scoring algorithms
├── resume_feedback_generator.py     # Candidate feedback generation
├── taxonomy_mapper.py               # Skills and titles normalization
├── timeline_analyzer.py             # Career progression analysis
├── entity_canonicalizer.py          # Entity standardization
├── embeddings.py                    # Semantic similarity computations
└── llm_provider.py                  # LLM integration layer
```

## Public API

### Core Classes

#### MultiResumeIntelligenceOrchestrator
Primary service class for advanced resume portfolio management and intelligent job processing.

```python
from tpm_job_finder_poc.enrichment.multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
from tpm_job_finder_poc.models.job import Job
from pathlib import Path

class MultiResumeIntelligenceOrchestrator:
    def __init__(self, llm_provider=None):
        """Initialize orchestrator with optional LLM provider.
        
        Args:
            llm_provider: Optional LLM provider for AI-powered scoring
        """
    
    def process_job_with_multi_resume_intelligence(self, 
                                                  job: Job, 
                                                  resume_base_path: Path) -> JobIntelligenceResult:
        """Complete multi-resume intelligence processing.
        
        Args:
            job: Job posting to analyze
            resume_base_path: Path to resume portfolio directory
            
        Returns:
            JobIntelligenceResult with selected resume, match score, and enhancements
            
        Raises:
            ProcessingError: When job processing fails
            ValidationError: When input validation fails
        """
    
    def process_multiple_jobs(self, 
                            jobs: List[Job], 
                            resume_base_path: Path) -> List[JobIntelligenceResult]:
        """Batch process multiple jobs with resume intelligence."""
```

#### ResumeDiscoveryService
Intelligent resume portfolio scanning and categorization service.

```python
from tpm_job_finder_poc.enrichment.resume_discovery_service import ResumeDiscoveryService

class ResumeDiscoveryService:
    def scan_resume_folders(self, base_path: Path) -> ResumeInventory:
        """Recursively scan and catalog resume portfolio.
        
        Returns:
            ResumeInventory with master resume and categorized candidates
        """
```

#### HybridSelectionEngine  
Two-stage resume selection with keyword pre-filtering and LLM scoring.

```python
from tpm_job_finder_poc.enrichment.hybrid_selection_engine import HybridSelectionEngine

class HybridSelectionEngine:
    def select_optimal_resume(self, job: Job, inventory: ResumeInventory) -> SelectionResult:
        """Select best resume using hybrid keyword + LLM approach.
        
        Returns:
            SelectionResult with selected resume, score, and rationale
        """
```

### Key Methods

#### `process_job_with_multi_resume_intelligence(job, resume_base_path) -> JobIntelligenceResult`
- **Purpose**: Complete intelligent job processing with resume portfolio analysis
- **Parameters**: 
  - `job`: Job posting object with title, company, description
  - `resume_base_path`: Path to directory containing resume portfolio
- **Returns**: JobIntelligenceResult with selected resume, match score, selection rationale, and enhancement suggestions
- **Example**:
```python
orchestrator = MultiResumeIntelligenceOrchestrator()
job = Job(title="ML Engineer", company="Google", description="...")
result = orchestrator.process_job_with_multi_resume_intelligence(job, Path("~/resumes"))

print(f"Selected: {result.selected_resume.filename}")
print(f"Score: {result.match_score}%")
print(f"Rationale: {result.selection_rationale}")
```

#### `validate_enhancement_uniqueness(enhancements, selected_resume) -> bool`
- **Purpose**: Ensure enhancements are <80% similar to selected resume and <20% similar to each other
- **Parameters**: List of enhancements and selected resume metadata
- **Returns**: Boolean indicating whether uniqueness validation passed
- **Example**:
```python
is_unique = orchestrator.validate_enhancement_uniqueness(enhancements, selected_resume)
if not is_unique:
    logger.warning("Enhancement uniqueness validation failed")
```

## Configuration

### Environment Variables
```bash
# Multi-Resume Intelligence Settings
MULTI_RESUME_SEMANTIC_SIMILARITY_THRESHOLD=0.8
MULTI_RESUME_ENHANCEMENT_SIMILARITY_THRESHOLD=0.2
MULTI_RESUME_KEYWORD_MATCH_THRESHOLD=0.3
MULTI_RESUME_MAX_PROCESSING_TIME=120
MULTI_RESUME_MAX_ENHANCEMENTS=3

# LLM Provider Settings (Optional)
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key_here
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=3
```

### Configuration Class
```python
from tpm_job_finder_poc.config.multi_resume_config import MultiResumeConfig, get_config

@dataclass
class MultiResumeConfig:
    semantic_similarity_threshold: float = 0.8
    enhancement_similarity_threshold: float = 0.2
    keyword_match_threshold: float = 0.3
    max_processing_time_seconds: int = 120
    max_enhancements: int = 3
    master_folder_names: List[str] = field(default_factory=lambda: ["master", "complete", "comprehensive"])
    
    @classmethod
    def from_env(cls) -> "MultiResumeConfig":
        return cls(
            semantic_similarity_threshold=float(os.environ.get("MULTI_RESUME_SEMANTIC_SIMILARITY_THRESHOLD", "0.8")),
            enhancement_similarity_threshold=float(os.environ.get("MULTI_RESUME_ENHANCEMENT_SIMILARITY_THRESHOLD", "0.2")),
            # ... other config values
        )

# Usage
config = get_config()  # Loads from environment or defaults
```

## Usage Examples

### Basic Multi-Resume Intelligence
```python
from tpm_job_finder_poc.enrichment.multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
from tpm_job_finder_poc.models.job import Job
from pathlib import Path

# Initialize orchestrator
orchestrator = MultiResumeIntelligenceOrchestrator()

# Process single job
job = Job(
    title="Senior Python Developer",
    company="Acme Corp",
    description="We need a Python expert with ML experience..."
)

result = orchestrator.process_job_with_multi_resume_intelligence(
    job, Path("~/my_resume_portfolio")
)

print(f"Selected Resume: {result.selected_resume.filename}")
print(f"Match Score: {result.match_score}%")
print(f"Confidence: {result.confidence_level}")
print(f"Selection Rationale: {result.selection_rationale}")

for i, enhancement in enumerate(result.enhancements, 1):
    print(f"Enhancement {i}: {enhancement.bullet_point}")
    print(f"  Relevance: {enhancement.relevance_score}")
    print(f"  Category: {enhancement.category}")
```

### Batch Processing Multiple Jobs
```python
# Process multiple jobs efficiently
jobs = [
    Job(title="ML Engineer", company="Google", description="..."),
    Job(title="Data Scientist", company="Meta", description="..."),
    Job(title="Python Developer", company="Netflix", description="...")
]

results = orchestrator.process_multiple_jobs(jobs, Path("~/resumes"))

for result in results:
    print(f"Job: {result.job_id}")
    print(f"Selected: {result.selected_resume.filename if result.selected_resume else 'None'}")
    print(f"Processing Time: {result.processing_time:.2f}s")
```

### Resume Portfolio Discovery
```python
from tpm_job_finder_poc.enrichment.resume_discovery_service import ResumeDiscoveryService

discovery = ResumeDiscoveryService()
inventory = discovery.scan_resume_folders(Path("~/resume_portfolio"))

print(f"Master Resume: {inventory.master_resume.filename if inventory.master_resume else 'None'}")
print(f"Candidate Resumes: {len(inventory.candidate_resumes)}")

for resume in inventory.candidate_resumes:
    print(f"  - {resume.filename}")
    print(f"    Domain: {resume.domain_classification.primary_domain}")
    print(f"    Confidence: {resume.domain_classification.confidence_score}")
```

### Advanced Configuration with Custom LLM
```python
from tpm_job_finder_poc.llm_provider.openai_provider import OpenAIProvider

# Initialize with custom LLM provider
llm_provider = OpenAIProvider(api_key="your_key", model="gpt-4")
orchestrator = MultiResumeIntelligenceOrchestrator(llm_provider=llm_provider)

# Process with custom settings
result = orchestrator.process_job_with_multi_resume_intelligence(job, resume_path)
```

## Architecture Decisions

### Key Design Choices

1. **Two-Stage Selection Process**: Combines keyword pre-filtering with LLM scoring for optimal performance and accuracy
   - Stage 1 reduces candidates to 1-3 using domain keywords
   - Stage 2 applies LLM scoring only when multiple candidates remain
   - Balances speed with intelligence

2. **Semantic Similarity Validation**: Uses sentence transformers for enhancement uniqueness validation
   - Prevents duplicate or overly similar enhancement suggestions
   - Configurable thresholds (80% for resume similarity, 20% for enhancement similarity)
   - Ensures meaningful, diverse suggestions

3. **Master Resume Strategy**: Dedicated master/comprehensive resume handling
   - Master resumes identified by folder naming convention
   - Used only for enhancement generation, never for direct submission
   - Provides rich content source for bullet point suggestions

4. **Caching and Performance**: Intelligent caching to avoid repeated processing
   - Resume inventory cached per base path
   - Batch processing optimizations for multiple jobs
   - Configurable timeouts and resource limits

### Dependencies

**Internal Dependencies:**
- `models.resume_inventory` - Data models and structures
- `models.job` - Job posting representations
- `config.multi_resume_config` - Configuration management
- `llm_provider` - Multi-provider LLM integration

**External Dependencies:**
- `sentence-transformers` - Semantic similarity calculations
- `sklearn` - ML scoring and analysis
- `numpy` - Numerical computations
- `pandas` - Data manipulation (optional)

**Optional Dependencies:**
- LLM providers (OpenAI, Anthropic, etc.) - For AI-powered scoring
- `python-docx` - DOCX resume parsing
- `PyPDF2` - PDF resume parsing

### Interfaces

**Implements:**
- `IMultiResumeIntelligenceOrchestrator` - Main orchestration interface
- `IResumeDiscoveryService` - Portfolio scanning interface
- `IHybridSelectionEngine` - Resume selection interface
- `IEnhancedContentAnalyzer` - Content analysis interface

**Provides Services:**
- Multi-resume intelligent job processing
- Resume portfolio discovery and categorization
- Semantic similarity analysis
- Enhancement generation and validation

**Consumes Services:**
- LLM providers for AI-powered scoring
- Secure storage for resume file access
- Configuration management for settings

## Error Handling

### Exception Types
```python
class EnrichmentError(Exception):
    """Base exception for enrichment component errors."""
    
class ProcessingError(EnrichmentError):
    """Job processing workflow failures."""
    
class ResumeDiscoveryError(EnrichmentError):
    """Resume portfolio scanning failures."""
    
class SelectionEngineError(EnrichmentError):
    """Resume selection process failures."""
    
class ValidationError(EnrichmentError):
    """Input validation or uniqueness validation failures."""
```

### Error Recovery

**Retry Logic:**
- LLM calls include exponential backoff (3 attempts)
- File system operations retry on temporary failures
- Network timeouts with configurable duration (30s default)

**Fallback Strategies:**
- Generic enhancements when master resume analysis fails
- Heuristic scoring when LLM providers unavailable
- Simplified selection when full pipeline fails

**Graceful Degradation:**
- Returns partial results when non-critical components fail
- Logs detailed error context for debugging
- Maintains processing continuity for batch operations

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── test_multi_resume_orchestrator.py
│   ├── test_resume_discovery_service.py
│   ├── test_hybrid_selection_engine.py
│   └── test_enhanced_content_analyzer.py
├── integration/
│   ├── test_enrichment_integration.py
│   └── test_multi_resume_end_to_end.py
└── fixtures/
    ├── sample_jobs.py
    ├── mock_resumes/
    └── test_portfolios/
```

### Running Tests
```bash
# Unit tests for enrichment component
pytest tests/unit/test_*enrichment* -v

# Integration tests
pytest tests/integration/test_enrichment_integration.py -v

# Multi-resume intelligence tests
pytest tests/unit/test_multi_resume_intelligence.py -v

# Full enrichment test suite
pytest -k "enrichment" --cov=tpm_job_finder_poc.enrichment
```

### Test Data Requirements
- Sample job postings with varied requirements
- Mock resume portfolios with master/candidate structure
- Test LLM providers for deterministic testing
- Known similarity scores for validation testing

## Performance

### Benchmarks
- **Resume Discovery**: ~50-100 resumes/second for portfolio scanning
- **Selection Processing**: ~2-5 seconds per job (with LLM scoring)
- **Enhancement Generation**: ~1-3 seconds per master resume analysis
- **Memory Usage**: ~50-100MB for typical portfolio (10-20 resumes)

### Optimization Features
- **Inventory Caching**: Avoids repeated portfolio scanning
- **Batch LLM Processing**: Groups multiple candidates for efficiency  
- **Concurrent Processing**: Parallel job processing where safe
- **Resource Limits**: Configurable timeouts and memory bounds

### Monitoring
- **Health Checks**: Component availability and performance metrics
- **Processing Metrics**: Job processing times, success rates, LLM usage
- **Error Tracking**: Detailed error classification and frequency
- **Resource Usage**: Memory consumption, file I/O patterns

## Security

### Data Protection
- **PII Handling**: Resume content redacted in logs using centralized redactor
- **File Access**: All resume file I/O through SecureStorage component
- **API Keys**: LLM provider credentials managed through secure configuration
- **Audit Logging**: All resume access and processing logged for compliance

### Access Control
- **Path Validation**: Resume paths validated to prevent directory traversal
- **File Size Limits**: Configurable limits on resume file sizes (10MB default)
- **Format Validation**: Only approved resume formats accepted (.pdf, .docx, .txt, .doc)
- **Timeout Protection**: Processing timeouts prevent resource exhaustion

## Development

### Local Setup
```bash
# Install enrichment component dependencies
pip install sentence-transformers scikit-learn numpy

# Optional LLM provider dependencies
pip install openai anthropic

# Install development dependencies
pip install pytest pytest-cov black mypy

# Run component tests
python -m pytest tests/unit/test_*enrichment* -v
```

### Development Workflow
```bash
# Run enrichment component in development mode
python -m tpm_job_finder_poc.enrichment.multi_resume_orchestrator

# Test with sample data
python -c "
from tpm_job_finder_poc.enrichment.multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
from tpm_job_finder_poc.models.job import Job
from pathlib import Path

orchestrator = MultiResumeIntelligenceOrchestrator()
job = Job(title='Test Engineer', company='Test Corp', description='Testing role')
result = orchestrator.process_job_with_multi_resume_intelligence(job, Path('test_resumes'))
print(f'Result: {result.match_score}% match')
"
```

### Contributing Guidelines
- **Code Style**: Follow project Engineering Guidelines (types, error handling, documentation)
- **Testing**: Add tests for new functionality with >85% coverage
- **Documentation**: Update this README for any API changes
- **Performance**: Benchmark any changes affecting processing speed
- **Security**: Review PII handling for any resume content processing

## Related Documentation

- **[Multi-Resume Usage Guide](../../docs/specifications/MULTI_RESUME_USAGE_GUIDE.md)**: End-user guide and examples
- **[Advanced Resume Parsing Specification](../../docs/specifications/Advanced%20Resume%20Parsing_Scoring%20Functionality.md)**: Technical specification
- **[Implementation Summary](../../docs/implementation/IMPLEMENTATION_SUMMARY.md)**: Development progress and status
- **[LLM Provider Component](../llm_provider/README.md)**: LLM integration details
- **[Models Documentation](../models/README.md)**: Data structures and interfaces

---

*The enrichment component is the intelligence core of the TPM Job Finder system. For questions about multi-resume functionality, see the usage guide or create an issue.*