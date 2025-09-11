from .base import LLMProvider
import requests

class OllamaProvider(LLMProvider):
    """Adapter for local Ollama server."""
    def get_signals(self, prompt: str) -> dict:
        # Ollama does not require an API key
        url = "http://localhost:11434/api/generate"
        data = {"model": "llama2", "prompt": prompt}
        try:
            resp = requests.post(url, json=data, timeout=30)
            if resp.status_code == 429:
                return {"provider": "Ollama", "error": "Rate limit or quota exceeded"}
            resp.raise_for_status()
            result = resp.json()
            return {"provider": "Ollama", "response": result.get("response", "")}
        except Exception as e:
            from error_handler.handler import handle_error
            handle_error(e, context={'component': 'ollama_provider', 'method': 'get_signals', 'prompt': prompt})
            return {"provider": "Ollama", "error": str(e)}
