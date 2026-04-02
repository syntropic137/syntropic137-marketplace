---
model: haiku
allowed-tools: bash, git
---

You are verifying a CI fix for PR #{{pr_number}} in {{repository}}.

## Objective

Confirm the fix was applied and pushed correctly. This is a lightweight verification pass.

## Steps

1. **Check the commit was pushed:**
   ```bash
   git log --oneline -3
   ```

2. **Verify the fix is on the right branch:**
   ```bash
   git branch --show-current
   ```
   Should be `{{branch}}`.

3. **Check CI status** (may still be running):
   ```bash
   gh pr checks {{pr_number}} --json name,state,conclusion
   ```

4. **Post a status comment:**
   ```bash
   gh pr comment {{pr_number}} --body "**CI Self-Healing:** Applied fix in commit $(git rev-parse --short HEAD).

   **What was fixed:** [brief description from diagnosis]
   **Status:** Waiting for CI to re-run"
   ```

## Output

Report whether the fix was successfully applied and pushed. If CI has already completed, report pass/fail.
