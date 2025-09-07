import pytest
import os
from src.llm_provider.gemini_provider import GeminiProvider

def get_api_key():
    key = None
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "llm_keys.txt")
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                if line.strip().startswith("GEMINI:"):
                    key = line.split(":", 1)[1].strip()
    return key

def test_gemini_hello_world():
    api_key = get_api_key()
    if not api_key:
        pytest.skip("No Gemini API key found in llm_keys.txt")
    provider = GeminiProvider(api_key=api_key)
    prompt = "confirm successful call"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "Gemini"
    assert "response" in result or "error" in result
    print("Gemini response:", result.get("response", result.get("error")))
    prompt = "confirm successful call"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "Gemini"
    assert "response" in result or "error" in result
    print("Gemini response:", result.get("response", result.get("error")))
