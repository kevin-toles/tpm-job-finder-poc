# Enrichment Components

## Overview
The enrichment pipeline provides comprehensive job analysis, enhancement, and scoring capabilities using both traditional heuristics and modern LLM integration. This modular system supports the full workflow from job description parsing to candidate matching and feedback generation.

## Architecture

The enrichment system is built around a modular architecture that supports both deterministic rule-based processing and AI-powered enhancement:

```
enrichment/
├── orchestrator.py              # Main orchestration and workflow management
├── jd_parser.py                 # Job description parsing and extraction
├── ml_scorer.py                 # Machine learning-based job scoring
├── resume_parser.py             # Resume analysis and parsing
├── heuristic_scorer.py          # Rule-based scoring system
├── resume_feedback_generator.py # Feedback generation for candidates
├── taxonomy_mapper.py           # Skills and titles normalization
├── timeline_analyzer.py         # Career timeline analysis
├── entity_canonicalizer.py      # Entity normalization
├── embeddings.py                # Semantic similarity and embeddings
└── llm_provider.py              # LLM integration layer
```

## Core Components

### 1. Orchestrator (`orchestrator.py`)
Central coordination service for all enrichment activities:
- **Workflow Management**: Coordinates job processing pipelines
- **Service Integration**: Manages LLM providers and scoring services
- **Resource Coordination**: Handles concurrent processing and rate limiting
- **Error Handling**: Comprehensive error recovery and logging
- **Health Monitoring**: Service health checks and performance monitoring

### 2. Job Description Parser (`jd_parser.py`)
Advanced job description analysis and extraction:
- **Skills Extraction**: Identify technical and soft skills requirements
- **Requirements Parsing**: Extract education, experience, and qualification requirements
- **Compensation Analysis**: Parse salary ranges and benefits information
- **Location Processing**: Standardize location and remote work options
- **Company Information**: Extract company size, industry, and culture details

### 3. ML Scorer (`ml_scorer.py`)
Machine learning-based job compatibility scoring:
- **Compatibility Analysis**: Score job-candidate fit using ML models
- **Skills Matching**: Semantic similarity between candidate and job skills
- **Experience Weighting**: Score based on relevant experience levels
- **Cultural Fit**: Analyze company culture and candidate preferences
- **Prediction Confidence**: Provide confidence scores for recommendations

### 4. Resume Parser (`resume_parser.py`)
Comprehensive resume analysis and extraction:
- **Multi-Format Support**: Parse PDF, DOC, DOCX, and TXT resume formats
- **Information Extraction**: Extract contact info, experience, education, skills
- **Career Timeline**: Build chronological career progression
- **Skills Normalization**: Map skills to standardized taxonomy
- **Quality Assessment**: Evaluate resume completeness and formatting

### 5. Heuristic Scorer (`heuristic_scorer.py`)
Rule-based scoring system using recruiter-informed logic:
- **Deterministic Scoring**: Consistent, explainable scoring algorithms
- **Experience Matching**: Match years of experience to job requirements
- **Skills Coverage**: Calculate percentage of required skills covered
- **Location Compatibility**: Score based on location preferences and remote options
- **Salary Alignment**: Compare salary expectations with job offers

### 6. Resume Feedback Generator (`resume_feedback_generator.py`)
Actionable feedback generation for job seekers:
- **Gap Analysis**: Identify missing skills and experience gaps
- **Improvement Suggestions**: Provide specific recommendations for enhancement
- **Formatting Feedback**: Suggest resume formatting and structure improvements
- **Keyword Optimization**: Recommend keywords for better ATS compatibility
- **LLM Integration**: Use AI for personalized feedback generation

### 7. Taxonomy Mapper (`taxonomy_mapper.py`)
Skills and job titles normalization system:
- **Skills Standardization**: Map variant skill names to canonical forms
- **Title Normalization**: Standardize job titles across different companies
- **Industry Mapping**: Categorize roles by industry and function
- **Seniority Analysis**: Determine experience levels from titles
- **Technology Grouping**: Group related technologies and frameworks

## LLM Integration

### Supported Providers
The enrichment system integrates with multiple LLM providers for enhanced analysis:
- **OpenAI GPT**: GPT-3.5 and GPT-4 for general analysis
- **Anthropic Claude**: Advanced reasoning and analysis
- **Google Gemini**: Multi-modal analysis capabilities
- **DeepSeek**: Cost-effective analysis for high-volume processing
- **Ollama**: Local LLM deployment for privacy-sensitive processing

### LLM Use Cases
- **Job Description Enhancement**: Improve job posting quality and clarity
- **Skills Gap Analysis**: Identify candidate development opportunities
- **Interview Question Generation**: Create relevant interview questions
- **Salary Benchmarking**: Provide market salary insights
- **Career Path Recommendations**: Suggest career progression paths

## Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Raw Job Data  │    │ Resume Document  │    │  Configuration  │
│   (from APIs)   │    │  (PDF/DOC/TXT)   │    │   Parameters    │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Enrichment           │
                    │    Orchestrator         │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼───────┐    ┌───────────▼──────────┐    ┌───────▼───────┐
