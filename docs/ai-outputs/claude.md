# AI Test Design Output

**Tool:** [claude]
**Date:** 30 October 2026
**Prompt:** as recorded in [`ai-test-review.md`](../ai-test-review.md)

> Raw output from the tool, reformatted as Markdown only. The wording is unchanged.

---

Test cases derived only from requirements R1 to R9. Security inputs were informed by the Node.js rule set in fcerullo-cycubix/secure-ai-rules (`src/rules/nodejs-security.ts`), but every expected result comes from R1 to R9. Anything the requirements don't cover is listed under Questions.

## Requirements under test

| ID | Requirement |
|----|-------------|
| R1 | `POST /register` creates an account and returns 201 when both username and password are supplied. Missing fields return 400. |
| R2 | Usernames are unique regardless of letter case (`Player1` and `player1` are the same name). A duplicate returns 409. |
| R3 | Passwords must be at least 8 characters. Shorter passwords return 400. |
| R4 | `POST /login` returns 200 and a session token for valid credentials. |
| R5 | An unknown username and a wrong password return the same 401 response, so attackers cannot discover which accounts exist. |
| R6 | After 5 consecutive failed logins the account locks, and further logins return 423 even with the correct password. A successful login resets the counter. |
| R7 | `GET /profile` returns 200 with a valid `Authorization: Bearer <token>` header. Missing, unknown or malformed tokens return 401. |
| R8 | `POST /logout` revokes the token, so it can no longer be used. |
| R9 | The service never returns a 5xx error in response to client input. |

## Conventions

- Each test starts from a fresh service with no accounts unless stated.
- `reg(u, p)` means `POST /register` with body `{"username": u, "password": p}`.
- `login(u, p)` means `POST /login` with the same body.
- `profile(h)` means `GET /profile` with header `Authorization: h`.
- The requirements don't say requests are JSON or name the fields exactly, so the body format above is a working assumption (see Q1).
- Default account: `tester01` / `Passw0rd!` (9 characters). Default wrong password: `WrongPass1`.
- The ID prefix is the requirement covered. A second requirement in brackets means the test also checks it.
- Types: P = positive, N = negative, E = edge, S = security-driven negative.

## R1: Registration and required fields

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R1-01 | P | reg with both fields | `tester01` / `Passw0rd!` | 201 |
| R1-02 | P | 1) R1-01 2) login with same credentials | as R1-01 | Login returns 200 with a token, which shows the account was actually created [R4] |
| R1-03 | N | reg with username omitted | `{"password":"Passw0rd!"}` | 400 |
| R1-04 | N | reg with password omitted | `{"username":"tester01"}` | 400 |
| R1-05 | N | reg with empty object | `{}` | 400 |
| R1-06 | N | `POST /register` with no body | none | 400 |
| R1-07 | N | 1) reg with password omitted 2) reg same username with valid password | `ghost01`, then `ghost01` / `Passw0rd!` | Step 1: 400. Step 2: 201. A 409 at step 2 means the rejected request created an account |

## R2: Case-insensitive unique usernames

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R2-01 | N | Register the same name twice | `Player1` / `Passw0rd!` twice | 201, then 409 |
| R2-02 | N | Register, then lowercase variant | `Player1`, then `player1` | 201, then 409 |
| R2-03 | N | Register, then uppercase variant | `Player1`, then `PLAYER1` | 201, then 409 |
| R2-04 | N | Register, then mixed-case variant | `player1`, then `pLaYeR1` | 201, then 409 |
| R2-05 | P | Register two different names | `Player1`, then `Player2` | 201, 201 |
| R2-06 | N | Duplicate name with a different password | `Player1` / `Passw0rd!`, then `player1` / `Different9!` | 201, then 409 |
| R2-07 | N | 1) R2-06 2) `login("Player1","Passw0rd!")` 3) `login("Player1","Different9!")` | as listed | Step 2: 200. Step 3: 401. The duplicate attempt must not overwrite the original password [R4, R5] |
| R2-08 | E | Send `reg("Racer01")` and `reg("RACER01")` at the same moment. Repeat 20 times with fresh names | valid passwords | Each pair gives exactly one 201 and one 409, never two 201s, never a 5xx [R9] |

## R3: Minimum password length

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R3-01 | E | reg with 7-character password | `Abc123!` | 400 |
| R3-02 | E | reg with 8-character password | `Abc1234!` | 201 |
| R3-03 | E | reg with 9-character password | `Abc12345!` | 201 |
| R3-04 | N | reg with 1-character password | `a` | 400 |
| R3-05 | N | reg with empty password | `""` | 400 (either "missing" under R1 or "too short" under R3, both 400) |
| R3-06 | P | reg with long password | `A` repeated 64 times | 201 (no maximum is stated) |
| R3-07 | P | reg with 8 symbols | `!@#$%^&*` | 201 |
| R3-08 | N | 1) `reg("short01","Abc123!")` 2) `reg("short01","Abc1234!")` | as listed | 400, then 201. The rejected request created nothing |
| R3-09 | P | 1) R3-02 2) login with `Abc1234!` | as R3-02 | 200 with token [R4] |

