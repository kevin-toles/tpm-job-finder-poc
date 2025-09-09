import pytest
from src.llm_provider.deepseek_provider import DeepSeekProvider
from src.poc.utils.api_key_loader import load_api_keys

def test_deepseek_hello_world():
    api_keys = load_api_keys()
    api_key = api_keys.get("DEEPSEEK_API_KEY")
    print(f"DEBUG: Found DEEPSEEK_API_KEY: {repr(api_key)}")
    if not api_key:
        pytest.skip("No DeepSeek API key found in api_keys.json")
    provider = DeepSeekProvider(api_key=api_key)
    prompt = "confirm successful call"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "DeepSeek"
    assert "response" in result or "error" in result
    print("DeepSeek response:", result.get("response", result.get("error")))
    prompt = "confirm successful call"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "DeepSeek"
    assert "response" in result or "error" in result
    print("DeepSeek response:", result.get("response", result.get("error")))
