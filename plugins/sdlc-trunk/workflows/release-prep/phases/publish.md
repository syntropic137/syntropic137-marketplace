---
model: haiku
allowed-tools: bash, git
timeout-seconds: 120
max-tokens: 4096
---

You are finalizing release {{tag}} of {{repository}}.

## Objective

Update the GitHub release with the generated notes. If there are blockers from the audit, flag them instead of publishing.

## Steps

### If No Blockers

1. **Update the release with generated notes:**
   ```bash
   gh release edit {{tag}} --repo {{repository}} --notes "<release notes from previous phase>"
   ```

2. **Verify the release:**
   ```bash
   gh release view {{tag}} --repo {{repository}} --json name,tagName,isDraft,isPrerelease,body
   ```

3. **Post a summary comment** on the most recent merged PR (if detectable):
   ```bash
   echo "Release {{tag}} published with updated release notes."
   ```

### If Blockers Found

Do NOT publish. Instead:

1. **Comment on the release** with the blockers:
   ```bash
   gh release edit {{tag}} --repo {{repository}} --notes "$(cat <<NOTES
   ## Release Blocked

   The following issues must be resolved before this release ships:

   [list blockers from audit phase]

   ---
   *This release was audited automatically by Syntropic.*
   NOTES
   )"
   ```

2. **Mark as draft** if not already:
   ```bash
   gh release edit {{tag}} --repo {{repository}} --draft
   ```

## Output

Report the final release status: published, blocked, or draft.
