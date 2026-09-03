---
model: sonnet
allowed-tools: bash, read
description: Audit release readiness — version consistency, changelog, CI, open issues, breaking changes
---

# Release Audit

Audit release `{{tag}}` of `{{repository}}` for readiness before generating notes. Follow the `Workflow` and produce a structured blockers JSON for the `Report` phase.

## Variables

TAG: {{tag}}
REPOSITORY: {{repository}}
PREVIOUS_TAG: {{previous_tag}}

## Workflow

1. **Version consistency** — check `package.json`, `pyproject.toml`, `Cargo.toml`, or equivalent. Verify the version number matches `{{tag}}` (e.g., tag `v1.2.0` → version `1.2.0`).

2. **Changelog** — check for `CHANGELOG.md`, `HISTORY.md`, or `CHANGES.md`. Verify there's an entry for this version.

3. **CI status on the tagged commit:**
   ```bash
   gh api repos/{{repository}}/commits/{{tag}}/check-runs --jq '.check_runs[] | "\(.name): \(.conclusion)"'
   ```

4. **Open critical issues:**
   ```bash
   gh issue list --repo {{repository}} --label "priority:critical" --state open --json number,title
   ```

5. **Known vulnerabilities:**
   ```bash
   gh api repos/{{repository}}/dependabot/alerts --paginate --jq '.[].security_advisory.summary' 2>/dev/null || echo "No Dependabot data"
   ```

6. **Breaking changes** — scan commits between previous tag and `{{tag}}`:
   ```bash
   PREV="{{previous_tag}}"
   if [ -z "$PREV" ]; then
     PREV=$(git tag --sort=-creatordate | sed -n '2p')
   fi
   git log --oneline ${PREV}..{{tag}}
   ```
   Look for `BREAKING CHANGE`, `!:` in commit messages, or major version bumps.

## Report

Write an audit JSON to `artifacts/output/release-audit.md`:

```json
{
  "tag": "{{tag}}",
  "version_consistent": true,
  "changelog_updated": true,
  "ci_passing": true,
  "critical_issues_open": 0,
  "vulnerability_alerts": 0,
  "breaking_changes": [],
  "blockers": [],
  "warnings": [],
  "commits_since_last_release": 42,
  "previous_tag": "v1.1.0"
}
```
