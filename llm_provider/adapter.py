from config.config import Config
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider

class LLMAdapter:
    """Main entrypoint for scoring jobs with multiple LLMs."""
    def __init__(self):
        self.providers = self._load_providers()

    def _load_providers(self):
        providers = []
        # ChatGPT (OpenAI)
        chatgpt_key = Config.get("OPENAI_API_KEY")
        if chatgpt_key:
            providers.append(OpenAIProvider(api_key=chatgpt_key))
        # Ollama (toggle via OLLAMA_ENABLED)
        ollama_enabled = Config.get("OLLAMA_ENABLED", "false").lower()
        if ollama_enabled == "true":
            providers.append(OllamaProvider())
        # Anthropic
        anthropic_key = Config.get("ANTHROPIC_API_KEY")
        if anthropic_key:
            from .anthropic_provider import AnthropicProvider
            providers.append(AnthropicProvider(api_key=anthropic_key))
        # Gemini
        gemini_key = Config.get("GEMINI_API_KEY")
        if gemini_key:
            from .gemini_provider import GeminiProvider
            providers.append(GeminiProvider(api_key=gemini_key))
        # DeepSeek
        deepseek_key = Config.get("DEEPSEEK_API_KEY")
        if deepseek_key:
            from .deepseek_provider import DeepSeekProvider
            providers.append(DeepSeekProvider(api_key=deepseek_key))
        return providers

    def score_job(self, prompt: str) -> dict:
        results = {}
        for provider in self.providers:
            res = provider.get_signals(prompt)
            # Fallback: if error, log and continue
            if res.get("error"):
                # Optionally log error here
                results[res.get("provider", provider.__class__.__name__)] = {"error": res["error"]}
            else:
                results[res.get("provider", provider.__class__.__name__)] = res
        return results