## R4: Successful login

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R4-01 | P | Register default, then login | default | 200, response contains a non-empty session token |
| R4-02 | P | 1) R4-01 2) `profile("Bearer " + token)` | token from step 1 | 200 [R7] |
| R4-03 | P | Log in twice in a row | default | Both 200, each with a token (whether both stay valid is Q11) |
| R4-04 | N | login with wrong password | `tester01` / `WrongPass1` | 401, no token [R5] |
| R4-05 | S | login with password as a NoSQL operator object | `{"username":"tester01","password":{"$ne":null}}` | Not 200, no token, not 5xx (exact code is Q3/Q9) [R9] |
| R4-06 | S | login with operator objects in both fields, account exists | `{"username":{"$gt":""},"password":{"$gt":""}}` | Not 200, no token, not 5xx [R9] |
| R4-07 | S | login with SQL injection in username | `tester01' OR '1'='1` / `x` | 401 (string credentials that match no account) [R5] |
| R4-08 | S | login with SQL injection in password | `tester01` / `' OR '1'='1` | 401 [R5] |

## R5: No account enumeration

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R5-01 | N | login with unknown username | `nosuchuser` / `Passw0rd!` | 401 |
| R5-02 | N | login with known username, wrong password | `tester01` / `WrongPass1` | 401 |
| R5-03 | N | Capture full responses of R5-01 and R5-02 and diff them | as above | Same status and same body. Headers match apart from per-request values such as Date (scope is Q12) |
| R5-04 | E | login with unknown username 6 times | `nosuchuser` / `WrongPass1` | 401 every time, never 423 [R6] |

## R6: Lockout after 5 failures

All use the default account unless stated.

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R6-01 | N | 5 wrong logins, then correct login | `WrongPass1` x5, then `Passw0rd!` | Attempts 1 to 5: 401. Attempt 6: 423 |
| R6-02 | E | 4 wrong logins, then correct login | `WrongPass1` x4, then `Passw0rd!` | 401 x4, then 200 (not locked at 4) |
| R6-03 | P | 4 wrong, correct, 4 wrong, correct | as listed | 200 at attempts 5 and 10, which shows the success reset the counter |
| R6-04 | N | 4 wrong, correct, 5 wrong, correct | as listed | Attempt 5: 200. Attempt 11: 423 (reset, then locks again) |
| R6-05 | N | Lock the account, then wrong password | 5 x `WrongPass1`, then `WrongPass1` | 423 |
| R6-06 | N | Lock the account, then correct password 3 more times | `Passw0rd!` x3 | 423 each time (lock duration is Q14) |
| R6-07 | P | 1) Register B (`tester02` / `Passw0rd!`) 2) Lock A 3) login B | as listed, all from the same client IP | 200 for B. The lock is per account |
| R6-08 | E | Send 10 wrong logins concurrently, then one correct login | `WrongPass1` x10 | Each concurrent response is 401 or 423, none 5xx. Final login: 423 [R9] |

## R7: Profile access with bearer token

Setup: default account logged in, token `T`.

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R7-01 | P | profile with valid token | `Bearer T` | 200 |
| R7-02 | N | `GET /profile` with no Authorization header | none | 401 |
| R7-03 | N | Empty header value | `""` | 401 |
| R7-04 | N | Scheme only | `Bearer` | 401 |
| R7-05 | N | Scheme with trailing space, no token | `Bearer ` | 401 |
| R7-06 | N | Token without scheme | `T` | 401 |
| R7-07 | N | Wrong scheme | `Basic T` | 401 |
| R7-08 | N | Tampered token | `T` with its last character changed | 401 |
| R7-09 | N | Unknown token of the same length | random string, same length as `T` | 401 |
| R7-10 | N | Token with extra characters | `Bearer T` + `x` | 401 |
| R7-11 | S | Injection payload as token | `Bearer ' OR '1'='1` | 401 |
| R7-12 | S | Oversized token | `Bearer ` + `A` x8,000 | 401, not 5xx (see Q19) [R9] |
| R7-13 | N | Password used as token | `Bearer Passw0rd!` | 401 |

## R8: Logout revokes the token

The requirements don't say how the token is sent to `/logout` (Q20). These tests send it the way the API defines once that's answered.

| ID | Type | Steps | Test data | Expected result |
|----|------|-------|-----------|-----------------|
| R8-01 | P | 1) login → `T` 2) `profile(T)` 3) `logout(T)` 4) `profile(T)` | default | Step 2: 200. Step 4: 401 [R7] |
| R8-02 | P | 1) R8-01 2) login again → `T2` 3) `profile(T2)` | default | 200, 200. Logout does not block future logins [R4] |
| R8-03 | P | 1) Log in A → `TA`, B → `TB` 2) `logout(TA)` 3) `profile(TB)` | two accounts | 200. Revoking A's token doesn't affect B's |
| R8-04 | E | logout with no token, then with a garbage token | none; `zzzz` | Not 5xx (exact codes are Q20) [R9] |

