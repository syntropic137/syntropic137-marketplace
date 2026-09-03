#!/usr/bin/env python3
"""Mirror platform validator-only rules that the JSON Schemas don't express.

These rules live in Pydantic `field_validator`s on the core platform (not in
the exported JSON Schemas), so `check-jsonschema` reports "valid" for content
the platform actually refuses to load. This script re-implements the small
subset of that logic needed to catch it in this repo's CI.

Usage:
    python check_semantic_rules.py
    python check_semantic_rules.py --plugins-dir plugins --marketplace-json marketplace.json

Exit codes:
    0: no semantic rule violations found
    1: one or more semantic rule violations found
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

# Highest core-repo release these rules were verified against. Bumped by hand
# per CONTRIBUTING.md's "Schema versioning" runbook whenever a human confirms
# the core repo shipped a new validator-only rule.
KNOWN_PLATFORM_VERSION = (0, 27, 0)

RULE_INTRODUCED_AT = {
    "closed_tool_vocab": (0, 27, 0),
    "max_tokens_rejected": (0, 27, 0),
}

# Mirrors ToolName / canonical_tool_name (core repo@v0.27.0
# packages/syn-shared/src/syn_shared/tools.py:26-58). Matched case-insensitively.
CANONICAL_TOOL_NAMES = {
    "bash",
    "edit",
    "glob",
    "grep",
    "ls",
    "multiedit",
    "read",
    "task",
    "todoread",
    "todowrite",
    "webfetch",
    "websearch",
    "write",
}

MAX_TOKENS_KEYS = {"max_tokens", "max-tokens"}

UNARY_OPERATORS = {"not_empty", "is_empty"}
BINARY_OPERATORS = {"eq", "neq", "contains"}
LIST_OPERATORS = {"in", "not_in"}


def _rule_active(rule: str) -> bool:
    return KNOWN_PLATFORM_VERSION >= RULE_INTRODUCED_AT[rule]


def _split_tool_list(value: Any) -> list[str]:
    """Normalize an allowed-tools/allowed_tools value (list or comma string)."""
    if isinstance(value, str):
        return [t.strip() for t in value.split(",") if t.strip()]
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def read_frontmatter(phase_path: Path) -> dict[str, Any] | None:
    """Extract the YAML frontmatter block from a phase markdown file, if any."""
    content = phase_path.read_text()
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else None


def check_closed_tool_vocab(plugins_dir: Path) -> list[str]:
    """Every allowed_tools/allowed-tools entry must be a known tool name."""
    if not _rule_active("closed_tool_vocab"):
        return []

    errors: list[str] = []

    for workflow_path in sorted(plugins_dir.rglob("workflow.yaml")):
        doc = yaml.safe_load(workflow_path.read_text()) or {}
        for phase in doc.get("phases") or []:
            for tool in _split_tool_list(phase.get("allowed_tools")):
                if tool.lower() not in CANONICAL_TOOL_NAMES:
                    errors.append(
                        f"{workflow_path}: unknown tool '{tool}' in allowed_tools "
                        f"for phase '{phase.get('id', '?')}'"
                    )

    for phase_path in sorted(plugins_dir.rglob("phases/*.md")):
        data = read_frontmatter(phase_path)
        if not data:
            continue
        for tool in _split_tool_list(data.get("allowed-tools")):
            if tool.lower() not in CANONICAL_TOOL_NAMES:
                errors.append(f"{phase_path}: unknown tool '{tool}' in allowed-tools frontmatter")

    return errors


def check_max_tokens_rejected(plugins_dir: Path) -> list[str]:
    """max_tokens/max-tokens is a hard error if present at all, any value."""
    if not _rule_active("max_tokens_rejected"):
        return []

    errors: list[str] = []

    for workflow_path in sorted(plugins_dir.rglob("workflow.yaml")):
        doc = yaml.safe_load(workflow_path.read_text()) or {}
        for phase in doc.get("phases") or []:
            for key in MAX_TOKENS_KEYS:
                if key in phase:
                    errors.append(
                        f"{workflow_path}: '{key}' present in phase '{phase.get('id', '?')}' "
                        "(rejected regardless of value)"
                    )

    for phase_path in sorted(plugins_dir.rglob("phases/*.md")):
        data = read_frontmatter(phase_path)
        if not data:
            continue
        for key in MAX_TOKENS_KEYS:
            if key in data:
                errors.append(f"{phase_path}: '{key}' present in frontmatter (rejected regardless of value)")

    return errors


def check_trigger_operator_value(plugins_dir: Path) -> list[str]:
    """Trigger condition operator/value shape must be internally consistent."""
    errors: list[str] = []

    for triggers_path in sorted(plugins_dir.rglob("triggers.json")):
        try:
            doc = json.loads(triggers_path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{triggers_path}: invalid JSON ({exc})")
            continue

        for trigger in doc.get("triggers") or []:
            for condition in trigger.get("conditions") or []:
                operator = condition.get("operator")
                field = condition.get("field", "?")
                has_value = "value" in condition
                value = condition.get("value")

                if operator in UNARY_OPERATORS:
                    if has_value:
                        errors.append(
                            f"{triggers_path}: operator '{operator}' must not have a 'value' "
                            f"(field '{field}')"
                        )
                elif operator in BINARY_OPERATORS:
                    if not has_value or isinstance(value, (list, dict)):
                        errors.append(
                            f"{triggers_path}: operator '{operator}' requires a scalar 'value' "
                            f"(field '{field}')"
                        )
                elif operator in LIST_OPERATORS:
                    if not has_value or not isinstance(value, list):
                        errors.append(
                            f"{triggers_path}: operator '{operator}' requires an array 'value' "
                            f"(field '{field}')"
                        )

    return errors


def check_marketplace_manifest_versions(marketplace_path: Path, repo_root: Path) -> list[str]:
    """Every marketplace.json plugin entry's version must match its manifest's version."""
    errors: list[str] = []
    doc = json.loads(marketplace_path.read_text())

    for plugin in doc.get("plugins") or []:
        name = plugin.get("name", "?")
        marketplace_version = plugin.get("version")
        source = plugin.get("source", "")
        manifest_path = repo_root / source.lstrip("./") / "syntropic137-plugin.json"

        if not manifest_path.exists():
            errors.append(f"{marketplace_path}: plugin '{name}' source manifest not found at {manifest_path}")
            continue

        manifest_version = json.loads(manifest_path.read_text()).get("version")
        if marketplace_version != manifest_version:
            errors.append(
                f"{marketplace_path}: plugin '{name}' version mismatch: "
                f"marketplace.json has '{marketplace_version}', {manifest_path} has '{manifest_version}'"
            )

    return errors


def check_semantic_rules(plugins_dir: Path, marketplace_path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    errors += check_closed_tool_vocab(plugins_dir)
    errors += check_max_tokens_rejected(plugins_dir)
    errors += check_trigger_operator_value(plugins_dir)
    errors += check_marketplace_manifest_versions(marketplace_path, repo_root)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugins-dir", default="plugins", help="Plugins directory")
    parser.add_argument("--marketplace-json", default="marketplace.json", help="Path to marketplace.json")
    parser.add_argument("--repo-root", default=".", help="Repo root, for resolving marketplace.json plugin sources")
    args = parser.parse_args()

    plugins_dir = Path(args.plugins_dir)
    marketplace_path = Path(args.marketplace_json)
    repo_root = Path(args.repo_root)

    if not plugins_dir.is_dir():
        print(f"Error: plugins directory '{plugins_dir}' not found", file=sys.stderr)
        return 1
    if not marketplace_path.is_file():
        print(f"Error: marketplace file '{marketplace_path}' not found", file=sys.stderr)
        return 1

    errors = check_semantic_rules(plugins_dir, marketplace_path, repo_root)

    if errors:
        print()
        for error in errors:
            print(f"::error::{error}")
        print(f"\n{len(errors)} semantic rule violation(s) found")
        return 1

    print("All semantic rule checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
