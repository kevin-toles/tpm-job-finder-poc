
# job_normalizer

Cleans, normalizes, validates, and dedupes job postings from ATS connectors.

## Usage
- Use the normalization utilities to standardize job data fields (title, salary, location).
- Deduplicate jobs by company, title, and URL hash.
- Parse raw job data into a unified schema.
- Handles edge cases and malformed data with validation and error reporting.

## API
- `JobPosting` (Pydantic model): strict schema, UTC date normalization, required fields, error logging.
- `normalize_job`, `normalize_title`, `normalize_salary`, `normalize_location`: normalization utilities with logging for unexpected types.
- `dedupe_jobs`: removes duplicates, logs input/output counts.
- `parse_job`: parses raw job dicts, raises and logs errors for invalid data.

## Error Handling & Logging
- All normalization and parsing functions log warnings/errors for invalid or missing data.
- Validation errors are raised and logged with context.
- Logging can be configured via Python's `logging` module.

## Extensibility
- To add a new job source, implement a parser that outputs the `JobPosting` schema.
- See `parser.py` for examples.

## Tests
Run with:
```
PYTHONPATH=. pytest job_normalizer/tests/
```

## Integration
- Integration tests simulate real-world job feeds and edge cases.

## Example
```python
from job_normalizer.jobs.parser import parse_job
from job_normalizer.jobs.normalizer import normalize_job, dedupe_jobs

raw = { ... }
job = parse_job(raw, source="remoteok")
norm = normalize_job(job)
jobs = dedupe_jobs([norm, ...])
```
