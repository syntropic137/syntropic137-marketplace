---
model: sonnet
allowed-tools: bash, git
timeout-seconds: 300
max-tokens: 8192
---

You are posting a code review for PR #{{pr_number}} on {{repository}}.

## Objective

Transform the analysis findings into a GitHub PR review. The review should be constructive, specific, and actionable.

## Format

Compose a review using this structure:

```markdown
## Code Review

**Risk:** [low/medium/high] | **Files:** [count] | **Findings:** [count]

### Summary
[What does this PR do? Is it ready to merge?]

---

### Findings

#### [!] [Critical finding title]
`path/to/file.py:42`

[Explanation — what's wrong and why it matters]

**Fix:** [Specific suggestion with code if helpful]

---

#### [?] [Warning title]
`path/to/file.py:88`

[Explanation]

**Fix:** [Suggestion]

---

#### [~] [Suggestion title]
`path/to/file.py:120`

[Explanation]

---

### Verdict

[approve / request changes / comment only]
[Any questions for the author]
[What was done well — acknowledge good work]
```

## Severity Indicators

- `[!]` Critical — must fix before merge
- `[?]` Warning — should fix, not a blocker
- `[~]` Suggestion — nice to have

## Guidelines

- Be specific: exact file paths and line numbers
- Be constructive: explain *why*, not just *what*
- Be proportional: don't block over style nits
- Be concise: developers read reviews quickly
- If clean: a short "LGTM" is fine — don't invent issues

## Post the Review

```bash
gh pr review {{pr_number}} --body "<review content>" --event COMMENT
```

If verdict is `request_changes`, use `--event REQUEST_CHANGES`.
If verdict is `approve` with no findings, use `--event APPROVE`.
