from src.error_service.handler import handle_error

def test_handle_error_basic():
    exc = ValueError("unit test error")
    context = {"test": "unit"}
    result = handle_error(exc, context)
    assert result["type"] == "ValueError"
    assert result["message"] == "unit test error"
    assert result["context"] == context

def test_handle_error_notify():
    exc = RuntimeError("notify test error")
    context = {"test": "notify"}
    result = handle_error(exc, context, notify=True)
    assert result["type"] == "RuntimeError"
    assert result["message"] == "notify test error"
    assert result["context"] == context
