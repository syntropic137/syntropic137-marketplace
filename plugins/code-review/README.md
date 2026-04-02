# Code Review Plugin

AI-powered code review for pull requests. Analyzes changes for bugs, security issues, type safety gaps, and architecture violations, then produces a structured review report.

## Workflows

### `code-review`

**Type:** review | **Classification:** simple | **Phases:** 2

| Phase | Purpose |
|-------|---------|
| **Analyze** | Diff all changes, read full file context, identify issues by severity |
| **Report** | Transform findings into actionable GitHub PR review comments |

## Triggers

| Trigger | Event | Conditions |
|---------|-------|------------|
| `on-pr-opened` | `pull_request` | action is `opened` or `synchronize` |

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `pr_number` | Yes | Pull request number |
| `repository` | Yes | Repository in `owner/repo` format |
| `branch` | Yes | Head branch of the PR |
| `title` | No | PR title for context |

## Usage

```bash
# Install from marketplace
syn workflow install code-review

# Run manually
syn workflow run code-review \
  --input pr_number=42 \
  --input repository=myorg/myrepo \
  --input branch=feat/my-feature

# Or attach the trigger to auto-run on PRs
syn triggers create \
  --workflow code-review \
  --from-package code-review
```
