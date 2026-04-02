---
model: sonnet
allowed-tools: bash, git
---

You are generating release notes for {{tag}} of {{repository}}.

## Objective

Create comprehensive, well-organized release notes from the commit history since the last release.

## Process

1. **Get the commit range:**
   ```bash
   # Use previous_tag from audit or detect it
   PREV_TAG=$(git tag --sort=-creatordate | sed -n '2p')
   git log --oneline ${PREV_TAG}..{{tag}}
   ```

2. **Categorize commits** using conventional commit prefixes:

   | Prefix | Category | Emoji |
   |--------|----------|-------|
   | `feat` | New Features | |
   | `fix` | Bug Fixes | |
   | `perf` | Performance | |
   | `docs` | Documentation | |
   | `refactor` | Refactoring | |
   | `test` | Testing | |
   | `chore` | Maintenance | |
   | `BREAKING` | Breaking Changes | |

3. **Generate the notes** in this format:

```markdown
## What's New

### Breaking Changes
- [list any breaking changes with migration instructions]

### New Features
- **scope:** description (#PR)

### Bug Fixes
- **scope:** description (#PR)

### Performance
- description (#PR)

### Other Changes
- description (#PR)

## Contributors
@author1, @author2

## Full Changelog
https://github.com/{{repository}}/compare/${PREV_TAG}...{{tag}}
```

## Guidelines

- Lead with the most impactful changes
- Include PR numbers as links where available
- For breaking changes, include migration instructions
- Mention contributors by GitHub username
- Keep descriptions concise — one line per item
- Group related changes under the same bullet