## R9: No 5xx on client input

Expected result for every row: status is not in the 500 to 599 range, and a valid reg sent afterwards still returns 201 (the service is still working).

| ID | Type | Steps | Test data |
|----|------|-------|-----------|
| R9-01 | N | Malformed JSON to `/register` and `/login` | `{"username":"a",` |
| R9-02 | N | Valid JSON with wrong Content-Type | `text/plain`; `application/x-www-form-urlencoded` |
| R9-03 | N | Wrong field types on `/register` and `/login` | number `123`, `true`, `[]`, `null`, `{}` in each field |
| R9-04 | E | Very large password on `/register` | 10 MB string |
| R9-05 | E | Deeply nested JSON | 10,000 nested arrays |
| R9-06 | E | Unusual Unicode in username | emoji, right-to-left text, zero-width space, `\u0000` |
| R9-07 | S | Prototype-pollution keys | `{"__proto__":{"admin":true},"username":"p1","password":"Passw0rd!"}`, same with `constructor` |
| R9-08 | E | Duplicate JSON keys | `{"username":"a","username":"b","password":"Passw0rd!"}` |
| R9-09 | N | Unsupported methods | `GET /register`, `DELETE /login`, `PUT /profile` |
| R9-10 | N | Path and query oddities | `/register/../profile`, `/login?username[$ne]=x` |
| R9-11 | S | Header abuse on `/profile` | two Authorization headers; non-ASCII bytes in the header |
| R9-12 | S | Injection payloads in username on `/register`, then `reg("tester01","Passw0rd!")` | `'; DROP TABLE users;--`, `{"$where":"sleep(5000)"}` |

## Questions

Ambiguities in the requirements that were listed here instead of guessed.

### Input format and validation

- **Q1.** Are request bodies JSON, and are the fields named exactly `username` and `password`? Which content types are accepted?
- **Q2.** Does an empty string, whitespace-only string, or `null` count as "supplied" for R1?
- **Q3.** What status should wrong field types (number, array, object) return? 400?
- **Q4.** Are there username rules: minimum or maximum length, allowed characters, trimming of spaces?
- **Q5.** How does R2's case-insensitivity work beyond plain ASCII? For example, is `straße` the same as `STRASSE`, and are composed and decomposed `é` the same name?
- **Q6.** For R3, what is a "character": bytes, Unicode code points, or visible characters? Is whitespace trimmed? Is there a maximum length?
- **Q7.** Which error wins when several apply, for example a duplicate username with a short password (400 or 409)?

### Login

- **Q8.** Is login case-insensitive on username (can `TESTER01` log into `tester01`)? If so, do failed attempts with case variants count toward the same R6 counter?
- **Q9.** What does `/login` return for missing fields or wrong types: 400 or 401?
- **Q10.** Where is the token in the response, what format is it, and does it expire?
- **Q11.** Can one account hold several valid tokens at once, or does a new login invalidate the old token?

### R5 and R6

- **Q12.** Does "the same 401 response" mean status only, or also body, headers and response time? Timing is a known leak if password hashing only runs for existing users.
- **Q13.** R5 and R6 conflict: only real accounts can ever return 423, so an attacker can find accounts by failing 5 logins. It also lets anyone lock any known account. Is this accepted?
- **Q14.** How long does a lock last, and how is it lifted?
- **Q15.** Do tokens issued before the lock stay valid?
- **Q16.** Is "consecutive" counted per account or across the service? Do malformed login requests count as failures?

### R7 and R8

- **Q17.** Is the Bearer scheme case-insensitive (`bearer T`)? How are extra spaces or two Authorization headers treated?
- **Q18.** What does the profile body contain? Without this, a test can't check that a token returns the right user's data.
- **Q19.** If a proxy rejects an oversized header with 431, does that satisfy R7's 401?
- **Q20.** How is the token sent to `/logout`, what does a successful logout return, and what is returned for a missing, invalid or already-revoked token?
- **Q21.** Does logout revoke only the presented token, or every session for that account?

### Beyond the requirements

- **Q22.** Should tests also check that error responses never contain stack traces or database errors, and should there be IP rate limiting? Both are recommended by the secure-ai-rules repo but aren't in R1 to R9.

## Notes on the security reference

- The repo's SQL and NoSQL injection sections led to R4-05 to R4-08, R7-11 and R9-12.
- Its sample token middleware returns 403 for an invalid token. R7 requires 401, so R7-08 to R7-10 will catch an implementation that copied that pattern.
- Its login limiter example is per IP and returns 429. R6 is per account and requires 423, so R6-01 and R6-07 will fail against an IP-only limiter.
- Its MongoDB login example queries username and password together, which suggests plaintext storage. Hashing can't be verified through this API, so no test was written for it.