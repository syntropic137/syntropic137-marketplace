---
model: sonnet
allowed-tools: bash, git
timeout-seconds: 300
max-tokens: 8192
---

You are writing a code review report for PR #{{pr_number}} on {{repository}}.

## Objective

Transform the analysis findings into actionable GitHub PR review comments. The goal is a helpful, constructive review that the author can act on immediately.

## Input

The previous phase produced a structured analysis with findings categorized by severity and type. Use that analysis to write the review.

## Output Format

Write a GitHub-compatible review comment in Markdown. Structure it as:

### Review Header

```markdown
## Code Review: {{title}}

**Risk Level:** [low/medium/high] | **Files Reviewed:** [count] | **Findings:** [count]

### Summary
[One paragraph: what does this PR do, and what's the overall verdict?]
```

### Findings (grouped by severity)

For each finding, format as:

```markdown
#### [severity emoji] [title]
**File:** `path/to/file.py:42`
**Category:** [bug/security/type-safety/etc.]

[Explanation of the issue]

**Suggestion:**
[How to fix, with code snippet if helpful]
```

Use these severity indicators:
- Critical: `[!]` prefix
- Warning: `[?]` prefix
- Suggestion: `[~]` prefix

### Closing

End with:
- Whether the PR is ready to merge as-is, needs changes, or needs discussion
- Any questions for the author about intent or trade-offs
- Acknowledgment of what was done well (if applicable)

## Guidelines

- Be specific — reference exact file paths and line numbers
- Be constructive — explain *why* something is an issue, not just *that* it is
- Be proportional — don't block a PR over style preferences
- Respect the author's intent — suggest improvements, don't rewrite their approach
- If the PR is clean, say so — a short "LGTM" review is fine for good code

Post the review using `gh pr review {{pr_number}} --body "<review>"` or output the Markdown for manual posting.
