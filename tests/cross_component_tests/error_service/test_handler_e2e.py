from error_handler.handler import handle_error, error_catcher
import pytest

def test_e2e_error_handling():
    class Dummy:
        @error_catcher
        def fail(self):
            raise Exception("e2e test error")
    dummy = Dummy()
    with pytest.raises(Exception):
        dummy.fail()
    # Simulate error propagation and logging
    exc = Exception("direct error")
    result = handle_error(exc, context={"test": "e2e"})
    assert result["type"] == "Exception"
    assert result["message"] == "direct error"
