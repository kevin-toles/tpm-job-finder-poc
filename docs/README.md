# TPM Job Finder Documentation

This directory contains documentation for the TPM Job Finder POC project.

## Overview

The TPM Job Finder is a proof-of-concept application designed to help Technical Program Managers find relevant job opportunities across multiple job boards and company websites.

## Architecture

### Core Components

1. **Search Engine** (`src/core/search.py`)
   - Main job search and filtering logic
   - Market analysis functionality
   - Job scoring and ranking

2. **Data Models** (`src/models/job.py`)
   - Pydantic models for data validation
   - Job posting, search criteria, and user profile schemas

3. **Connectors** (`src/connectors/`)
   - Integration with external job boards
   - Currently includes Lever connector
   - Extensible for additional job sources

4. **Utilities** (`src/utils/`)
   - Common data processing functions
   - Text parsing and normalization
   - Helper functions

### Data Flow

```
Search Criteria → Search Engine → Connectors → Job Boards
                                     ↓
Job Results ← Data Processing ← Raw Job Data
```

## Usage Examples

### Basic Job Search

```python
from src.core.search import JobSearchEngine
from src.models.job import SearchCriteria

# Create search engine
engine = JobSearchEngine()

# Define search criteria
criteria = SearchCriteria(
    keywords=["technical program manager", "tpm"],
    location="Remote",
    remote_allowed=True,
    salary_min=120000
)

# Search for jobs
jobs = engine.search_jobs(criteria.dict())
```

### Using Connectors

```python
from src.connectors.lever import LeverConnector

# Initialize connector
connector = LeverConnector(api_key="your-api-key")

# Fetch jobs from a company
jobs = connector.fetch_jobs("company-name")
```

## Configuration

Configuration is managed through environment variables and the `src/config/settings.py` module.

Key configuration options:
- API keys for job board integrations
- Database connection settings
- Rate limiting parameters
- Feature flags

## Testing

The project includes comprehensive test coverage:

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test component interactions

Run tests with:
```bash
python -m pytest tests/
```

## Development

### Adding New Job Board Connectors

1. Create a new file in `src/connectors/`
2. Implement the connector class with required methods:
   - `fetch_jobs()`
   - `get_job_details()`
   - `search_companies()`
3. Add transformation functions for data normalization
4. Add tests in `tests/integration/`

### Data Models

All data should use the Pydantic models defined in `src/models/` for:
- Type validation
- Serialization/deserialization
- API documentation generation

## Future Enhancements

This POC establishes the foundation for:

1. **Enhanced Search Capabilities**
   - Machine learning-based job matching
   - Advanced filtering and ranking
   - Personalized recommendations

2. **Additional Integrations**
   - More job board connectors
   - Company career page scrapers
   - Email notifications

3. **User Interface**
   - Web application
   - Mobile app
   - API endpoints

4. **Analytics and Insights**
   - Job market trend analysis
   - Salary benchmarking
   - Success tracking