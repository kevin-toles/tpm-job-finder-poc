import pytest
from src.llm_provider.gemini_provider import GeminiProvider
from src.poc.utils.api_key_loader import load_api_keys

def test_gemini_hello_world():
    api_keys = load_api_keys()
    api_key = api_keys.get("GEMINI_API_KEY")
    print(f"DEBUG: Found GEMINI_API_KEY: {repr(api_key)}")
    if not api_key:
        pytest.skip("No Gemini API key found in api_keys.json")
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
