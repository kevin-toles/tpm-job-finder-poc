from src.error_service.handler import handle_error

def test_handle_error_multiple_types():
    for exc_type, msg in [(TypeError, "type error"), (IndexError, "index error"), (ZeroDivisionError, "zero division")]:
        exc = exc_type(msg)
        result = handle_error(exc, context={"test": "regression"})
        assert result["type"] == exc_type.__name__
        assert result["message"] == msg
