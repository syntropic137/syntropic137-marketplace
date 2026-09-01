---
model: haiku
allowed-tools: bash
description: Verify the fix was committed and pushed, then post a status comment
---

# Verify Fix

Confirm the CI fix was correctly applied and pushed for PR `{{pr_number}}` in `{{repository}}`. This is a lightweight verification pass.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
BRANCH: {{branch}}
FIX_SUMMARY: {{fix}}

## Workflow

1. **Review the fix summary from the previous phase** — see `FIX_SUMMARY` in Variables above.

2. **Confirm the commit landed:**
   ```bash
   git log --oneline -3
   ```

3. **Confirm the correct branch:**
   ```bash
   git branch --show-current
   ```
   Should be `{{branch}}`.

4. **Check CI status** (may still be queued):
   ```bash
   gh pr checks {{pr_number}} --repo {{repository}} --json name,state,conclusion
   ```

5. **Post a status comment:**
   ```bash
   gh pr comment {{pr_number}} --repo {{repository}} --body "**CI Self-Healing:** Applied fix in $(git rev-parse --short HEAD).

   **What was fixed:** ${FIX_SUMMARY}
   **CI status:** [passing / still running / still failing]"
   ```

## Report

Write a verification report to `artifacts/output/verification.md`:

```markdown
## Verification

**PR:** #{{pr_number}} on {{repository}}
**Branch:** {{branch}}
**Commit SHA:** [SHA]
**Fix confirmed:** yes | no
**CI status:** passing | running | failing
**Comment posted:** yes | no
```
