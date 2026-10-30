"""A small account service used as a test target.

The service intentionally contains seeded defects. The test suite, the log
analysis tools and docs/bug-reports.md document how each one was found.
"""
import logging
import os
import secrets

from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

MAX_FAILED_ATTEMPTS = 5
MIN_PASSWORD_LENGTH = 8


def _build_logger(log_path):
    logger = logging.getLogger(f"auth_service.{secrets.token_hex(4)}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(log_path) if log_path else logging.NullHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def create_app(log_path=None):
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = False

    users = {}
    sessions = {}
    log = _build_logger(log_path)

    def record(level, event, status, user="-", session="-"):
        log.log(
            level,
            "event=%s user=%s session=%s status=%s path=%s",
            event, user or "-", session, status, request.path,
        )

    def credentials():
        data = request.get_json(silent=True) or {}
        return str(data.get("username", "")).strip(), str(data.get("password", ""))

    def token_from_header():
        header = request.headers.get("Authorization")
        if header is None:
            return None
        return header.split(" ")[1]

    @app.post("/register")
    def register():
        username, password = credentials()
        if not username or not password:
            record(logging.WARNING, "register_rejected", 400, username)
            return jsonify(error="username and password are required"), 400
        if username in users:
            record(logging.WARNING, "register_rejected", 409, username)
            return jsonify(error="username already taken"), 409
        if len(password) <= MIN_PASSWORD_LENGTH:
            record(logging.WARNING, "register_rejected", 400, username)
            return jsonify(error=f"password must be at least {MIN_PASSWORD_LENGTH} characters"), 400

        users[username] = {"hash": generate_password_hash(password), "failed": 0, "locked": False}
        record(logging.INFO, "registered", 201, username)
        return jsonify(username=username), 201

    @app.post("/login")
    def login():
        username, password = credentials()
        user = users.get(username)
        if user is None:
            record(logging.WARNING, "login_failed", 401, username)
            return jsonify(error="invalid username or password"), 401
        if user["locked"]:
            record(logging.WARNING, "login_blocked", 423, username)
            return jsonify(error="account locked"), 423
        if not check_password_hash(user["hash"], password):
            user["failed"] += 1
            if user["failed"] > MAX_FAILED_ATTEMPTS:
                user["locked"] = True
            record(logging.WARNING, "login_failed", 401, username)
            return jsonify(error="invalid username or password"), 401

        user["failed"] = 0
        token = secrets.token_hex(16)
        sessions[token] = username
        record(logging.INFO, "login_success", 200, username, token[:8])
        return jsonify(token=token), 200

    @app.get("/profile")
    def profile():
        token = token_from_header()
        username = sessions.get(token) if token else None
        if username is None:
            record(logging.WARNING, "profile_denied", 401)
            return jsonify(error="authentication required"), 401
        record(logging.INFO, "profile_viewed", 200, username, token[:8])
        return jsonify(username=username), 200

    @app.post("/logout")
    def logout():
        token = token_from_header()
        username = sessions.get(token) if token else None
        if username is None:
            record(logging.WARNING, "logout_denied", 401)
            return jsonify(error="authentication required"), 401
        record(logging.INFO, "logout", 200, username, token[:8])
        return jsonify(message="logged out"), 200

    @app.errorhandler(500)
    def server_error(_err):
        record(logging.ERROR, "server_error", 500)
        return jsonify(error="internal server error"), 500

    return app


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    create_app("logs/service.log").run(debug=False)
