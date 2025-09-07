import pytest
from src.llm_provider.ollama_provider import OllamaProvider

def test_ollama_hello_world():
    provider = OllamaProvider()
    prompt = "confirm successful call"
    result = provider.get_signals(prompt)
    if result.get("error") and "Connection refused" in result["error"]:
        pytest.skip("Ollama server not running on localhost:11434")
    assert isinstance(result, dict)
    assert "provider" in result
    assert result["provider"] == "Ollama"
    assert "response" in result or "error" in result
    print("Ollama response:", result.get("response", result.get("error")))
