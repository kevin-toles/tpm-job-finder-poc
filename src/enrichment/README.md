# Enrichment Components - README

## Overview
This folder contains core enrichment modules for job/resume matching, scoring, and feedback. Components are modular and extensible for POC and production use.

## Main Components
- **HeuristicScorer:** Deterministic scoring for resume/job fit, using recruiter-informed logic.
- **ResumeFeedbackGenerator:** Generates actionable feedback using heuristics and optional LLMs. Accepts txt/pdf/doc/docx resumes.
- **TaxonomyMapper:** Maps skills/titles to canonical forms for normalization.
- **Orchestrator:** Coordinates enrichment, scoring, and feedback across modules.
- **Embeddings:** (Stub) For semantic similarity and advanced matching.

## Stub Reference
- **Embeddings:** Stub for future semantic similarity and ML/LLM integration.
- **Orchestrator:** Extension points for analytics, feedback loops, external API integration.
- See [STUB_CATALOG.md](../../STUB_CATALOG.md) for a full list of stubs and guidance on extending them.

## Extensibility
- All components are designed for plug-and-play integration with ML/LLM services.
- Stubs and extension points are documented in code and the main stubs README.
- Future features: advanced analytics, feedback loops, and external API integration.

## Usage
- Import and use individual modules for scoring, feedback, or orchestration.
- Extend stubs as needed for production features.

---


---

## SecureStorage Integration

All enrichment modules now use SecureStorage for file, metadata, and log operations, ensuring secure and consistent data handling across enrichment workflows.

_Last updated: September 8, 2025_
