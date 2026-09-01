"""Tests for check_semantic_rules.py."""

from __future__ import annotations

import json
from pathlib import Path

from check_semantic_rules import (
    check_closed_tool_vocab,
    check_marketplace_manifest_versions,
    check_max_tokens_rejected,
    check_trigger_operator_value,
)


# --- helpers ---

def make_workflow(tmp_path: Path, plugin: str, workflow: str, phases: list[dict]) -> Path:
    wf_dir = tmp_path / "plugins" / plugin / "workflows" / workflow
    wf_dir.mkdir(parents=True)
    doc = {"id": workflow, "phases": phases}
    workflow_path = wf_dir / "workflow.yaml"
    workflow_path.write_text(_to_yaml(doc))
    return workflow_path


def _to_yaml(doc: dict) -> str:
    import yaml

    return yaml.safe_dump(doc)


def make_phase_file(tmp_path: Path, plugin: str, workflow: str, phase_id: str, frontmatter: str) -> Path:
    phases_dir = tmp_path / "plugins" / plugin / "workflows" / workflow / "phases"
    phases_dir.mkdir(parents=True, exist_ok=True)
    phase_path = phases_dir / f"{phase_id}.md"
    phase_path.write_text(f"---\n{frontmatter}\n---\n\n# {phase_id}\n")
    return phase_path


def make_triggers(tmp_path: Path, plugin: str, workflow: str, conditions: list[dict]) -> Path:
    wf_dir = tmp_path / "plugins" / plugin / "workflows" / workflow
    wf_dir.mkdir(parents=True, exist_ok=True)
    triggers_path = wf_dir / "triggers.json"
    doc = {"triggers": [{"name": "on-event", "event": "pull_request", "conditions": conditions}]}
    triggers_path.write_text(json.dumps(doc))
    return triggers_path


def make_marketplace(tmp_path: Path, plugins: list[dict]) -> Path:
    marketplace_path = tmp_path / "marketplace.json"
    marketplace_path.write_text(json.dumps({"plugins": plugins}))
    return marketplace_path


def make_manifest(tmp_path: Path, source: str, version: str) -> None:
    manifest_dir = tmp_path / source
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "syntropic137-plugin.json").write_text(json.dumps({"version": version}))


# --- check_closed_tool_vocab ---

def test_closed_tool_vocab_rejects_unknown_name(tmp_path: Path) -> None:
    make_phase_file(tmp_path, "my-plugin", "my-wf", "execute", "allowed-tools: bash, git, read")

    errors = check_closed_tool_vocab(tmp_path / "plugins")

    assert len(errors) == 1
    assert "git" in errors[0]
    assert "execute.md" in errors[0]


def test_closed_tool_vocab_accepts_known_names(tmp_path: Path) -> None:
    make_phase_file(tmp_path, "my-plugin", "my-wf", "execute", "allowed-tools: bash, read, edit")

    errors = check_closed_tool_vocab(tmp_path / "plugins")

    assert errors == []


def test_closed_tool_vocab_rejects_unknown_name_in_workflow_yaml(tmp_path: Path) -> None:
    make_workflow(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"id": "execute", "allowed_tools": ["bash", "git", "read"]}],
    )

    errors = check_closed_tool_vocab(tmp_path / "plugins")

    assert len(errors) == 1
    assert "git" in errors[0]
    assert "workflow.yaml" in errors[0]


def test_closed_tool_vocab_accepts_known_names_in_workflow_yaml(tmp_path: Path) -> None:
    make_workflow(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"id": "execute", "allowed_tools": ["bash", "read"]}],
    )

    errors = check_closed_tool_vocab(tmp_path / "plugins")

    assert errors == []


# --- check_max_tokens_rejected ---

def test_max_tokens_key_present_rejected_even_when_null(tmp_path: Path) -> None:
    make_phase_file(tmp_path, "my-plugin", "my-wf", "execute", "allowed-tools: bash\nmax-tokens: null")

    errors = check_max_tokens_rejected(tmp_path / "plugins")

    assert len(errors) == 1
    assert "max-tokens" in errors[0]


def test_max_tokens_key_absent_passes(tmp_path: Path) -> None:
    make_phase_file(tmp_path, "my-plugin", "my-wf", "execute", "allowed-tools: bash")

    errors = check_max_tokens_rejected(tmp_path / "plugins")

    assert errors == []


# --- check_trigger_operator_value ---

def test_trigger_operator_value_in_requires_array(tmp_path: Path) -> None:
    make_triggers(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"field": "action", "operator": "in", "value": "opened"}],
    )

    errors = check_trigger_operator_value(tmp_path / "plugins")

    assert len(errors) == 1
    assert "in" in errors[0]
    assert "array" in errors[0]


def test_trigger_operator_value_in_with_array_passes(tmp_path: Path) -> None:
    make_triggers(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"field": "action", "operator": "in", "value": ["opened", "synchronize"]}],
    )

    errors = check_trigger_operator_value(tmp_path / "plugins")

    assert errors == []


def test_trigger_operator_value_not_empty_forbids_value(tmp_path: Path) -> None:
    make_triggers(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"field": "title", "operator": "not_empty", "value": "anything"}],
    )

    errors = check_trigger_operator_value(tmp_path / "plugins")

    assert len(errors) == 1
    assert "not_empty" in errors[0]


def test_trigger_operator_value_not_empty_without_value_passes(tmp_path: Path) -> None:
    make_triggers(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"field": "title", "operator": "not_empty"}],
    )

    errors = check_trigger_operator_value(tmp_path / "plugins")

    assert errors == []


def test_trigger_operator_value_eq_requires_scalar(tmp_path: Path) -> None:
    make_triggers(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"field": "action", "operator": "eq", "value": ["opened"]}],
    )

    errors = check_trigger_operator_value(tmp_path / "plugins")

    assert len(errors) == 1
    assert "eq" in errors[0]
    assert "scalar" in errors[0]


def test_trigger_operator_value_eq_with_scalar_passes(tmp_path: Path) -> None:
    make_triggers(
        tmp_path,
        "my-plugin",
        "my-wf",
        [{"field": "action", "operator": "eq", "value": "opened"}],
    )

    errors = check_trigger_operator_value(tmp_path / "plugins")

    assert errors == []


# --- check_marketplace_manifest_versions ---

def test_marketplace_manifest_version_mismatch_detected(tmp_path: Path) -> None:
    make_manifest(tmp_path, "plugins/my-plugin", "0.4.0")
    marketplace_path = make_marketplace(
        tmp_path, [{"name": "my-plugin", "source": "./plugins/my-plugin", "version": "0.3.0"}]
    )

    errors = check_marketplace_manifest_versions(marketplace_path, tmp_path)

    assert len(errors) == 1
    assert "0.3.0" in errors[0]
    assert "0.4.0" in errors[0]


def test_marketplace_manifest_version_match_passes(tmp_path: Path) -> None:
    make_manifest(tmp_path, "plugins/my-plugin", "0.3.0")
    marketplace_path = make_marketplace(
        tmp_path, [{"name": "my-plugin", "source": "./plugins/my-plugin", "version": "0.3.0"}]
    )

    errors = check_marketplace_manifest_versions(marketplace_path, tmp_path)

    assert errors == []
