"""Tests for check_version_bumps.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from check_version_bumps import check_version_bumps, get_changed_plugins, get_version


# --- helpers ---

def make_manifest(tmp_path: Path, plugin: str, version: str) -> Path:
    plugin_dir = tmp_path / "plugins" / plugin
    plugin_dir.mkdir(parents=True)
    manifest = plugin_dir / "syntropic137-plugin.json"
    manifest.write_text(json.dumps({"name": plugin, "version": version}))
    return manifest


# --- get_version ---

def test_get_version(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path, "my-plugin", "1.2.3")
    assert get_version(manifest) == "1.2.3"


# --- get_changed_plugins ---

def test_get_changed_plugins_filters_to_plugin_dir(tmp_path: Path) -> None:
    git_output = "plugins/code-review/workflow.yaml\nplugins/sdlc-trunk/phases/fix.md\nREADME.md\n"
    with patch("check_version_bumps.subprocess.run") as mock_run:
        mock_run.return_value.stdout = git_output
        result = get_changed_plugins("origin/main", tmp_path / "plugins")
    assert result == ["code-review", "sdlc-trunk"]


def test_get_changed_plugins_deduplicates(tmp_path: Path) -> None:
    git_output = "plugins/code-review/a.md\nplugins/code-review/b.md\n"
    with patch("check_version_bumps.subprocess.run") as mock_run:
        mock_run.return_value.stdout = git_output
        result = get_changed_plugins("origin/main", tmp_path / "plugins")
    assert result == ["code-review"]


def test_get_changed_plugins_ignores_non_plugin_files(tmp_path: Path) -> None:
    git_output = "CLAUDE.md\n.github/workflows/validate.yml\nmarketplace.json\n"
    with patch("check_version_bumps.subprocess.run") as mock_run:
        mock_run.return_value.stdout = git_output
        result = get_changed_plugins("origin/main", tmp_path / "plugins")
    assert result == []


# --- check_version_bumps ---

def test_passes_when_version_bumped(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    make_manifest(tmp_path, "my-plugin", "0.2.0")

    git_diff_output = "plugins/my-plugin/workflow.yaml\n"
    base_manifest_json = json.dumps({"name": "my-plugin", "version": "0.1.0"})

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
            returncode = 0
        r = Result()
        if "diff" in cmd:
            r.stdout = git_diff_output
        elif "show" in cmd:
            r.stdout = base_manifest_json
        return r

    with patch("check_version_bumps.subprocess.run", side_effect=fake_run):
        errors = check_version_bumps("origin/main", plugins_dir)

    assert errors == []


def test_fails_when_version_not_bumped(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    make_manifest(tmp_path, "my-plugin", "0.1.0")

    git_diff_output = "plugins/my-plugin/workflow.yaml\n"
    base_manifest_json = json.dumps({"name": "my-plugin", "version": "0.1.0"})

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
            returncode = 0
        r = Result()
        if "diff" in cmd:
            r.stdout = git_diff_output
        elif "show" in cmd:
            r.stdout = base_manifest_json
        return r

    with patch("check_version_bumps.subprocess.run", side_effect=fake_run):
        errors = check_version_bumps("origin/main", plugins_dir)

    assert len(errors) == 1
    assert "my-plugin" in errors[0]
    assert "0.1.0" in errors[0]


def test_fails_when_version_decreased(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    make_manifest(tmp_path, "my-plugin", "0.2.0")

    git_diff_output = "plugins/my-plugin/workflow.yaml\n"
    base_manifest_json = json.dumps({"name": "my-plugin", "version": "0.3.0"})

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
            returncode = 0
        r = Result()
        if "diff" in cmd:
            r.stdout = git_diff_output
        elif "show" in cmd:
            r.stdout = base_manifest_json
        return r

    with patch("check_version_bumps.subprocess.run", side_effect=fake_run):
        errors = check_version_bumps("origin/main", plugins_dir)

    assert len(errors) == 1
    assert "my-plugin" in errors[0]
    assert "0.3.0" in errors[0]
    assert "0.2.0" in errors[0]


def test_fails_when_version_malformed(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    make_manifest(tmp_path, "my-plugin", "not-a-version")

    git_diff_output = "plugins/my-plugin/workflow.yaml\n"
    base_manifest_json = json.dumps({"name": "my-plugin", "version": "0.1.0"})

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
            returncode = 0
        r = Result()
        if "diff" in cmd:
            r.stdout = git_diff_output
        elif "show" in cmd:
            r.stdout = base_manifest_json
        return r

    with patch("check_version_bumps.subprocess.run", side_effect=fake_run):
        errors = check_version_bumps("origin/main", plugins_dir)

    assert len(errors) == 1
    assert "my-plugin" in errors[0]
    assert "not-a-version" in errors[0]


def test_passes_for_new_plugin_with_any_version(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    make_manifest(tmp_path, "new-plugin", "0.1.0")

    git_diff_output = "plugins/new-plugin/workflow.yaml\n"

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
            returncode = 0 if "diff" in cmd else 1  # git show fails = new plugin
        r = Result()
        if "diff" in cmd:
            r.stdout = git_diff_output
        return r

    with patch("check_version_bumps.subprocess.run", side_effect=fake_run):
        errors = check_version_bumps("origin/main", plugins_dir)

    assert errors == []


def test_skips_plugin_with_no_manifest(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    # Don't create a manifest
    (tmp_path / "plugins" / "ghost-plugin").mkdir(parents=True)

    git_diff_output = "plugins/ghost-plugin/something.md\n"

    with patch("check_version_bumps.subprocess.run") as mock_run:
        mock_run.return_value.stdout = git_diff_output
        errors = check_version_bumps("origin/main", plugins_dir)

    assert errors == []


def test_no_changed_plugins_returns_no_errors(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    with patch("check_version_bumps.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "CLAUDE.md\n"
        errors = check_version_bumps("origin/main", plugins_dir)

    assert errors == []
