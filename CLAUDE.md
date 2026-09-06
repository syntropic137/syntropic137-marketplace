# syntropic137-marketplace — Agent Reference

## 1. Repo Purpose

High-quality, ready-to-run workflow plugins for the Syntropic137 platform. These are the first thing new users install — quality matters. Each plugin must work end-to-end on a fresh install with no manual setup beyond providing inputs.

Users install plugins with:

```
syn workflow install <plugin-name>
```

## 2. Phases Run On A Harness, Chosen Per Phase

A workflow is a multi-phase pipeline. Each phase is one headless agent invocation, and the platform runs that invocation on one of two harnesses:

| `agent.provider` | Runs | Notes |
|---|---|---|
| `claude` | `claude -p` | The default when no `agent` block is declared |
| `codex` | `codex exec` | Requires `CODEX_AUTH_JSON` on the platform stack |

Harness selection is declared **per phase in `workflow.yaml`**, never in the phase markdown. See section 3a.

**Phase files for claude phases** follow the Claude command standard: the body may reference slash commands and skills by name. When authoring or reviewing one, treat it as a Claude custom slash command and fetch the relevant doc first:

- Commands: https://code.claude.com/docs/en/commands.md
- Skills: https://code.claude.com/docs/en/skills.md
- Hooks: https://code.claude.com/docs/en/hooks.md
- Settings and tools: https://code.claude.com/docs/en/settings.md

**Rule: WebFetch the relevant doc above before authoring any phase file for a claude phase, or any command or skill.**

**Phase files for codex phases** are plain instruction prompts. Slash commands, Claude plugins, hook events, subagent tracking, and TodoWrite are Claude-only. A phase that needs any of them must stay on `claude`.

The canonical workflow authoring standard lives in the Syntropic platform repo docs at `apps/syn-docs/content/docs/guide/workflows.mdx`.

## 3. Phase File Standard Format

Phase frontmatter carries **no harness field**. The platform's `phase-frontmatter.schema.json` sets `additionalProperties: false` and defines only `model`, `allowed-tools`, `timeout-seconds`, `execution-type`, `description`, `argument-hint`, and the deprecated `max-tokens` (declaring which is itself an error). An `agent:` key here is a validation error. Harness selection belongs in `workflow.yaml` (section 3a).

```md
---
model: sonnet|haiku
allowed-tools: bash, git, read, edit
description: One-line description of what this phase does
---

# Phase Name

Brief purpose statement. References `Variables` and `Workflow` sections.

## Variables

DYNAMIC_VAR: {{input_name}}
STATIC_VAR: value

## Workflow

1. Numbered step
2. Numbered step

## Report

How to produce the output / what to write to stdout for the next phase.
```

Rules:

- **Variables section is required** — list every `{{variable}}` used in the file, at the top of the body
- Dynamic vars (from workflow inputs) come first; static defaults/constants come second
- Workflow steps are numbered
- Report section tells the agent exactly what artifact to produce and in what format
- Be token-efficient: no redundant preamble, no "you are an AI assistant" filler
- Right-size the model to the work. The tier idea applies on both harnesses, only the names differ. On **claude** phases use **haiku** for lightweight work (context gathering, verification) and **sonnet** for analysis and implementation. On **codex** phases name a concrete model id, there is no tier alias
- `allowed-tools` currently enforces nothing on either harness. Per ADR-069 the platform never populates it, so no tool restriction is ever applied and the codex-side rejection guard is unreachable. Declare it to document intent, never as a control. To actually bound a phase, put it on `codex` and set `sandbox` in `workflow.yaml`. Note `sandbox` is filesystem-only, network egress is available at every level, and a phase that publishes under `artifacts/output/` needs `full-access`
- **Punctuation style: prefer `:` and `,` over `-` and em dashes** — cleaner, more scannable, plays better with token budgets

## 3a. Harness Selection (`agent` block in `workflow.yaml`)

The platform selects a harness per phase through an `agent` block on the phase entry in `workflow.yaml`. There is no CLI flag and no environment variable for it, and it cannot be set from phase frontmatter.

```yaml
phases:
  - id: implement
    prompt_file: phases/implement.md
    agent:
      provider: claude          # claude | codex, claude is the default
      model: sonnet
  - id: review
    prompt_file: phases/review.md
    agent:
      provider: codex
      model: gpt-5.6-sol        # name a concrete model, see below
      sandbox: read-only        # codex honours this, claude does not
```

Fields: `provider`, `model`, `sandbox` (`read-only` | `workspace-write` | `full-access`), `allow_delegation`.

Rules that bite:

- **Codex phases need `CODEX_AUTH_JSON`** on the platform stack. Without it the phase fails to provision. A marketplace plugin that ships codex phases is therefore asking every installer to set that variable, so say so in the plugin README.
- **Name a concrete model id on every codex phase.** Codex does not report its model on the wire, so omitting `model` leaves the run **unpriced**: no cost lands in `syn costs` for that phase.
- **`allowed_tools` is not a control on either harness.** Do not rely on it to restrict a phase. Use `sandbox` on a codex phase, which is the only enforced boundary today.
- **`sandbox` constrains codex only** today. Declaring `read-only` on a claude phase does not restrict it, so do not document it as a guarantee there.
- **Claude-only features**: hook events, subagent tracking, TodoWrite, and Claude plugins.

### KNOWN GAP: this marketplace cannot ship `agent` blocks yet

Every shipped plugin under `plugins/` declares **no** `agent` block, so every phase runs on the default `claude` harness. That is not an oversight in the phase files, it is a version floor:

