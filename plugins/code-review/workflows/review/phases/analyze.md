---
model: sonnet
allowed-tools: bash, read
description: Analyze all PR changes and produce a structured findings JSON
---

# Analyze Changes

Analyze every change in PR `{{pr_number}}` on `{{repository}}`. Follow the `Workflow` to produce a structured findings JSON for the `Report` phase.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
BASE_BRANCH: {{base_branch}}
TITLE: {{title}}

## Workflow

1. **Understand scope** — Run `git log --oneline {{base_branch}}..HEAD`. Read commit messages to understand intent.

2. **Review the diff** — Run `git diff {{base_branch}}...HEAD`. For large diffs, work file-by-file.

3. **Read full context** — For each modified file, read the surrounding code (not just the diff lines) to understand how changes fit the existing architecture.

4. **Evaluate against these categories:**

   - **Critical (must fix before merge):** Logic errors, security vulnerabilities (injection, auth bypass, secrets in code), data loss risks, breaking API changes without migration.
   - **Warnings (should fix):** Missing error handling for likely failures, type safety gaps, race conditions, missing tests for new behavior.
   - **Suggestions (nice to have):** Naming clarity, duplication, performance on hot paths, documentation gaps.

## Report

Write findings to `artifacts/output/findings.md`:

```json
{
  "summary": "One-paragraph assessment of the PR",
  "risk_level": "low|medium|high",
  "findings": [
    {
      "severity": "critical|warning|suggestion",
      "category": "bug|security|type-safety|architecture|testing|performance|style",
      "file": "path/to/file.py",
      "line": 42,
      "title": "Short description",
      "detail": "Why this matters",
      "suggestion": "How to fix"
    }
  ],
  "files_reviewed": ["list", "of", "files"],
  "test_coverage": "Assessment of test coverage for new code"
}
```
