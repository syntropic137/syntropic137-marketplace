# syntropic137-marketplace — Agent Reference

## 1. Repo Purpose

High-quality, ready-to-run workflow plugins for the Syntropic137 platform. These are the first thing new users install — quality matters. Each plugin must work end-to-end on a fresh install with no manual setup beyond providing inputs.

Users install plugins with:

```
syn workflow install <plugin-name>
```

## 2. Workflow Phase Files = Claude Commands

Workflow phase files (`phases/*.md`) follow the **Claude command standard** exactly. A workflow is a multi-phase command — each phase is one command invocation. When authoring or reviewing phase files, treat them as Claude custom slash commands.

Key docs to fetch on demand:

- Commands: https://code.claude.com/docs/en/commands.md
- Skills: https://code.claude.com/docs/en/skills.md
- Hooks: https://code.claude.com/docs/en/hooks.md
- Settings and tools: https://code.claude.com/docs/en/settings.md

**Rule: WebFetch the relevant doc above before authoring any phase file, command, or skill.**

The canonical workflow authoring standard (kept in sync with this file) lives in the Syntropic platform repo at `packages/syn-domain/CLAUDE.md`.

## 3. Phase File Standard Format

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
- Use **haiku** for lightweight phases (context gathering, verification); use **sonnet** for analysis and implementation
- **Punctuation style: prefer `:` and `,` over `-` and em dashes** — cleaner, more scannable, plays better with token budgets

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
| `phases` | Ordered list with `id`, `name`, `order`, `execution_type`, `prompt_file`, `input_artifacts`, `output_artifacts`, `allowed_tools` |

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
- [ ] Phase models match complexity (haiku vs sonnet)
- [ ] Workflow runs end-to-end on a clean workspace with only declared inputs provided
- [ ] `syntropic137-plugin.json` manifest is valid (CI schema validation runs on push)
