
# LLM Provider Adapter

Pluggable connector for scoring jobs and extracting signals from multiple LLMs (OpenAI, Ollama, Anthropic, Gemini, DeepSeek, etc.).

## Usage
- Add your API keys to `api_keys.txt` in the project root, e.g.:
  ```
  OPENAI_API_KEY=sk-xxxxxx
  ANTHROPIC_API_KEY=sk-ant-xxxxxx
  GEMINI_API_KEY=your-key
  DEEPSEEK_API_KEY=your-key
  OLLAMA_API_KEY=  # leave blank for local
  ```
- You can also set API keys as environment variables (recommended for CI/CD and security):
  - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY`
- The adapter will automatically skip providers with missing/blank keys.

## Interpreting Skipped Tests
- Tests for LLM providers will be skipped if the required API key or local server is not configured.
- This is expected and ensures the test suite does not fail due to missing external credentials.

## Security Warning
- **Never hard-code API keys in code or commit them to version control.**
- Use environment variables or `api_keys.txt` (which should be excluded from public repos).

## API
- `LLMAdapter.score_job(prompt: str) -> dict`: Get scores/rationales from all available LLMs.

## Extending
- Add new provider adapters in this folder and update `adapter.py`.
- Add a corresponding test in `tests/unit/` and update integration/e2e tests as needed.

## Example
```python
from src.llm_provider.adapter import LLMAdapter
adapter = LLMAdapter()
results = adapter.score_job("Score this job for fit: ...")
print(results)
```
