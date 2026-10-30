import pytest

from app.service import create_app

VALID_PASSWORD = "strongpass123"


class Api:
    """Thin wrapper so tests read like the requirements they check."""

    def __init__(self, client):
        self.client = client

    def register(self, username="player1", password=VALID_PASSWORD):
        return self.client.post("/register", json={"username": username, "password": password})

    def login(self, username="player1", password=VALID_PASSWORD):
        return self.client.post("/login", json={"username": username, "password": password})

    def login_token(self, username="player1", password=VALID_PASSWORD):
        self.register(username, password)
        return self.login(username, password).get_json()["token"]

    def profile(self, token=None, header=None):
        headers = {}
        if header is not None:
            headers["Authorization"] = header
        elif token is not None:
            headers["Authorization"] = f"Bearer {token}"
        return self.client.get("/profile", headers=headers)

    def logout(self, token):
        return self.client.post("/logout", headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "service.log"


@pytest.fixture
def api(log_file):
    return Api(create_app(str(log_file)).test_client())
