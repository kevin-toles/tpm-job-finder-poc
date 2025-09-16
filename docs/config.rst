Configuration Guide
==================

## Environment Variables
- Store secrets and API keys in `.env` or GitHub Actions secrets
- Supported keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY`, etc.

## Service Config
- Each service/component can have its own config file in its folder
- Use the centralized `config_manager.py` for loading config and secrets

## Multi-Resume Intelligence Configuration
The multi-resume intelligence system uses `MultiResumeConfig` with the following key parameters:

- `semantic_similarity_threshold: 0.8` - Enhancements must be <80% similar to selected resume content
- `enhancement_similarity_threshold: 0.2` - Enhancements must be <20% similar to each other
- `keyword_match_threshold: 0.3` - Minimum keyword match for pre-filtering
- `max_enhancements: 3` - Number of enhancements to generate per job
- `master_folder_names: ["master", "complete", "comprehensive"]` - Folder names identifying master resumes
- `domain_keywords` - Keywords for classifying resumes by domain (technology, business, creative)

Configuration file location: `config/multi_resume_config.json`

## CI/CD
- All tests and linting run automatically in GitHub Actions
- Coverage is uploaded to Codecov

## Adding New Configs
- Document new config options here and in the relevant service README
