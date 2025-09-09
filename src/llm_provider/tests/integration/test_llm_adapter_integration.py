import pytest
from src.llm_provider.adapter import LLMAdapter

def test_llm_adapter_integration_chatgpt():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    if "ChatGPT" not in results:
        pytest.skip("ChatGPT provider not enabled/configured.")
    assert "ChatGPT" in results
    assert "response" in results["ChatGPT"] or "error" in results["ChatGPT"]

def test_llm_adapter_integration_ollama():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    if "Ollama" not in results:
        pytest.skip("Ollama provider not enabled/configured.")
    assert "Ollama" in results
    assert "response" in results["Ollama"] or "error" in results["Ollama"]

def test_llm_adapter_integration_anthropic():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    if "Anthropic" not in results:
        pytest.skip("Anthropic provider not enabled/configured.")
    assert "Anthropic" in results
    assert "response" in results["Anthropic"] or "error" in results["Anthropic"]

def test_llm_adapter_integration_gemini():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    if "Gemini" not in results:
        pytest.skip("Gemini provider not enabled/configured.")
    assert "Gemini" in results
    assert "response" in results["Gemini"] or "error" in results["Gemini"]

def test_llm_adapter_integration_deepseek():
    adapter = LLMAdapter()
    prompt = "Score this job for fit: Senior TPM at Acme Corp, remote, $150k."
    results = adapter.score_job(prompt)
    if "DeepSeek" not in results:
        pytest.skip("DeepSeek provider not enabled/configured.")
    assert "DeepSeek" in results
    assert "response" in results["DeepSeek"] or "error" in results["DeepSeek"]
