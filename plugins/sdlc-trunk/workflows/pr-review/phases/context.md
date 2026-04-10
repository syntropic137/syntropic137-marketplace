---
model: haiku
allowed-tools: bash, git, read
description: Gather PR metadata, project stack, and coding standards for the deep review
---

# Gather Context

Quickly collect all context needed for the deep analysis phase. This is a fast, lightweight pass — don't read full file contents.

## Variables

PR_NUMBER: {{pr_number}}
REPOSITORY: {{repository}}
BRANCH: {{branch}}
BASE_BRANCH: {{base_branch}}
TITLE: {{title}}
AUTHOR: {{author}}

## Workflow

1. **PR metadata:**
   ```bash
   gh pr view {{pr_number}} --repo {{repository}} --json title,body,labels,milestone,additions,deletions,changedFiles
   ```

2. **Commit history:**
   ```bash
   git log --oneline {{base_branch}}..HEAD
   ```

3. **Diff stats:**
   ```bash
   git diff --stat {{base_branch}}...HEAD
   ```

4. **Project conventions** — check for (read, don't skip):
   - `CLAUDE.md` or `AGENTS.md` at repo root (coding standards)
   - `pyproject.toml` or `package.json` (language/framework)
   - Linter configs (`.eslintrc`, `ruff.toml`, `pyright` settings)
   - Test location and naming conventions

## Report

Write a structured context summary to `artifacts/output/pr-context.md`:

```markdown
## PR Context

**Title:** {{title}}
**Author:** {{author}}
**Branch:** {{branch}} → {{base_branch}}
**Changed files:** N
**Additions/Deletions:** +N / -N

### Commits
[commit list]

### Project Stack
- Language: [detected]
- Framework: [detected]
- Linter: [detected]
- Test framework: [detected]

### Coding Standards
[key rules from CLAUDE.md/AGENTS.md, or "none found"]

### Changed Files
[grouped by directory/module]
```
