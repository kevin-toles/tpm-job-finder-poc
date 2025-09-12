from .base import LLMProvider
import requests

class GeminiProvider(LLMProvider):
    """Adapter for Google Gemini Generative Language API."""
    def get_signals(self, prompt: str) -> dict:
        if not self.api_key:
            return {"provider": "Gemini", "error": "No API key provided"}
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-bison:generateMessage?key=" + self.api_key
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": {
                "messages": [
                    {"content": prompt}
                ]
            },
            "temperature": 0.7,
            "candidate_count": 1
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 429:
                return {"provider": "Gemini", "error": "Rate limit or quota exceeded"}
            resp.raise_for_status()
            result = resp.json()
            candidates = result.get("candidates", [])
            content = candidates[0].get("content", "") if candidates else ""
            return {"provider": "Gemini", "response": content}
        except Exception as e:
            from tpm_job_finder_poc.error_handler.handler import handle_error
            handle_error(e, context={'component': 'gemini_provider', 'method': 'get_signals', 'prompt': prompt})
            return {"provider": "Gemini", "error": str(e)}
