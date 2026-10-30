import pytest


def test_profile_with_valid_token_returns_username(api):
    token = api.login_token()
    response = api.profile(token)
    assert response.status_code == 200
    assert response.get_json() == {"username": "player1"}


def test_profile_without_authorization_header_returns_401(api):
    assert api.profile().status_code == 401


def test_profile_with_unknown_token_returns_401(api):
    assert api.profile("0" * 32).status_code == 401


@pytest.mark.xfail(strict=True, reason="BUG-005: malformed Authorization header causes a 500")
@pytest.mark.parametrize("header", ["Bearer", "not-a-bearer-token"])
def test_profile_with_malformed_header_returns_401(api, header):
    assert api.profile(header=header).status_code == 401


def test_logout_with_valid_token_returns_200(api):
    token = api.login_token()
    assert api.logout(token).status_code == 200


@pytest.mark.xfail(strict=True, reason="BUG-004: logout does not revoke the session token")
def test_token_is_rejected_after_logout(api):
    token = api.login_token()
    api.logout(token)
    assert api.profile(token).status_code == 401
