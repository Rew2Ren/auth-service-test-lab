# Bug Reports

Severity reflects technical impact. Priority reflects what a player would actually experience, and how urgently it needs fixing before release.

| ID | Title | Severity | Priority | Found by |
|----|-------|----------|----------|----------|
| BUG-004 | Logout does not revoke the session token | High | P1 | Test + log query |
| BUG-003 | Account locks after six failed logins instead of five | High | P1 | Test |
| BUG-005 | Malformed Authorization header causes a server error | Medium | P2 | Test + log query |
| BUG-001 | Duplicate usernames allowed when letter case differs | Medium | P2 | Test |
| BUG-002 | Password of exactly the minimum length is rejected | Low | P3 | Test |
| BUG-007 | Non-string usernames are accepted and converted to text | Medium | P2 | AI-suggested test (R9-03) |
| BUG-008 | Deeply nested JSON causes a server error | Medium | P2 | AI-suggested test (R9-05) |
| BUG-006 | Authorization scheme is not checked | Low | P3 | AI-suggested test (R7-07) |
---

## BUG-004: Logout does not revoke the session token

**Requirement:** R8
**Steps to reproduce**
1. Register and log in as `player1`, and keep the returned token.
2. `POST /logout` with that token. The response is `200`.
3. `GET /profile` with the same token.

**Expected:** `401`
**Actual:** `200`, with the profile returned

**Player impact:** A player who logs out on a shared or public device is still logged in for anyone holding the token. That puts their account, purchases and progress at risk.
**Root cause:** `logout()` logs the event but never removes the token from `sessions`.
**Evidence:** `test_token_is_rejected_after_logout`, and the `session_used_after_logout` query in `tools/queries.sql`.

## BUG-003: Account locks after six failed logins instead of five

**Requirement:** R6
**Steps to reproduce:** Register, send 5 logins with a wrong password, then log in with the correct password.
**Expected:** `423` (locked)
**Actual:** `200`

**Player impact:** Attackers get one extra password guess per account than the security policy allows.
**Root cause:** Off-by-one comparison: `failed > MAX_FAILED_ATTEMPTS` should be `>=`.
**Evidence:** `test_account_locks_after_five_failed_attempts`

## BUG-005: Malformed Authorization header causes a server error

**Requirement:** R7, R9
**Steps to reproduce:** `GET /profile` with the header `Authorization: Bearer` (no token).
**Expected:** `401`
**Actual:** `500`

**Player impact:** A buggy client or third-party tool crashes the request instead of getting a clear error. At scale, this adds noise to error monitoring and can hide real incidents.
**Root cause:** `token_from_header()` indexes `split(" ")[1]` without checking the header format.
**Evidence:** `test_profile_with_malformed_header_returns_401`, and the `server_errors` query.

## BUG-001: Duplicate usernames allowed when letter case differs

**Requirement:** R2
**Steps to reproduce:** Register `Player1`, then register `player1`.
**Expected:** `409`
**Actual:** `201`

**Player impact:** Players can impersonate others with look-alike names, and support staff cannot reliably tell accounts apart.
**Root cause:** The uniqueness check compares raw strings instead of normalised (lowercased) usernames.
**Evidence:** `test_register_with_same_username_in_different_case_returns_409`

## BUG-002: Password of exactly the minimum length is rejected

**Requirement:** R3
**Steps to reproduce:** Register with an 8-character password.
**Expected:** `201`
**Actual:** `400`, with the error message saying "at least 8 characters"

**Player impact:** A confusing sign-up experience: the error message contradicts the input the player gave. This could lose new players at registration.
**Root cause:** Off-by-one comparison: `len(password) <= MIN_PASSWORD_LENGTH` should be `<`.
**Evidence:** `test_register_with_password_of_exactly_minimum_length_returns_201`

## BUG-006: Authorization scheme is not checked

**Requirement:** R7
**Steps to reproduce**
1. Register and log in as `player1`, and keep the returned token.
2. `GET /profile` with the header `Authorization: Basic <token>`.

**Expected:** `401`, because only the `Bearer` scheme is valid
**Actual:** `200`, with the profile returned

**Player impact:** Low direct risk, since a valid token is still needed. But the service accepts headers that the spec says are malformed. If another component, such as a gateway or logging tool, treats non-Bearer headers differently, the two could disagree about who is authenticated.
**Root cause:** `token_from_header()` takes the second word of the Authorization header without checking that the first word is `Bearer`.
**Evidence:** `test_profile_with_wrong_auth_scheme_returns_401`. Found by an AI-suggested test case (R7-07), see `docs/ai-test-review.md`.

## BUG-007: Non-string usernames are accepted and converted to text

**Requirement:** R1. The spec doesn't define a status for wrong field types (AI review question Q3). I chose `400` because a username that isn't text has not been validly supplied.
**Steps to reproduce:** `POST /register` with `{"username": null, "password": "Passw0rd!"}`. Repeat with `123`, `true`, `[]` and `{}`.

**Expected:** `400`
**Actual:** `201`. Accounts are created with the literal usernames "None", "123", "True", "[]" and "{}".

**Player impact:** A buggy game client or third-party tool can silently create junk accounts. A player might then appear in-game or in support tools as "None", which is confusing and hard to clean up.
**Root cause:** `credentials()` converts any value to text with `str()` before validating it, so non-string values become non-empty usernames that pass the empty check.
**Evidence:** `test_register_with_non_string_username_returns_400` (5 cases). Found by an AI-suggested test case (R9-03).

## BUG-008: Deeply nested JSON causes a server error

**Requirement:** R9
**Steps to reproduce:** `POST /register` with `Content-Type: application/json` and a body of 10,000 `[` characters followed by 10,000 `]` characters.

**Expected:** a `4xx` error. R9 requires anything other than `5xx`.
**Actual:** `500`

**Player impact:** Anyone can trigger server errors at will with a single small request, no account needed. At scale, this adds noise to error monitoring and could hide real incidents.
**Root cause:** Python's JSON parser exceeds its recursion limit (about 1,000 levels) on deeply nested input and raises `RecursionError`. `request.get_json(silent=True)` only suppresses invalid-JSON errors, so the exception goes unhandled.
**Evidence:** `test_deeply_nested_json_does_not_cause_server_error`. Found by an AI-suggested test case (R9-05).