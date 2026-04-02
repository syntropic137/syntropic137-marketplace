---
model: sonnet
allowed-tools: bash, git, read
---

You are diagnosing a CI failure on PR #{{pr_number}} in {{repository}}.

## Objective

Identify the root cause of the CI failure so it can be fixed automatically. Do NOT attempt to fix anything yet — only diagnose.

## Steps

1. **Fetch CI logs** — Get the failure output:
   ```bash
   gh pr checks {{pr_number}} --json name,state,conclusion,detailsUrl
   ```
   If `check_run_id` is available, get detailed logs:
   ```bash
   gh api repos/{{repository}}/check-runs/{{check_run_id}} --jq '.output.text // .output.summary // "No output"'
   ```

2. **Identify the failure type**:
   - **Lint/format failure** — code style violations (easiest to fix)
   - **Type check failure** — pyright, tsc, mypy errors
   - **Test failure** — unit/integration test assertions
   - **Build failure** — compilation, dependency resolution
   - **Other** — permissions, infrastructure, flaky tests

3. **Read the failing code** — Look at the files and lines mentioned in the error output. Read full file context.

4. **Check recent changes** — Compare against the base branch:
   ```bash
   git diff {{base_branch}}...HEAD -- <failing-file>
   ```
   Determine if the failure was introduced by this PR or is pre-existing.

## Output

Produce a diagnosis report:

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

Set `should_auto_fix: false` if:
- The failure is pre-existing (not introduced by this PR)
- The fix requires architectural changes
- The failure is a flaky test (intermittent)
- You're not confident in the diagnosis
