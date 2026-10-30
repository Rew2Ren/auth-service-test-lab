"""Drive scripted player sessions through the service to produce a realistic sample log.

Usage: python -m tools.simulate_traffic logs/sample.log
"""
import argparse
import os

from app.service import create_app


def simulate(log_path):
    client = create_app(log_path).test_client()

    def post(path, body=None, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        return client.post(path, json=body, headers=headers)

    # A normal player: register, log in, check profile, log out, then reuse the old token.
    post("/register", {"username": "aether", "password": "travellerpass1"})
    token = post("/login", {"username": "aether", "password": "travellerpass1"}).get_json()["token"]
    client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    post("/logout", token=token)
    client.get("/profile", headers={"Authorization": f"Bearer {token}"})

    # Someone guessing passwords against another account.
    post("/register", {"username": "lumine", "password": "travellerpass2"})
    for guess in ["123456", "password", "lumine123", "qwerty", "letmein", "abyss"]:
        post("/login", {"username": "lumine", "password": guess})

    # A client sending a malformed Authorization header.
    client.get("/profile", headers={"Authorization": "Bearer"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_path")
    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.log_path) or ".", exist_ok=True)
    simulate(args.log_path)
    print(f"Sample traffic written to {args.log_path}")


if __name__ == "__main__":
    main()
