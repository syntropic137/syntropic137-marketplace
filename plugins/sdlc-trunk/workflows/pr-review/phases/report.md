---
model: sonnet
allowed-tools: bash, git
description: Post a structured GitHub PR review from the analysis findings
---

# Post Review

Transform the deep analysis findings into a GitHub PR review for PR `{{pr_number}}` on `{{repository}}`. Follow the `Workflow` and post via the `Report` step.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
FINDINGS: {{analyze}}

## Workflow

1. Review the findings from the previous phase — see `FINDINGS` in Variables above.

2. Compose a review using this structure:

   ```
   ## Code Review

   **Risk:** low/medium/high | **Files:** N | **Findings:** N

   ### Summary
   [What does this PR do? Is it ready to merge?]

   ---

   ### Findings

   #### [!] Critical title
   `path/to/file.py:42`

   [What's wrong and why it matters]

   **Fix:** [Specific suggestion with code if helpful]

   ---

   #### [?] Warning title
   `path/to/file.py:88`

   [Explanation] **Fix:** [Suggestion]

   ---

   #### [~] Suggestion title
   `path/to/file.py:120`

   [Explanation]

   ---

   ### Verdict

   [approve / request changes / comment only]
   [Questions for the author]
   [What was done well — acknowledge good work]
   ```

3. Severity indicators: `[!]` critical (must fix), `[?]` warning (should fix), `[~]` suggestion (nice to have).

4. Guidelines: exact file paths and line numbers; explain *why*; don't block over style nits; if clean, a short "LGTM" is appropriate.

## Report

Post the review to GitHub:

```bash
gh pr review {{pr_number}} --repo {{repository}} --body "<review content>" --event COMMENT
# Use --event REQUEST_CHANGES if verdict is request_changes
# Use --event APPROVE if verdict is approve with no findings
```

Write a summary to `artifacts/output/review.md`:

```markdown
## Review Posted

**PR:** #{{pr_number}} on {{repository}}
**Verdict:** approve | request_changes | comment
**Risk level:** low | medium | high
**Findings:** N critical, N warnings, N suggestions

[Link to the posted review if available]
```
