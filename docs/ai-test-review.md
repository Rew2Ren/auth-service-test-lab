# AI-Assisted Test Design Review

> **Status:** In progress. Fill in this file yourself with real results before publishing.

## Purpose

To compare AI-generated test cases against my own suite, and record where an AI tool's suggestions helped, where they were wrong, and where human judgement was needed.

## Method

1. Give each tool `SPEC.md` (only the spec, not the code) with the same prompt.
2. Compare its suggested test cases against the existing suite in `tests/`.
3. Decide on each suggestion: **Keep** (add to the suite), **Fix** (useful idea, wrong detail) or **Reject**, and record why.

**Prompt used:**

```
You are a software test engineer. Using only the requirements below, write test cases for this account service. For each test give an ID, the requirement it covers, the steps, the test data and the expected result. Include positive, negative and edge cases. Do not assume any behaviour that isn't in the requirements. If something is ambiguous, list it as a question instead of guessing.
```

## Results

### [Claude]

| # | Suggested test | Decision | Reasoning |
|---|----------------|----------|-----------|
| R1-06 | Register with no request body | Keep | Not in my suite. Passes (400) and closes a gap for empty requests. |
| R2-07 | Failed duplicate must not overwrite the original password | Keep | A data-integrity check I hadn't considered. Login behaviour passes; the registration step hits BUG-001. |
| R2-08 | Simultaneous registration of case variants | Reject | Needs truly concurrent requests, which Flask's test client can't send. Out of scope until I test a live server. |
| R3-08 | Rejected registration must not create an account | Covered | Fails, but only because of BUG-002 (8-character password). Adds no new information. |
| R4-05 | NoSQL operator object as password | Fix | NoSQL injection doesn't apply: there's no MongoDB here. The real idea, wrong field types, is covered by R9-03. |
| R5-04 | Unknown username never triggers lockout | Keep | Passes. Guards against a future lockout fix that leaks which accounts exist. |
| R6-07 | Locking account A doesn't lock account B | Keep | Passes. Confirms the lock is per account, not per client. |
| R7-07 | Wrong auth scheme (`Basic <token>`) | Keep | **Fails: returns 200.** New defect, not one of the seeded bugs. |
| R9-03 | Wrong field types (`null`, number, list) | Keep | **Fails: creates accounts named "None", "123" and so on.** New defect. |
| R9-05 | Deeply nested JSON | Keep | **Fails: returns 500**, breaking R9. New defect. |
| R9-07 | Prototype-pollution keys | Reject | JavaScript-specific. Python dictionaries have no prototype chain. |
| Q13 | Lockout reveals which accounts exist | Question | A genuine design conflict between R5 and R6, and the most valuable insight in the output. |

## Takeaways

- **It rediscovered every seeded defect from the spec alone.** Without seeing any code, the tool proposed tests that catch all five seeded bugs: case-insensitive usernames (R2-02), the 8-character boundary (R3-02), the lockout threshold (R6-01), token revocation on logout (R8-01) and the malformed header crash (R7-04). That shows requirements-based test design works well as an AI task.
- **It found three defects my own suite missed.** Its tests for the wrong auth scheme (R7-07), wrong field types (R9-03) and deeply nested JSON (R9-05) all failed against the service. These weren't seeded bugs. They're now logged as BUG-006 to BUG-008.
- **It predicted results but couldn't verify them.** Every expected result was the tool's reading of the spec. I only knew which tests mattered after running them. Several looked important but added nothing new, such as R3-08, which only failed because of an existing bug.
- **It brought in context I didn't ask for.** Although I asked it to use only the requirements, it drew on a Node.js security rule set. That produced tests that don't apply to a Python service, such as NoSQL injection and prototype pollution, which I had to filter out.
- **Its best contribution was a question, not a test.** Q13 points out that R5 and R6 conflict: because only real accounts can lock, the lockout itself reveals which usernames exist. That's a design flaw in the requirements, which no amount of testing the code would catch.

**How I'd use agents in a real test workflow:** let the agent generate a broad set of candidate tests and questions from the requirements, then apply human judgement to filter out what's irrelevant, run everything, and triage the failures. The agent widens coverage quickly. The tester decides what's real.