- `marketplace.json` declares `syntropic137.min_platform_version: 0.25.2`.
- CI (`.github/workflows/validate.yml`) fetches `workflow.schema.json` from the platform repo at that exact tag and validates every `workflow.yaml` against it.
- The `agent` block does not exist in the v0.25.2 schema. `provider`, `model` and `allow_delegation` first appear in **v0.26.0**. `sandbox` first appears in **v0.28.0**.
- The schema sets `additionalProperties: false`, so adding an `agent` block today fails CI rather than being ignored.

**Do not add `agent` blocks to shipped plugins until `min_platform_version` is raised.** Raising it to `0.26.0` unlocks `provider`, `model` and `allow_delegation`. Raising it to `0.28.0` also unlocks `sandbox`. Either raise excludes installers on older platform versions, so it is a marketplace-wide compatibility decision, not a per-plugin one.

A second, smaller gap: even once the floor is raised, there is no way to declare a harness from a phase markdown file. Frontmatter forbids unknown keys and has no `agent` field. A phase file's `model: sonnet` therefore carries no harness information on its own, and a reader has to open `workflow.yaml` to know which harness the phase runs on.

## 4. Artifact System

Phases exchange data through the artifact workspace. Every phase runs in an ephemeral container with this layout:

```
/workspace/
├── artifacts/
│   ├── input/    ← Previous phase outputs (injected by platform, read-only)
│   │             └── {phase_id}.md
│   └── output/   ← Write YOUR deliverables here (ONLY path collected)
└── repos/        ← Clone repositories here
```

**Writing artifacts** — every phase must write its output to `artifacts/output/<name>.md` before the session ends. The workspace root is injected by the platform system prompt — phase files use relative paths only.

**Reading artifacts** — previous phase outputs are available two ways:
- As inline variable substitution: `{{phase_id}}` in the phase file is replaced with the phase's output content
- As files in `artifacts/input/{phase_id}.md` (the platform injects these; the workspace system prompt explains the paths)

Phase files reference previous phases via `{{phase_id}}` in the Variables section. No hardcoded paths in phase files.

**Declaring artifacts in workflow.yaml** — each phase must declare:

```yaml
- id: analyze
  input_artifacts: []             # phase IDs whose outputs to inject
  output_artifacts:
    - findings                    # names of files this phase writes
```

The `output_artifacts` list is informational metadata; what actually gets collected is everything written to `artifacts/output/`.

## 5. Ephemeral Phase Constraint (CRITICAL)

State does **not** survive between phases except via:

- **Artifact files** — written to `artifacts/output/` (workspace root is platform-injected), available to next phase via `{{phase_id}}` variable substitution
- **GitHub** — comments, PR reviews, releases posted via `gh`
- **Git push** — if a phase edits files, it MUST commit AND push in the same phase

You cannot edit in phase 2 and push in phase 3. Push must happen in the same phase as the edit.

## 6. `--repo` Flag Rule

All `gh` CLI subcommands (`pr`, `issue`, `release`, `checks`, etc.) MUST include `--repo {{repository}}`. The workspace git remote is not reliable.

`gh api` calls with `repos/` in the path are fine as-is.

## 7. Plugin Structure

```
plugins/
└── my-plugin/
    ├── syntropic137-plugin.json    # manifest: name, version, description, author
    ├── README.md
    └── workflows/
        └── my-workflow/
            ├── workflow.yaml       # id, inputs, phases list
            ├── triggers.json       # GitHub event triggers + input_mapping
            └── phases/
                ├── phase-one.md
                └── phase-two.md
```

### `syntropic137-plugin.json` fields

| Field | Required | Notes |
|---|---|---|
| `manifest_version` | yes | Always `1` |
| `name` | yes | Kebab-case, matches directory name |
| `version` | yes | Semver |
| `description` | yes | One sentence |
| `author` | yes | GitHub username or org |
| `license` | yes | e.g. `"MIT"` |
| `repository` | yes | Full GitHub URL |

### `workflow.yaml` fields

| Field | Notes |
|---|---|
| `id` | Kebab-case identifier |
| `inputs` | List of `{name, description, required, default}` |
| `phases` | Ordered list with `id`, `name`, `order`, `execution_type`, `prompt_file`, `input_artifacts`, `output_artifacts`, `allowed_tools`, and (platform >= 0.26.0 only, see section 3a) `agent` |

## 8. Existing Plugins

| Plugin | Workflows |
|---|---|
| `code-review` | `review` — analyze PR diff, post structured review |
| `sdlc-trunk` | `pr-review`, `ci-fix`, `release-prep` — full trunk-based dev lifecycle |

## 9. Quality Checklist

Before submitting or merging a new plugin:

- [ ] All `{{variables}}` declared in every phase's Variables section
- [ ] Every phase writes its output to `artifacts/output/<name>.md` (relative path, workspace root from platform)
- [ ] Non-first phases reference previous outputs via `{{phase_id}}` variable in the Variables section (no hardcoded paths)
- [ ] `input_artifacts` and `output_artifacts` declared in every phase of `workflow.yaml`
- [ ] Every phase that edits files also commits and pushes in the same phase
- [ ] All `gh` subcommands include `--repo {{repository}}`
- [ ] Phase models match complexity. On claude phases that is haiku vs sonnet, on codex phases it is a concrete model id
- [ ] No `agent` block in any `workflow.yaml` while `min_platform_version` is below `0.26.0` (see section 3a)
- [ ] No phase relies on `allowed-tools` as a restriction. It enforces nothing on either harness
- [ ] Workflow runs end-to-end on a clean workspace with only declared inputs provided
- [ ] `syntropic137-plugin.json` manifest is valid (CI schema validation runs on push)
