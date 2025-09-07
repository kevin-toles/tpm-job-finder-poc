Configuration Guide
==================

## Environment Variables
- Store secrets and API keys in `.env` or GitHub Actions secrets
- Supported keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY`, etc.

## Service Config
- Each service/component can have its own config file in its folder
- Use the centralized `config_manager.py` for loading config and secrets

## CI/CD
- All tests and linting run automatically in GitHub Actions
- Coverage is uploaded to Codecov

## Adding New Configs
- Document new config options here and in the relevant service README
