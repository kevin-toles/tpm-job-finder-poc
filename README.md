
# TPM Job-Finder Proof-of-Concept

## Overview
This repo is organized as a set of top-level service folders, each representing a major feature or microservice. The architecture is designed for clear ownership, modularity, and future migration to true microservices.

## Architecture Cheat-Sheet

1. **job_aggregator/**: ATS connectors (RemoteOK, Greenhouse, Lever) for fetching jobs.
2. **job_normalizer/**: Cleans, normalizes, and dedupes job postings.
3. **llm_provider/**: Pluggable LLM adapter for scoring and rationale.
4. **heuristic_scorer/**: Fast, deterministic scoring utility.
5. **enrichment_orchestrator/**: Merges scores, applies business rules, ranks jobs.
6. **excel_exporter/**: Exports results to .xlsx for spreadsheet workflows.
7. **resume_uploader/**: FastAPI route for uploading resumes.
8. **resume_store/**: Persists resume text and metadata.
9. **storage/**: Abstracts local filesystem, future S3/GCS support.
10. **config/**: Loads environment config and secrets.
11. **audit_logger/**: Appends CLI/API actions to a JSONL audit trail.
12. **cache/**: Dedupe and already-applied job tracking.
13. **health/**: Status endpoint for container health checks.
14. **cli/**: CLI runner for pipeline execution.
15. **webhook/**: FastAPI route for deploy webhook.

## How to Run
- Each service is a Python package/module.
- Set `PYTHONPATH` to the project root for local development.
- Run tests with `PYTHONPATH=. pytest -v`.
- See per-service README files for details.

## Next Steps
- Per-service documentation
- Per-service requirements files
- Dockerization and CI/CD
- More tests and interface contracts

---
For a full narrative walkthrough, see `ARCHITECTURE.md` (to be added).
