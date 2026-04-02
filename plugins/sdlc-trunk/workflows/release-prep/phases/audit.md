---
model: sonnet
allowed-tools: bash, git, read
---

You are auditing release {{tag}} of {{repository}} for readiness.

## Objective

Verify the release is complete, consistent, and safe to ship. Identify any blockers before generating release notes.

## Checks

### 1. Version Consistency
- Check `package.json`, `pyproject.toml`, `Cargo.toml`, or equivalent for version numbers
- Verify the version matches the tag (e.g., `v1.2.0` tag should have `1.2.0` in version files)
- Flag mismatches

### 2. Changelog / History
- Check for `CHANGELOG.md`, `HISTORY.md`, or `CHANGES.md`
- Verify there's an entry for this version
- Flag if the changelog is missing or hasn't been updated

### 3. CI Status
```bash
# Check if all CI checks passed on the tagged commit
gh api repos/{{repository}}/commits/{{tag}}/check-runs --jq '.check_runs[] | "\(.name): \(.conclusion)"'
```
Flag any failing or incomplete checks.

### 4. Open Issues / PRs
```bash
# Check for any P0/critical issues still open
gh issue list --repo {{repository}} --label "priority:critical" --state open --json number,title
```

### 5. Dependencies
- Check for known vulnerabilities:
  ```bash
  gh api repos/{{repository}}/vulnerability-alerts --jq '.[] | .security_advisory.summary' 2>/dev/null || echo "No Dependabot data"
  ```

### 6. Breaking Changes
- Find the previous tag:
  ```bash
  git tag --sort=-creatordate | head -5
  ```
- Scan commit messages between tags for `BREAKING CHANGE`, `!:`, or major version bumps
- List any breaking changes found

## Output

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
