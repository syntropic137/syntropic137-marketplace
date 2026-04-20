---
model: sonnet
allowed-tools: bash, git, read, edit
description: Apply the diagnosed CI fix, commit, and push in one phase
---

# Apply Fix

Apply the fix for the CI failure on PR `{{pr_number}}` in `{{repository}}` based on the diagnosis from the previous phase. Follow the `Workflow` — edit, commit, and push all happen here (ephemeral constraint: no state carries to the next phase).

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
BRANCH: {{branch}}
DIAGNOSIS: {{diagnose}}

## Workflow

1. **Review the diagnosis from the previous phase** — see `DIAGNOSIS` in Variables above. If `should_auto_fix` is `false`, skip to the "Cannot Fix" step below.

2. **Clone the repo and apply fix by type:**

   - **lint/format:** Run the project formatter (e.g., `ruff format`, `black`, `prettier --write`, `eslint --fix`), then stage all changed files.
   - **typecheck:** Add missing annotations, fix type mismatches, add imports. Never use `# type: ignore` or `any` as a fix.
   - **test:** Fix the code to satisfy the test (not the other way, unless the test is clearly wrong due to an intentional behavior change).
   - **build:** Fix import paths, missing dependencies, version conflicts.

3. **Rules:**
   - Minimal changes only — fix exactly what's broken, don't refactor surrounding code
   - Stay on `{{branch}}` — never push to main
   - One commit covering all changes

4. **Commit and push:**
   ```bash
   git add <specific-files>
   git commit -m "fix: <what was fixed> (#{{pr_number}})"
   git push origin {{branch}}
   ```

5. **Cannot Fix** — if `should_auto_fix` is false, post a comment instead:
   ```bash
   gh pr comment {{pr_number}} --repo {{repository}} --body "**CI Self-Healing:** Diagnosed but cannot auto-fix.

   **Root cause:** [explanation from diagnosis]
   **Suggested fix:** [what the author should do]"
   ```

## Report

Write a fix summary to `artifacts/output/fix-summary.md`:

```markdown
## Fix Applied

**PR:** #{{pr_number}} on {{repository}}
**Branch:** {{branch}}
**Failure type:** lint | typecheck | test | build | other
**Root cause:** [from diagnosis]
**Fix:** [what was changed]
**Commit:** [SHA]
**Push status:** success | failed | skipped (could not auto-fix)
```

If unable to fix, document why and what the author needs to do manually.
