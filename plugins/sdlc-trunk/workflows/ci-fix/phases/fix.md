---
model: sonnet
allowed-tools: bash, git, read, edit
---

You are fixing a CI failure on PR #{{pr_number}} in {{repository}}.

The previous phase diagnosed the root cause. Apply the fix based on that diagnosis.

## Rules

1. **Minimal changes only** — Fix exactly what's broken. Do not refactor, clean up, or "improve" surrounding code.
2. **Stay on the PR branch** — All fixes go on `{{branch}}`. Never push to main.
3. **One commit** — All fixes in a single, descriptive commit.
4. **Don't break other things** — Run the relevant check locally before committing if possible.
5. **Skip if low confidence** — If the diagnosis said `should_auto_fix: false`, output a comment explaining the issue instead of attempting a fix.

## Fix Strategies by Type

### Lint/Format
```bash
# Run the project's formatter
# Python: ruff format, black
# JS/TS: prettier, eslint --fix
# Then commit the result
```

### Type Check
- Add missing type annotations
- Fix type mismatches
- Add necessary imports
- Never use `# type: ignore` or `any` as a fix

### Test Failure
- Fix the code to match the test expectation (not the other way around, unless the test is clearly wrong)
- If a test assertion is wrong due to intentional behavior change, update the test with a clear comment

### Build
- Fix import paths, missing dependencies
- Resolve version conflicts

## Process

1. Apply the fix using the Edit tool for targeted changes
2. Verify the fix looks correct by reading the modified files
3. Stage and commit:
   ```bash
   git add <specific-files>
   git commit -m "fix: <what was fixed> (#{{pr_number}})"
   ```
4. Push:
   ```bash
   git push origin {{branch}}
   ```

## If Fix Is Not Possible

If you cannot confidently fix the issue, post a comment instead:
```bash
gh pr comment {{pr_number}} --body "**CI Self-Healing:** Diagnosed the failure but cannot auto-fix.

**Root cause:** [explanation]
**Suggested fix:** [what the author should do]"
```
