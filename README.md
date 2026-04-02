# Syntropic137 Marketplace

Official workflow plugin marketplace for [Syntropic137](https://github.com/syntropic137/syntropic137). Install workflow packages with embedded triggers using the `syn` CLI.

## Quick Start

```bash
# Register this marketplace
syn marketplace add syntropic137/syntropic137-marketplace

# Browse available plugins
syn workflow search ""

# Install a plugin
syn workflow install code-review

# Run a workflow
syn workflow run code-review --input pr_number=42 --input repository=myorg/myrepo
```

## Available Plugins

| Plugin | Description | Category |
|--------|-------------|----------|
| [code-review](plugins/code-review/) | AI-powered code review on pull requests | sdlc |

## Plugin Structure

Each plugin follows the Syntropic package format:

```
plugins/<name>/
  syntropic137-plugin.json       # Plugin manifest (name, version, author)
  README.md                      # Plugin documentation
  workflows/
    <workflow-name>/
      workflow.yaml              # Workflow definition (phases, inputs)
      triggers.json              # Embedded trigger definitions (optional)
      phases/
        <phase-id>.md            # Phase prompts (YAML frontmatter + Markdown)
```

### File Formats

| File | Format | Purpose |
|------|--------|---------|
| `marketplace.json` | JSON | Registry index — lists all plugins |
| `syntropic137-plugin.json` | JSON | Plugin manifest — name, version, metadata |
| `triggers.json` | JSON | Trigger definitions — event, conditions, input mapping |
| `workflow.yaml` | YAML | Workflow definition — phases, inputs, repository |
| `phases/*.md` | Markdown | Phase prompts — YAML frontmatter + prompt body |

### Phase Frontmatter

```yaml
---
model: sonnet                    # Claude model (sonnet, opus, haiku)
allowed-tools: bash, git, read   # Tools available to the agent
timeout-seconds: 600             # Phase timeout
max-tokens: 16384                # Max output tokens
argument-hint: "[description]"   # Claude Code argument hint
---
```

### Trigger Format

```json
{
  "triggers": [
    {
      "name": "trigger-name",
      "description": "When this trigger fires",
      "event": "pull_request",
      "conditions": [
        { "field": "action", "operator": "in", "value": ["opened"] }
      ],
      "input_mapping": {
        "workflow_input": "webhook.payload.path"
      },
      "config": {
        "max_attempts": 3,
        "cooldown_seconds": 300,
        "daily_limit": 20,
        "budget_per_trigger_usd": 2.00
      }
    }
  ]
}
```

## Creating Your Own Plugin

1. **Scaffold** a new plugin:
   ```bash
   syn workflow init my-plugin
   ```

2. **Define** your workflow in `workflow.yaml` with phases and inputs

3. **Write** phase prompts as Markdown files with YAML frontmatter

4. **Add triggers** (optional) to auto-run on GitHub events

5. **Test locally:**
   ```bash
   syn workflow install ./my-plugin
   syn workflow run my-workflow --input key=value
   ```

6. **Publish** by adding to a marketplace repo or sharing the git URL:
   ```bash
   # Others can install directly from your repo
   syn workflow install github.com/yourorg/your-plugin
   ```

## Contributing

Want to add a plugin to this marketplace? See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
