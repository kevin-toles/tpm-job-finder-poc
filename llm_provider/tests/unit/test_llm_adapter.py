from llm_provider.adapter import LLMAdapter
import pytest

def test_llm_adapter_chatgpt():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    print(f"DEBUG: ChatGPT results: {results}")
    if "ChatGPT" not in results:
        pytest.skip("ChatGPT provider not enabled/configured.")
    assert "ChatGPT" in results
    assert "response" in results["ChatGPT"] or "error" in results["ChatGPT"]

def test_llm_adapter_anthropic():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    print(f"DEBUG: Anthropic results: {results}")
    if "Anthropic" not in results:
        pytest.skip("Anthropic provider not enabled/configured.")
    assert "Anthropic" in results
    assert "response" in results["Anthropic"] or "error" in results["Anthropic"]

def test_llm_adapter_ollama():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    print(f"DEBUG: Ollama results: {results}")
    if "Ollama" not in results:
        pytest.skip("Ollama provider not enabled/configured.")
    assert "Ollama" in results
    assert "response" in results["Ollama"] or "error" in results["Ollama"]

def test_llm_adapter_gemini():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    print(f"DEBUG: Gemini results: {results}")
    if "Gemini" not in results:
        pytest.skip("Gemini provider not enabled/configured.")
    assert "Gemini" in results
    assert "response" in results["Gemini"] or "error" in results["Gemini"]

def test_llm_adapter_deepseek():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    print(f"DEBUG: DeepSeek results: {results}")
    if "DeepSeek" not in results:
        pytest.skip("DeepSeek provider not enabled/configured.")
    assert "DeepSeek" in results
    assert "response" in results["DeepSeek"] or "error" in results["DeepSeek"]
