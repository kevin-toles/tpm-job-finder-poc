# llm_provider

Pluggable LLM adapter for scoring and rationale generation.

## Usage
- Call with normalized job and resume to get scores and rationale.
- Supports OpenAI, Anthropic, Gemini, or local providers.

## API
- `LLMProvider.score(job, resume)`

## Tests
Add and run with:
```
PYTHONPATH=. pytest
```
