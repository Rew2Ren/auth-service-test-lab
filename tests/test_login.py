import pytest


def fail_login(api, times, username="player1"):
    for _ in range(times):
        api.login(username, "wrong-password")


def test_login_with_valid_credentials_returns_token(api):
    api.register()
    response = api.login()
    assert response.status_code == 200
    assert len(response.get_json()["token"]) == 32


def test_login_with_wrong_password_returns_401(api):
    api.register()
    assert api.login(password="wrong-password").status_code == 401


def test_unknown_user_gets_same_error_as_wrong_password(api):
    """Identical responses stop attackers from discovering which usernames exist."""
    api.register()
    unknown = api.login("nobody", "whatever123")
    wrong = api.login("player1", "wrong-password")
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.get_json() == wrong.get_json()


def test_successful_login_resets_failed_attempt_counter(api):
    api.register()
    fail_login(api, 4)
    assert api.login().status_code == 200
    fail_login(api, 4)
    assert api.login().status_code == 200


@pytest.mark.xfail(strict=True, reason="BUG-003: account locks after six failures instead of five")
def test_account_locks_after_five_failed_attempts(api):
    api.register()
    fail_login(api, 5)
    assert api.login().status_code == 423


def test_locked_account_rejects_correct_password(api):
    api.register()
    fail_login(api, 6)
    assert api.login().status_code == 423
