from src.llm_provider.openai_provider import OpenAIProvider

def test_openai_provider_with_key():
    provider = OpenAIProvider(api_key="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")
    prompt = "Say hello!"
    result = provider.get_signals(prompt)
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "ChatGPT"
    assert "response" in result or "error" in result

def test_openai_provider_no_key():
    provider = OpenAIProvider(api_key=None)
    prompt = "Say hello!"
    result = provider.get_signals(prompt)
    assert result["error"] == "No API key provided"
