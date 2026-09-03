# Contributing to Syntropic137 Marketplace

This is the **official Syntropic137 workflow marketplace** — and a reference implementation for building your own. Whether you're adding a plugin here or creating a standalone marketplace repo, this guide covers the full process.

## Plugin Structure

Every plugin follows the [Syntropic package format](https://github.com/syntropic137/syntropic137):

```
plugins/<name>/
  syntropic137-plugin.json       # Plugin manifest
  README.md                      # Documentation
  workflows/
    <workflow-name>/
      workflow.yaml              # Workflow definition
      triggers.json              # Trigger definitions (optional)
      phases/
        <phase-id>.md            # Phase prompts
```

## Schema Validation

All files are validated against JSON schemas from the core Syntropic137 repo. The schemas are the authoritative specification for each file format.

### Which schemas apply

| File | Schema | Validates |
|------|--------|-----------|
| `marketplace.json` | `marketplace.schema.json` | Registry index structure |
| `syntropic137-plugin.json` | `plugin-manifest.schema.json` | Plugin metadata |
| `workflow.yaml` | `workflow.schema.json` | Workflow definition, phases, inputs |
| `triggers.json` | `triggers.schema.json` | Trigger events, conditions, mappings |
| `phases/*.md` frontmatter | `phase-frontmatter.schema.json` | Model, tools, hints |

### Schema versioning

The marketplace declares which platform version it targets in `marketplace.json`:

```json
{
  "syntropic137": {
    "min_platform_version": "0.19.7"
  }
}
```

CI fetches schemas from the core repo at the **matching git tag** (`v0.19.7`). When the platform releases new schemas:

1. Update `min_platform_version` in `marketplace.json`
2. Fix any validation errors from the new schemas
3. CI automatically fetches the new schema version
4. Check whether the core repo added new `@field_validator`/`@model_validator` logic since the previous pin (start at `core repo@main docs/adrs/ADR-053-plugin-schema-generation-strategy.md`, which documents that such logic is invisible to the exported JSON Schemas). If it did, the schema-level checks above won't catch it, only `.github/scripts/check_semantic_rules.py` can.

This ensures your marketplace is always validated against the schemas for the platform version you support.

### Semantic rules (`check_semantic_rules.py`)

Some platform validation lives in Pydantic `field_validator`s that are never exported to the JSON Schemas, so `check-jsonschema` reports content as "valid" even when the platform refuses to load it (e.g. an `allowed_tools` entry outside the platform's closed tool vocabulary). `.github/scripts/check_semantic_rules.py` hand-mirrors the small number of these rules this repo currently knows about.

Its enforcement is gated by `KNOWN_PLATFORM_VERSION`, a constant in the script itself, **independent of `marketplace.json`'s `min_platform_version`**. This is deliberate: it keeps the semantic checks active in every CI run regardless of what floor version the repo happens to be pinned to.

Whenever a human confirms the core repo shipped a release with new validator-only rules:

1. Bump `KNOWN_PLATFORM_VERSION` in `check_semantic_rules.py` to that release, whether or not `min_platform_version` itself is also being raised
2. If the new rule is one this script doesn't yet mirror, add a check function plus a `RULE_INTRODUCED_AT` entry and rejection-path tests in `test_check_semantic_rules.py`

### Running validation locally

```bash
# Fetch schemas (same as CI)
SCHEMA_VERSION="v0.19.7"  # match your min_platform_version
SCHEMA_BASE="https://raw.githubusercontent.com/syntropic137/syntropic137/${SCHEMA_VERSION}/schemas/plugin"
mkdir -p .schemas
for s in marketplace.schema.json plugin-manifest.schema.json workflow.schema.json triggers.schema.json phase-frontmatter.schema.json; do
  curl -sf "${SCHEMA_BASE}/${s}" -o ".schemas/${s}"
done

# Install validator
pip install check-jsonschema pyyaml

# Validate
check-jsonschema --schemafile .schemas/marketplace.schema.json marketplace.json
check-jsonschema --schemafile .schemas/plugin-manifest.schema.json plugins/my-plugin/syntropic137-plugin.json
python3 -c "import yaml,json,sys; json.dump(yaml.safe_load(open('plugins/my-plugin/workflows/my-wf/workflow.yaml')),sys.stdout)" | \
  check-jsonschema --schemafile .schemas/workflow.schema.json -
```

## Adding a Plugin to This Marketplace

1. **Create your plugin directory:**
   ```bash
   mkdir -p plugins/my-plugin/workflows/my-workflow/phases
   ```

2. **Add a manifest** (`plugins/my-plugin/syntropic137-plugin.json`):
   ```json
   {
     "manifest_version": 1,
     "name": "my-plugin",
     "version": "0.1.0",
     "description": "What this plugin does",
     "author": "your-name",
     "license": "MIT"
   }
   ```

3. **Define your workflow** (`workflow.yaml`):
   ```yaml
   id: my-workflow
   name: "My Workflow"
   description: "What this workflow does"
   type: implementation
   classification: simple

   inputs:
     - name: repository
       description: "Target repository (owner/repo)"
       required: true

   phases:
     - id: execute
       name: "Execute"
       order: 1
       execution_type: sequential
       prompt_file: phases/execute.md
       allowed_tools: [bash, read]
   ```

4. **Write phase prompts** (`phases/execute.md`):
   ```markdown
   ---
   model: sonnet
   allowed-tools: bash, read
   ---

   # Phase prompt

   Your instructions to the agent here. Use `{{repository}}` to reference inputs.
   ```

5. **Add triggers** (optional, `triggers.json`):
   ```json
   {
     "triggers": [{
       "name": "on-event",
       "event": "pull_request",
       "conditions": [
         { "field": "action", "operator": "in", "value": ["opened"] }
       ],
       "input_mapping": {
         "repository": "repository.full_name"
       }
     }]
   }
   ```
   > **Note:** Triggers in the marketplace are *examples* showing which events and conditions a plugin supports. Safety guardrails (max fires, cooldown, budget) are configured by the user when they register a trigger at runtime via `syn triggers register`.

6. **Register in `marketplace.json`:**
   ```json
   {
     "name": "my-plugin",
     "source": "./plugins/my-plugin",
     "version": "0.1.0",
     "description": "What this plugin does",
     "category": "sdlc",
     "tags": ["relevant", "tags"]
   }
   ```

7. **Test locally:**
   ```bash
   syn workflow install ./plugins/my-plugin
   syn workflow run my-workflow --input repository=myorg/myrepo
   ```

8. **Open a PR** — CI will validate all schemas and structure automatically.

## Building Your Own Marketplace

Any GitHub repo can be a Syntropic137 marketplace. Fork this repo or start from scratch:

1. **Create `marketplace.json`** at the repo root with `syntropic137.type: "workflow-marketplace"`
2. **Add plugins** following the structure above
3. **Copy `.github/workflows/validate.yml`** for schema validation CI
4. **Set `min_platform_version`** to the platform version you target

Users register your marketplace with:
```bash
syn marketplace add your-org/your-marketplace
```

Then install plugins by name:
```bash
syn workflow install my-plugin
```

## Trigger Safety

Marketplace triggers define **what events and conditions** a plugin responds to, not how aggressively it runs. Safety guardrails — max attempts, cooldown, daily limits, budget caps — are **runtime configuration** that users set per-trigger when they register via `syn triggers register`.

This separation means:
- **Marketplace authors** focus on correct event matching and input mapping.
- **Users** choose guardrails appropriate for their environment and budget.

See `syn triggers register --help` for the full set of configurable safety options.

## License

All plugins in this marketplace are MIT-licensed. By contributing, you agree to license your contribution under MIT.
