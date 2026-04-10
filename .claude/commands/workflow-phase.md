---
allowed-tools: Read, Write, WebFetch
description: Scaffold a new workflow phase file following the Claude command standard
argument-hint: [workflow-path] [phase-name] [description]
model: sonnet
---

# Workflow Phase

Scaffold a new phase file at the correct path under `WORKFLOW_PATH`, following the Claude command standard. Reference `Variables` and follow the `Workflow` to produce a complete, production-ready phase file.

## Variables

WORKFLOW_PATH: $1
PHASE_NAME: $2
DESCRIPTION: $3

## Workflow

1. **Load the standard** — WebFetch https://code.claude.com/docs/en/commands.md for the latest Claude command format.

2. **Read the workflow inputs** — Read `WORKFLOW_PATH/workflow.yaml` to extract the `inputs` list. These become the Variables section in the new phase.

3. **Determine the target path** — slugify `PHASE_NAME` (lowercase, hyphens) → `WORKFLOW_PATH/phases/<phase-name>.md`.

4. **Choose the right model:**
   - `haiku` — context gathering, lightweight reads, simple verification passes
   - `sonnet` — analysis, implementation, decision-making, anything that writes or posts

5. **Determine allowed-tools:**
   - Always include: `bash, git, read`
   - Add `edit` only if this phase modifies files
   - **If edit is included, the phase MUST also commit and push** — ephemeral constraint: no state carries between phases

6. **Determine artifact name** — derive a kebab-case output artifact name from PHASE_NAME (e.g., "Analyze Changes" → `findings`, "Gather Context" → `context`).

7. **Write the phase file** using this exact structure:

   ```md
   ---
   model: haiku|sonnet
   allowed-tools: bash, git, read[, edit]
   description: DESCRIPTION
   ---

   # PHASE_NAME

   [One sentence purpose. Reference `Variables` and `Workflow`.]

   ## Variables

   [List every input from workflow.yaml that this phase uses]
   VAR_NAME: {{input_name}}

   ## Workflow

   [If not the first phase, step 1 must be:]
   1. Review the previous phase output — see `PREVIOUS_OUTPUT` (or the relevant named var) in Variables above.

   [Numbered steps. Include exact commands.]

   ## Report

   Write output to `artifacts/output/<artifact-name>.md`:
   [Describe the structure and content of the output file.]
   ```

8. **Add artifact declarations to workflow.yaml** — open `WORKFLOW_PATH/workflow.yaml` and add `input_artifacts` and `output_artifacts` to this phase's entry.

9. **Ephemeral reminder:** if this phase uses `edit`, verify the Workflow includes `git add`, `git commit`, and `git push origin {{branch}}` before the Report step.

## Report

- Path of the created phase file
- workflow.yaml updated with `input_artifacts` / `output_artifacts` for this phase
- Variables detected from workflow.yaml inputs
- Model chosen and why
- Output artifact name and path
- Any inputs referenced that don't appear in workflow.yaml (flag as missing)
