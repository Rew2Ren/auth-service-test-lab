"""R9: the service must never return a 5xx error in response to client input."""
import pytest


@pytest.mark.xfail(strict=True, reason="BUG-008: deeply nested JSON causes a 500")
def test_deeply_nested_json_does_not_cause_server_error(api):
    body = "[" * 10000 + "]" * 10000                                  
    response = api.client.post("/register", data=body, content_type="application/json")
    assert response.status_code < 500     