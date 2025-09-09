import pytest
from src.llm_provider.anthropic_provider import AnthropicProvider
from src.poc.utils.api_key_loader import load_api_keys


def test_anthropic_hello_world():
    try:
        api_keys = load_api_keys()
    except FileNotFoundError:
        pytest.skip("No Anthropic API key found in api_keys.txt or environment variables")
    key = api_keys.get("ANTHROPIC_API_KEY")
    print(f"DEBUG: Found ANTHROPIC_API_KEY: {repr(key)}")
    if not key:
        pytest.skip("No Anthropic API key found in api_keys.txt or environment variables")
    provider = AnthropicProvider(api_key=key)
    prompt = "Hello, world"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "Anthropic"
    assert "response" in result or "error" in result
    print("Anthropic response:", result.get("response", result.get("error")))