│ Job Description│    │   Resume Parser      │    │   Skills      │
│    Parser      │    │   & Analyzer         │    │ Taxonomy      │
└───────┬───────┘    └───────────┬──────────┘    └───────┬───────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     ML Scorer &         │
                    │  Heuristic Scorer       │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Feedback Generator    │
                    │   & Recommendations     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Enhanced Job Data    │
                    │  + Scoring + Feedback   │
                    └─────────────────────────┘
```

## Usage Examples

### 1. Basic Job Enrichment
```python
from tpm_job_finder_poc.enrichment.orchestrator import EnrichmentOrchestrator

orchestrator = EnrichmentOrchestrator()
enriched_job = await orchestrator.enrich_job(job_data)
```

### 2. Resume Analysis and Scoring
```python
from tpm_job_finder_poc.enrichment.resume_parser import ResumeParser
from tpm_job_finder_poc.enrichment.ml_scorer import MLScorer

parser = ResumeParser()
scorer = MLScorer()

resume_data = parser.parse_resume("resume.pdf")
score = scorer.score_compatibility(job_data, resume_data)
```

### 3. Generate Candidate Feedback
```python
from tpm_job_finder_poc.enrichment.resume_feedback_generator import ResumeFeedbackGenerator

feedback_gen = ResumeFeedbackGenerator()
feedback = feedback_gen.generate_feedback(resume_data, job_data)
```

### 4. Skills Normalization
```python
from tpm_job_finder_poc.enrichment.taxonomy_mapper import TaxonomyMapper

mapper = TaxonomyMapper()
canonical_skills = mapper.normalize_skills(["Javascript", "React.js", "Node"])
# Returns: ["JavaScript", "React", "Node.js"]
```

## Configuration

### Enrichment Settings
```json
{
  "enrichment": {
    "enabled": true,
    "llm_provider": "openai",
    "scoring_enabled": true,
    "feedback_enabled": true,
    "taxonomy_mapping": true,
    "batch_processing": {
      "enabled": true,
      "batch_size": 10,
      "concurrent_requests": 3
    },
    "scoring_weights": {
      "skills_match": 0.4,
      "experience_match": 0.3,
      "location_match": 0.2,
      "salary_match": 0.1
    }
  }
}
```

### LLM Provider Configuration
```python
# In llm_keys.txt
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GEMINI_API_KEY=your-gemini-key
```

## Security & Storage

### SecureStorage Integration
All enrichment modules use SecureStorage for:
- **File Operations**: Secure resume and document processing
- **Metadata Management**: Audit trails and processing history
- **Log Operations**: Secure logging of enrichment activities
- **Cache Management**: Secure caching of processing results

### Data Privacy
- **Resume Processing**: Local processing with secure storage
- **API Key Management**: Secure handling of LLM provider credentials
- **Data Retention**: Configurable data retention policies
- **Audit Logging**: Complete audit trails for compliance

## Performance & Scaling

### Optimization Features
- **Async Processing**: Concurrent job and resume processing
- **Caching**: Intelligent caching of LLM responses and computations
- **Batch Processing**: Efficient batch processing for high-volume scenarios
- **Rate Limiting**: Respect LLM provider rate limits
- **Resource Management**: Memory and CPU optimization

### Monitoring
- **Processing Metrics**: Track enrichment throughput and latency
- **Quality Metrics**: Monitor scoring accuracy and feedback quality
- **Error Rates**: Track and alert on processing errors
- **LLM Usage**: Monitor API usage and costs

## Extension Points

### Adding New Scorers
```python
from tpm_job_finder_poc.enrichment.orchestrator import EnrichmentOrchestrator

class CustomScorer:
    def score_job(self, job_data: dict, candidate_data: dict) -> float:
        # Implement custom scoring logic
        return score

orchestrator = EnrichmentOrchestrator()
orchestrator.register_scorer("custom", CustomScorer())
```

### Adding New Enrichers
```python
class CustomEnricher:
    def enrich_job(self, job_data: dict) -> dict:
        # Implement custom enrichment logic
        return enhanced_job_data

orchestrator.register_enricher("custom", CustomEnricher())
```

## Testing

The enrichment pipeline is thoroughly tested with:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component workflow testing
- **LLM Tests**: Mock and live LLM provider testing
- **Performance Tests**: Load and performance validation

Run enrichment tests:
```bash
python -m pytest tests/unit/test_enrichment/ -v
python -m pytest tests/integration/test_enrichment_integration.py -v
```

## Future Enhancements

- **Advanced ML Models**: Integration with custom ML models for scoring
- **Multi-Language Support**: Resume and job parsing in multiple languages
- **Real-Time Processing**: Stream processing for high-volume scenarios
- **Advanced Analytics**: Detailed analytics and reporting dashboard
- **A/B Testing**: Framework for testing different enrichment strategies

---

_Last updated: January 2025 - Production-ready enrichment pipeline with comprehensive LLM integration_
