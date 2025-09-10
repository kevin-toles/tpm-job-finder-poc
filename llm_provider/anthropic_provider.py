from .base import LLMProvider
import requests

class AnthropicProvider(LLMProvider):
    """Adapter for Anthropic Claude API (Messages endpoint)."""
    def get_signals(self, prompt: str) -> dict:
        if not self.api_key:
            return {"provider": "Anthropic", "error": "No API key provided"}
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": "claude-sonnet-4-20250514",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 429:
                return {"provider": "Anthropic", "error": "Rate limit or quota exceeded"}
            resp.raise_for_status()
            result = resp.json()
            # Extract reply from content array
            content = " ".join([c.get("text", "") for c in result.get("content", [])])
            return {"provider": "Anthropic", "response": content}
        except Exception as e:
            from error_handler.handler import handle_error
            handle_error(e, context={'component': 'anthropic_provider', 'method': 'get_signals', 'prompt': prompt})
            return {"provider": "Anthropic", "error": str(e)}
