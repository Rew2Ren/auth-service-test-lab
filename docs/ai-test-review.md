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
[Paste the exact prompt you gave the tools]
```

## Results

### [Tool name, e.g. Claude Code]

| # | Suggested test | Decision | Reasoning |
|---|----------------|----------|-----------|
| 1 | | | |
| 2 | | | |

### [Tool name, e.g. Codex]

| # | Suggested test | Decision | Reasoning |
|---|----------------|----------|-----------|
| 1 | | | |

## Takeaways

- [What did the tools catch that I missed?]
- [What did they get wrong, e.g. made-up status codes or requirements not in the spec?]
- [How would I use agents in a real test workflow, based on this?]
