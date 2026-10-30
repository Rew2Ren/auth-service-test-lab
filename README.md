# Auth Service Test Lab

![tests](https://github.com/Rew2Ren/auth-service-test-lab/actions/workflows/tests.yml/badge.svg)

A small account service (register, login, profile, logout) with **seeded defects**, plus the tooling I built to find them: a requirements-based test suite, log analysis in SQL, and written bug reports judged from the player's perspective.

## What this project shows

- **Test design from requirements:** every test maps to a requirement in [`SPEC.md`](SPEC.md).
- **Known-defect tracking:** failing tests for confirmed bugs are marked `xfail(strict=True)`, so CI stays green. If a bug is fixed, the test flags it, which prompts a tracking update.
- **Log investigation with SQL:** `tools/` parses service logs into SQLite and runs queries that surface failures independently of the tests, such as session reuse after logout and server errors.
- **Bug reporting:** [`docs/bug-reports.md`](docs/bug-reports.md) covers steps to reproduce, expected and actual results, root cause, and severity and priority based on player impact.
- **AI-assisted testing:** [`docs/ai-test-review.md`](docs/ai-test-review.md) compares AI-generated test cases with my own and records where judgement was needed.

## Findings

| ID | Defect | Severity |
|----|--------|----------|
| BUG-004 | Logout does not revoke the session token | High |
| BUG-003 | Lockout triggers after six failed logins instead of five | High |
| BUG-005 | Malformed Authorization header causes a 500 error | Medium |
| BUG-001 | Usernames differing only by case can both be registered | Medium |
| BUG-002 | 8-character password rejected despite an 8-character minimum | Low |
| BUG-007 | Non-string usernames (e.g. `null`) are accepted as text | Medium |
| BUG-008 | Deeply nested JSON causes a 500 error | Medium |
| BUG-006 | Authorization scheme is not checked | Low |

## Run it

```bash
pip install -r requirements.txt
pytest -v                                         # 20 passed, 6 xfailed (known bugs)

python -m tools.simulate_traffic logs/sample.log  # generate realistic traffic
python -m tools.log_to_sqlite logs/sample.log logs.db
python -m tools.investigate logs.db               # run the SQL investigation queries
```

## Structure

```
app/service.py          Flask service under test
tests/                  pytest suite, grouped by feature
tools/                  log loader, SQL queries, traffic simulator
docs/                   bug reports and AI test review
SPEC.md                 requirements the tests are written against
```

## Next steps

- Add a mock third-party login provider (OAuth-style) and test the token exchange flow
- Run the API tests against the live server over HTTP, not just Flask's test client
- Fix the seeded bugs and turn the `xfail` tests into regression tests

**Tools:** Python, Flask, pytest, SQLite, GitHub Actions
