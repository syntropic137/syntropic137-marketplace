---
model: sonnet
allowed-tools: bash, git
description: Generate categorized release notes from commit history since the last tag
---

# Generate Release Notes

Generate comprehensive release notes for `{{tag}}` of `{{repository}}` from the commit history since the previous release.

## Variables

TAG: {{tag}}
REPOSITORY: {{repository}}
RELEASE_AUDIT: {{audit}}

## Workflow

1. **Review the release audit from the previous phase** — see `RELEASE_AUDIT` in Variables above. Use `previous_tag` from the audit JSON.

2. **Get the commit range** — use `previous_tag` from the audit, or detect:
   ```bash
   PREV_TAG=$(printf '%s' "$RELEASE_AUDIT" | tr -d '\n' | sed -n 's/.*"previous_tag"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
   if [ -z "$PREV_TAG" ] || [ "$PREV_TAG" = "null" ]; then
     PREV_TAG=$(git tag --sort=-creatordate | sed -n '2p')
   fi
   git log --oneline "${PREV_TAG}..{{tag}}"
   ```

3. **Categorize commits** by conventional commit prefix:

   | Prefix | Category |
   |--------|----------|
   | `feat` | New Features |
   | `fix` | Bug Fixes |
   | `perf` | Performance |
   | `docs` | Documentation |
   | `refactor` | Refactoring |
   | `test` | Testing |
   | `chore` | Maintenance |
   | `BREAKING` | Breaking Changes |

4. **Draft the notes** (see Report format below). Include PR numbers as links where available. For breaking changes, add migration instructions.

## Report

Write release notes to `artifacts/output/release-notes.md`:

```markdown
## What's New

### Breaking Changes
- [description with migration instructions]

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

Guidelines: lead with most impactful changes; one line per item; group related changes; keep descriptions concise.
