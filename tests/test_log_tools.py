"""The log tools should surface defects from production-style logs, not just from tests."""
import pytest

from tools.investigate import run
from tools.log_to_sqlite import load, parse_line
from tools.simulate_traffic import simulate


@pytest.fixture
def findings(tmp_path):
    log_path, db_path = tmp_path / "sample.log", tmp_path / "logs.db"
    simulate(str(log_path))
    assert load(str(log_path), str(db_path)) > 0
    return run(str(db_path))


def test_parse_line_extracts_fields():
    line = "2026-10-28 10:00:00,123 WARNING event=login_failed user=lumine session=- status=401 path=/login"
    row = parse_line(1, line)
    assert row[3:] == ("login_failed", "lumine", "-", 401, "/login")


def test_parse_line_ignores_unrelated_lines():
    assert parse_line(1, "Traceback (most recent call last):") is None


def test_failed_logins_are_counted_per_user(findings):
    assert ("lumine", 6) in findings["failed_logins_per_user"]


def test_server_errors_are_surfaced(findings):
    assert [row[2] for row in findings["server_errors"]] == ["/profile"]


def test_session_reuse_after_logout_is_detected(findings):
    rows = findings["session_used_after_logout"]
    assert len(rows) == 1
    assert rows[0][1] == "aether" and rows[0][3] == "profile_viewed"
