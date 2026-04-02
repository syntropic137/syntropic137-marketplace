---
model: sonnet
allowed-tools: bash, git, read
timeout-seconds: 600
max-tokens: 16384
---

You are performing a deep code review of PR #{{pr_number}} on {{repository}}.

The previous phase gathered context about the PR, project stack, and coding standards. Use that context to guide your review.

## Review Checklist

For each changed file, evaluate against these categories:

### 1. Correctness
- Does the logic produce the intended result?
- Are edge cases handled (empty inputs, nulls, boundary values)?
- Do error paths behave correctly?
- Are there off-by-one errors, missing awaits, or unclosed resources?

### 2. Security
- Input validation at system boundaries (user input, API params, file paths)
- No secrets, tokens, or credentials in code
- SQL/command injection prevention
- Proper authentication and authorization checks
- Safe file operations (no path traversal)

### 3. Type Safety
- All function signatures fully typed (no implicit `any`, no untyped parameters)
- Null/undefined handled explicitly (no `!` assertions without justification)
- Return types match actual returns
- Generic types used where appropriate (not `object` or `dict`)

### 4. Testing
- New behavior has corresponding tests
- Tests cover both happy path and error cases
- Tests are deterministic (no timing dependencies, no network calls)
- Existing tests updated if behavior changed

### 5. Architecture
- Changes respect existing module boundaries
- No circular dependencies introduced
- New code follows established patterns in the codebase
- Appropriate separation of concerns

### 6. Performance (only for hot paths)
- No N+1 queries or unbounded loops
- Large data sets handled with pagination/streaming
- Caching used appropriately (not prematurely)

## Process

1. Read the full diff: `git diff {{base_branch}}...HEAD`
2. For each changed file, read the full file for context (not just the diff)
3. Cross-reference with project coding standards from the context phase
4. Record findings with exact file paths and line numbers

## Output

Produce a JSON findings document:

```json
{
  "summary": "One paragraph assessment",
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
  "files_reviewed": ["list of files"]
}
```
