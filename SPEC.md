# Account Service Requirements

The test suite is derived from these requirements. Each test name maps to one of them.

| ID | Requirement |
|----|-------------|
| R1 | `POST /register` creates an account and returns `201` when both username and password are supplied. Missing fields return `400`. |
| R2 | Usernames are unique regardless of letter case (`Player1` and `player1` are the same name). A duplicate returns `409`. |
| R3 | Passwords must be **at least 8 characters**. Shorter passwords return `400`. |
| R4 | `POST /login` returns `200` and a session token for valid credentials. |
| R5 | An unknown username and a wrong password return the same `401` response, so attackers cannot discover which accounts exist. |
| R6 | After **5** consecutive failed logins the account locks, and further logins return `423` even with the correct password. A successful login resets the counter. |
| R7 | `GET /profile` returns `200` with a valid `Authorization: Bearer <token>` header. Missing, unknown or malformed tokens return `401`. |
| R8 | `POST /logout` revokes the token, so it can no longer be used. |
| R9 | The service never returns a `5xx` error in response to client input. |
