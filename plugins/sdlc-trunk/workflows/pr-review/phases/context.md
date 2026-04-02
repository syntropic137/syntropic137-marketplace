---
model: haiku
allowed-tools: bash, git, read
timeout-seconds: 300
max-tokens: 8192
---

You are preparing context for a code review of PR #{{pr_number}} on {{repository}}.

## Objective

Quickly gather all relevant context so the deep analysis phase can focus on finding issues rather than reading files. This is a fast, lightweight pass.

## Steps

1. **PR metadata** — Run:
   ```bash
   gh pr view {{pr_number}} --json title,body,labels,milestone,additions,deletions,changedFiles
   ```

2. **Commit history** — Understand the progression of changes:
   ```bash
   git log --oneline {{base_branch}}..HEAD
   ```

3. **Changed files summary** — Get the list and diff stats:
   ```bash
   git diff --stat {{base_branch}}...HEAD
   ```

4. **Project conventions** — Check for:
   - `CLAUDE.md` or `AGENTS.md` at the repo root (coding standards)
   - `pyproject.toml` or `package.json` (language/framework)
   - Linter configs (`.eslintrc`, `ruff.toml`, `pyright` settings)
   - Test patterns (where tests live, naming conventions)

## Output

Produce a structured context summary:

```
## PR Context

**Title:** {{title}}
**Author:** {{author}}
**Branch:** {{branch}} → {{base_branch}}
**Changed files:** [count]
**Additions/Deletions:** +[n] / -[n]

### Commits
[commit list]

### Project Stack
- Language: [detected]
- Framework: [detected]
- Linter: [detected]
- Test framework: [detected]

### Coding Standards
[key rules from CLAUDE.md/AGENTS.md if present]

### Changed Files
[grouped by directory/module]
```

Keep this fast — don't read full file contents, just gather metadata.
