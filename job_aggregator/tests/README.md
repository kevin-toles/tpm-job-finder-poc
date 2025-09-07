# job_aggregator Tests

## How to Run
```
PYTHONPATH=. pytest tests/aggregators/
```

## Coverage
- Unit tests for each connector (RemoteOK, Greenhouse, Lever)
- End-to-end tests using sample fixture data
- Integration tests for all connectors

## Adding More Tests
- Add edge-case tests for API failures, schema mismatches, and deduplication
- Use pytest fixtures for offline testing
