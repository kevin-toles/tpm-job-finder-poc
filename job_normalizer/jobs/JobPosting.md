# JobPosting Model

Normalized representation of a single job ad. Used across all connectors and services.

## Fields
- **id**: str — SHA-256 hash or source-specific ID
- **source**: str — remoteok | greenhouse | lever | ...
- **company**: str
- **title**: str
- **location**: str | None
- **salary**: str | None
- **url**: HttpUrl
- **date_posted**: datetime
- **raw**: dict — Unmodified payload from upstream API

## Example
```python
JobPosting(
    id="123456",
    source="remoteok",
    company="Acme Corp",
    title="Technical Program Manager",
    location="Remote",
    salary="$150k–$180k",
    url="https://remoteok.com/remote-jobs/123456",
    date_posted=datetime(2025, 1, 4, 21, 20, tzinfo=timezone.utc),
    raw={...}
)
```
