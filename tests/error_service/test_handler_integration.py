from error_handler.handler import handle_error, error_catcher
import pytest

def test_error_catcher_decorator():
    @error_catcher
    def will_fail():
        raise KeyError("integration test error")
    with pytest.raises(KeyError):
        will_fail()
