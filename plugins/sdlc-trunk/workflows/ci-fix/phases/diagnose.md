---
model: sonnet
allowed-tools: bash, read
description: Diagnose the root cause of a CI failure — do not fix, only diagnose
---

# Diagnose Failure

Identify the root cause of the CI failure on PR `{{pr_number}}` in `{{repository}}`. Follow the `Workflow` to produce a diagnosis JSON for the fix phase. Do NOT attempt fixes here.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
BRANCH: {{branch}}
CHECK_RUN_NAME: {{check_run_name}}
CHECK_RUN_ID: {{check_run_id}}

## Workflow

1. **Fetch CI logs:**
   ```bash
   gh pr checks {{pr_number}} --repo {{repository}} --json name,state,conclusion,detailsUrl
   ```
   If `CHECK_RUN_ID` is set, get detailed output:
   ```bash
   gh api repos/{{repository}}/check-runs/{{check_run_id}} --jq '.output.text // .output.summary // "No output"'
   ```

2. **Classify the failure type:**
   - `lint` — code style violations (easiest to auto-fix)
   - `typecheck` — pyright, tsc, mypy errors
   - `test` — failing assertions
   - `build` — compilation or dependency errors
   - `other` — permissions, infra, flaky tests

3. **Read the failing code** — look at files and lines from the error output; read full file context.

4. **Check if introduced by this PR:**
   ```bash
   git diff main...HEAD -- <failing-file>
   ```
   Determine if the failure pre-existed or was introduced by this PR's changes.

## Report

Write a diagnosis JSON to `artifacts/output/diagnosis.md`:

```json
{
  "failure_type": "lint|typecheck|test|build|other",
  "root_cause": "Clear explanation of why CI failed",
  "introduced_by_pr": true,
  "affected_files": ["path/to/file.py"],
  "error_messages": ["exact error text"],
  "fix_strategy": "What needs to change to fix this",
  "confidence": "high|medium|low",
  "should_auto_fix": true
}
```

Set `should_auto_fix: false` if: the failure is pre-existing, the fix requires architectural changes, it's a flaky test, or confidence is low.
