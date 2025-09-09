# job_aggregator

ATS connectors for fetching Technical Program Manager jobs from RemoteOK, Greenhouse, and Lever.

## Usage
- Use the connector classes to fetch jobs from each source.
- Returns normalized `JobPosting` objects for downstream processing.

## API
- `RemoteOKConnector.fetch_since(days)`
- `GreenhouseConnector.fetch_since(days)`
- `LeverConnector.fetch_since(days)`

## Tests
Run with:
```
PYTHONPATH=. pytest tests/aggregators/
```
