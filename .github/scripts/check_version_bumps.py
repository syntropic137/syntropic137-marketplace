#!/usr/bin/env python3
"""Check that every plugin with changed files has a version bump.

Usage:
    python check_version_bumps.py --base origin/main
    python check_version_bumps.py --base origin/main --plugins-dir plugins

Exit codes:
    0: all changed plugins have version bumps (or no plugins changed)
    1: one or more plugins are missing a version bump
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_changed_plugins(base_ref: str, plugins_dir: Path) -> list[str]:
    """Return plugin names that have changed files relative to base_ref."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    changed: set[str] = set()
    for line in result.stdout.splitlines():
        path = Path(line)
        # Match plugins/<name>/...
        if len(path.parts) >= 2 and path.parts[0] == str(plugins_dir.name):
            changed.add(path.parts[1])
    return sorted(changed)


def get_version(manifest_path: Path) -> str:
    """Read the version field from a plugin manifest."""
    return json.loads(manifest_path.read_text())["version"]


def get_base_version(manifest_path: Path, base_ref: str) -> str:
    """Get the version from the base branch, or '0.0.0' for new plugins."""
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{manifest_path}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "0.0.0"
    try:
        return json.loads(result.stdout)["version"]
    except (json.JSONDecodeError, KeyError):
        return "0.0.0"


def parse_semver(version: str) -> tuple[int, int, int] | None:
    """Parse a strict X.Y.Z semver string, or None if it doesn't match."""
    parts = version.split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def check_version_bumps(base_ref: str, plugins_dir: Path) -> list[str]:
    """Return a list of error messages for plugins missing a version bump."""
    errors: list[str] = []

    changed_plugins = get_changed_plugins(base_ref, plugins_dir)
    if not changed_plugins:
        print("No plugin files changed — skipping version check")
        return errors

    for plugin in changed_plugins:
        manifest = plugins_dir / plugin / "syntropic137-plugin.json"
        if not manifest.exists():
            print(f"  {plugin}: no manifest found, skipping")
            continue

        current = get_version(manifest)
        base = get_base_version(manifest, base_ref)

        current_tuple = parse_semver(current)
        base_tuple = parse_semver(base)

        if current_tuple is None:
            errors.append(
                f"Plugin '{plugin}' has an invalid version '{current}' in {manifest} "
                "(expected semver X.Y.Z)"
            )
        elif base_tuple is None:
            errors.append(
                f"Plugin '{plugin}' has an invalid base version '{base}' (expected semver X.Y.Z)"
            )
        elif current_tuple == base_tuple:
            errors.append(
                f"Plugin '{plugin}' changed but version is still {current} — "
                f"bump the version in {manifest}"
            )
        elif current_tuple < base_tuple:
            errors.append(
                f"Plugin '{plugin}' version decreased from {base} to {current} in {manifest} — "
                "bumps must increase the version"
            )
        else:
            print(f"  {plugin}: {base} → {current} ✓")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="Base ref to diff against")
    parser.add_argument("--plugins-dir", default="plugins", help="Plugins directory")
    args = parser.parse_args()

    plugins_dir = Path(args.plugins_dir)
    if not plugins_dir.is_dir():
        print(f"Error: plugins directory '{plugins_dir}' not found", file=sys.stderr)
        return 1

    errors = check_version_bumps(base_ref=args.base, plugins_dir=plugins_dir)

    if errors:
        print()
        for error in errors:
            print(f"::error::{error}")
        print(f"\n{len(errors)} plugin(s) need a version bump before merge")
        return 1

    print("All changed plugins have version bumps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
