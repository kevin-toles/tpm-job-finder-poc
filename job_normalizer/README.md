# job_normalizer

Cleans, normalizes, and dedupes job postings from ATS connectors.

## Usage
- Use the normalization utilities to standardize job data.
- Deduplication by company, title, and URL hash.

## API
- `JobPosting` pydantic model
- `Normalizer` and `Parser` utilities

## Tests
Run with:
```
PYTHONPATH=. pytest tests/aggregators/
```
