---
model: sonnet
allowed-tools: bash
description: Transform analysis findings into a posted GitHub PR review
---

# Write Review

Transform the findings from the previous phase into a constructive GitHub PR review for PR `{{pr_number}}` on `{{repository}}`. Follow the `Workflow` and post via the `Report` step.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
TITLE: {{title}}
FINDINGS: {{analyze}}

## Workflow

1. Review the findings from the previous phase — see `FINDINGS` in Variables above.

2. Compose a review using this structure:

   ```
   ## Code Review: {{title}}

   **Risk Level:** low/medium/high | **Files Reviewed:** N | **Findings:** N

   ### Summary
   [What does this PR do, and what's the overall verdict?]

   ---

   #### [!] Critical title
   `path/to/file.py:42` | **Category:** bug/security/etc.

   [Explanation — what's wrong and why it matters]

   **Fix:** [Specific suggestion with code snippet if helpful]

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
   [Questions for the author about intent or trade-offs]
   [Acknowledge what was done well — a short "LGTM" is fine for clean code]
   ```

3. Guidelines: reference exact file paths and line numbers; explain *why*, not just *what*; don't block over style nits; if the PR is clean, say so clearly.

## Report

Post the review to GitHub:

```bash
gh pr review {{pr_number}} --repo {{repository}} --body "<review content>" --event COMMENT
# Use --event REQUEST_CHANGES if verdict is request_changes
# Use --event APPROVE if clean and approving
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
