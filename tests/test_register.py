import pytest


def test_register_with_valid_details_returns_201(api):
    response = api.register()
    assert response.status_code == 201
    assert response.get_json() == {"username": "player1"}


@pytest.mark.parametrize("payload", [{}, {"username": "player1"}, {"password": "strongpass123"}])
def test_register_with_missing_fields_returns_400(api, payload):
    assert api.client.post("/register", json=payload).status_code == 400


def test_register_with_duplicate_username_returns_409(api):
    api.register("player1")
    assert api.register("player1").status_code == 409


@pytest.mark.xfail(strict=True, reason="BUG-001: username uniqueness check is case-sensitive")
def test_register_with_same_username_in_different_case_returns_409(api):
    api.register("Player1")
    assert api.register("player1").status_code == 409


def test_register_with_password_below_minimum_returns_400(api):
    assert api.register(password="seven77").status_code == 400


@pytest.mark.xfail(strict=True, reason="BUG-002: password of exactly the minimum length is rejected")
def test_register_with_password_of_exactly_minimum_length_returns_201(api):
    assert api.register(password="eight888").status_code == 201

def test_register_with_no_request_body_returns_400(api):
    assert api.client.post("/register").status_code == 400

def test_failed_duplicate_registration_does_not_overwrite_password(api):
    api.register("Player1", "Passw0rd!")
    assert api.register("Player1", "Different9!").status_code == 409  
    assert api.login("Player1", "Passw0rd!").status_code == 200        
    assert api.login("Player1", "Different9!").status_code == 401               

@pytest.mark.xfail(strict=True, reason="BUG-007: non-string usernames are converted to text")
@pytest.mark.parametrize("username", [None, 123, True, [], {}])
def test_register_with_non_string_username_returns_400(api, username):
    response = api.client.post("/register", json={"username": username, "password": "Passw0rd!"})
    assert response.status_code == 400