from src.llm_provider.adapter import LLMAdapter

def test_llm_regression_rate_limit():
    adapter = LLMAdapter()
    prompt = "Trigger rate limit test."
    results = adapter.score_job(prompt)
    # Regression: Ensure error is handled gracefully
    for res in results.values():
        assert "error" in res or "response" in res
