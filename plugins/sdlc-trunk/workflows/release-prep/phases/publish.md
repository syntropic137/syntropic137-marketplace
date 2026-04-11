---
model: haiku
allowed-tools: bash, git
description: Update the GitHub release with generated notes, or block if audit found blockers
---

# Finalize Release

Update GitHub release `{{tag}}` on `{{repository}}` with the generated notes from the previous phase. If the audit phase found blockers, do NOT publish — flag them instead.

## Variables

TAG: {{tag}}
REPOSITORY: {{repository}}
RELEASE_AUDIT: {{audit}}
RELEASE_NOTES: {{notes}}

## Workflow

1. **Review the audit and release notes from previous phases** — see `RELEASE_AUDIT` and `RELEASE_NOTES` in Variables above. Check `blockers` in the audit JSON. If blockers exist, skip to "If Blockers Found" below.

### If No Blockers

2. **Update the release with generated notes:**
   ```bash
   RELEASE_NOTES_FILE="$(mktemp)"
   cat > "$RELEASE_NOTES_FILE" <<'EOF'
   {{notes}}
   EOF
   gh release edit {{tag}} --repo {{repository}} --notes-file "$RELEASE_NOTES_FILE"
   ```

3. **Verify the release:**
   ```bash
   gh release view {{tag}} --repo {{repository}} --json name,tagName,isDraft,isPrerelease,body
   ```

### If Blockers Found

Do NOT publish. Instead:

2. **Update the release with blocker details:**
   ```bash
   gh release edit {{tag}} --repo {{repository}} --notes "## Release Blocked

   The following issues must be resolved before this release ships:

   [list blockers from audit phase]

   ---
   *Audited automatically by Syntropic137.*"
   ```

3. **Mark as draft:**
   ```bash
   gh release edit {{tag}} --repo {{repository}} --draft
   ```

## Report

Write a release summary to `artifacts/output/release-summary.md`:

```markdown
## Release Summary

**Tag:** {{tag}}
**Repository:** {{repository}}
**Outcome:** published | blocked | draft
**Release URL:** [URL if published]
**Blockers:** [list if blocked, or "none"]
```
