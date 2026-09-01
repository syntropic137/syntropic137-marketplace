---
model: sonnet
allowed-tools: bash, read
description: Deep code review across correctness, security, type safety, testing, and architecture
---

# Deep Analysis

Perform a deep code review of PR `{{pr_number}}` on `{{repository}}`. The previous phase gathered project context and coding standards — use that output to guide this review.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
BASE_BRANCH: {{base_branch}}
PR_CONTEXT: {{context}}

## Workflow

1. **Review the PR context from the previous phase** — see `PR_CONTEXT` in Variables above.

2. **Read the full diff:**
   ```bash
   git diff {{base_branch}}...HEAD
   ```

3. **For each changed file**, read the complete file for context (not just the diff lines).

4. **Evaluate against these categories:**

   - **Correctness:** Logic errors, edge cases (nulls, empty inputs, boundary values), off-by-one errors, missing awaits, unclosed resources.
   - **Security:** Input validation at system boundaries, no secrets in code, injection prevention, proper auth checks, safe file ops (no path traversal).
   - **Type Safety:** No implicit `any`, no untyped params, null/undefined handled explicitly (no `!` assertions without justification), return types match.
   - **Testing:** New behavior has tests covering happy path and error cases; tests are deterministic; existing tests updated if behavior changed.
   - **Architecture:** Module boundaries respected, no circular deps, new code follows established patterns, appropriate separation of concerns.
   - **Performance** (hot paths only): No N+1 queries, large data sets paginated/streamed, caching appropriate.

5. Cross-reference findings against the project coding standards from the context phase.

## Report

Write a JSON findings document to `artifacts/output/findings.md`:

```json
{
  "summary": "One-paragraph assessment",
  "risk_level": "low|medium|high",
  "verdict": "approve|request_changes|comment",
  "findings": [
    {
      "severity": "critical|warning|suggestion",
      "category": "correctness|security|type-safety|testing|architecture|performance",
      "file": "path/to/file",
      "line": 42,
      "title": "Short description",
      "detail": "Why this matters",
      "suggestion": "How to fix"
    }
  ],
  "testing_assessment": "Are new changes adequately tested?",
  "files_reviewed": ["list", "of", "files"]
}
```
