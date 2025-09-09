import pytest
import os
from src.llm_provider.openai_provider import OpenAIProvider
from src.poc.utils.api_key_loader import load_api_keys
api_keys = load_api_keys()
key = api_keys.get("OPENAI_API_KEY")
print(f"DEBUG: Found OPENAI_API_KEY: {repr(key)}")

def test_chatgpt_hello_world():
    if not key:
        pytest.skip("No ChatGPT API key found in environment or llm_keys.txt")
    provider = OpenAIProvider(api_key=key)
    prompt = "confirm successful call"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "ChatGPT"
    assert "response" in result or "error" in result
    print("ChatGPT response:", result.get("response", result.get("error")))
