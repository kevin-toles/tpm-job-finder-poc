from .base import LLMProvider
import requests

class OpenAIProvider(LLMProvider):
    """Adapter for OpenAI's ChatGPT API."""
    def get_signals(self, prompt: str) -> dict:
        if not self.api_key:
            return {"error": "No API key provided"}
        # Example minimal request (update for your use case)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 429:
                return {"provider": "ChatGPT", "error": "Rate limit or quota exceeded"}
            resp.raise_for_status()
            result = resp.json()
            # Extract score/rationale from result (customize as needed)
            content = result["choices"][0]["message"]["content"]
            return {"provider": "ChatGPT", "response": content}
        except Exception as e:
            from src.error_service.handler import handle_error
            handle_error(e, context={'component': 'openai_provider', 'method': 'get_signals', 'prompt': prompt})
            return {"provider": "ChatGPT", "error": str(e)}
