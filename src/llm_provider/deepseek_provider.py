from .base import LLMProvider
import requests

class DeepSeekProvider(LLMProvider):
    """Adapter for DeepSeek OpenAI-compatible API."""
    def get_signals(self, prompt: str) -> dict:
        if not self.api_key:
            return {"provider": "DeepSeek", "error": "No API key provided"}
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 429:
                return {"provider": "DeepSeek", "error": "Rate limit or quota exceeded"}
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"] if result.get("choices") else ""
            return {"provider": "DeepSeek", "response": content}
        except Exception as e:
            return {"provider": "DeepSeek", "error": str(e)}
