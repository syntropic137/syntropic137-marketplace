# SDLC Trunk-Based Development

Full trunk-based development lifecycle powered by AI agents. Three workflows that cover the PR-to-release pipeline, each with embedded triggers for automatic execution.

## Architecture

```
PR Opened/Updated          CI Failure              Release Created
       |                       |                        |
       v                       v                        v
  +-----------+          +-----------+           +-------------+
  | PR Review |          |  CI Fix   |           | Release Prep|
  +-----------+          +-----------+           +-------------+
  | context   |          | diagnose  |           | audit       |
  | analyze   |          | fix       |           | notes       |
  | report    |          | verify    |           | publish     |
  +-----------+          +-----------+           +-------------+
       |                       |                        |
       v                       v                        v
  Review posted          Fix pushed             Notes published
  on GitHub PR           to branch              on GitHub release
```

## Workflows

### PR Review (`sdlc-pr-review`)

**Trigger:** `pull_request` — opened, synchronize
**Phases:** 3 (context → analyze → report)

Comprehensive pull request review:
1. **Context** (haiku) — fast metadata gathering, project conventions, diff stats
2. **Analysis** (sonnet) — deep review against 6 categories: correctness, security, type safety, testing, architecture, performance
3. **Report** (sonnet) — posts structured review on GitHub with severity indicators

### CI Self-Healing (`sdlc-ci-fix`)

**Trigger:** `check_run` — completed with failure (webhook-only)
**Phases:** 3 (diagnose → fix → verify)

Automatic CI failure resolution:
1. **Diagnose** (sonnet) — fetch CI logs, classify failure type, determine root cause
2. **Fix** (sonnet) — apply minimal targeted fix, commit and push
3. **Verify** (haiku) — confirm push succeeded, post status comment

Safety guards:
- Max 2 fix attempts per PR
- 10-minute cooldown between attempts
- $5 budget cap per trigger
- 30s debounce to batch rapid check events
- Skips pre-existing failures and low-confidence diagnoses

### Release Preparation (`sdlc-release-prep`)

**Trigger:** `release` — created, published
**Phases:** 3 (audit → notes → publish)

Release readiness verification and notes generation:
1. **Audit** (sonnet) — version consistency, changelog, CI status, open critical issues, vulnerabilities, breaking changes
2. **Notes** (sonnet) — generate categorized release notes from conventional commits
3. **Publish** (haiku) — update GitHub release or block if audit found issues

## Installation

```bash
# Register the marketplace
syn marketplace add syntropic137/syntropic137-marketplace

# Install the plugin
syn workflow install sdlc-trunk

# List installed workflows
syn workflow installed
```

## Usage

```bash
# Run PR review manually
syn workflow run sdlc-pr-review \
  --input pr_number=42 \
  --input repository=myorg/myrepo \
  --input branch=feat/my-feature

# Run CI fix manually
syn workflow run sdlc-ci-fix \
  --input pr_number=42 \
  --input repository=myorg/myrepo \
  --input branch=feat/my-feature

# Run release prep manually
syn workflow run sdlc-release-prep \
  --input repository=myorg/myrepo \
  --input tag=v1.2.0

# Attach triggers for automatic execution
syn triggers create --workflow sdlc-pr-review --from-package sdlc-trunk
syn triggers create --workflow sdlc-ci-fix --from-package sdlc-trunk
syn triggers create --workflow sdlc-release-prep --from-package sdlc-trunk
```

## Notes

- **CI Self-Healing requires webhooks** — the `check_run` event is not available via the Events API (GitHub limitation). You need a webhook URL configured (e.g., via Cloudflare tunnel).
- **PR Review works with polling** — `pull_request` events are available via both webhooks and the Events API poller.
- **Release Prep works with polling** — `release` events are available via both channels.
