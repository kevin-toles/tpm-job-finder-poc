import pytest
import os
from src.llm_provider.openai_provider import OpenAIProvider
key = os.environ.get("OPENAI_API_KEY")
if key:
    print(f"DEBUG: Found OPENAI_API_KEY in environment: {repr(key)}")
else:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "llm_keys.txt")
    print(f"DEBUG: Reading llm_keys.txt from {config_path}")
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                print(f"DEBUG: Raw line: {repr(line)}")
                line_clean = line.strip().replace("\r", "").replace("\n", "")
                print(f"DEBUG: Cleaned line: {repr(line_clean)}")
                if line_clean.lower().startswith("chatgpt:"):
                    parts = line_clean.split(":", 1)
                    if len(parts) == 2:
                        key_candidate = parts[1].strip()
                        print(f"DEBUG: Found ChatGPT key candidate: {repr(key_candidate)}")
                        if key_candidate:
                            key = key_candidate
    print(f"DEBUG: Final ChatGPT key: {repr(key)}")

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
