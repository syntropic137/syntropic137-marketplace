#!/usr/bin/env python3
"""Fetch platform JSON Schemas from exactly one resolved ref, no per-file fallback.

Replaces the inline bash/curl loop that could silently mix schemas fetched
from different refs (some from the pinned tag, some from `main`) while
reporting only the pinned tag. A failed fetch is a hard, named failure: it
never substitutes a different ref for a subset of files.

Usage:
    python fetch_schemas.py --version v0.25.2 --out-dir .schemas

Exit codes:
    0: all five schemas fetched from the requested ref
    1: one or more schemas failed to fetch
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path
from typing import Callable

SCHEMA_FILES = [
    "marketplace.schema.json",
    "plugin-manifest.schema.json",
    "workflow.schema.json",
    "triggers.schema.json",
    "phase-frontmatter.schema.json",
]

SCHEMA_BASE_TEMPLATE = "https://raw.githubusercontent.com/syntropic137/syntropic137/{version}/schemas/plugin/{schema}"

Fetcher = Callable[[str, str], bytes]


def default_fetcher(url: str, schema: str) -> bytes:
    with urllib.request.urlopen(url) as response:  # noqa: S310 - fixed, trusted host
        return response.read()


def fetch_schemas(version: str, out_dir: Path, fetcher: Fetcher = default_fetcher) -> list[str]:
    """Fetch all schema files from `version` into `out_dir`.

    Returns a list of error messages, one per failed file. On any failure,
    no files are written to `out_dir` from this run — either all five land
    or none do, so `out_dir` never ends up a mix of refs.
    """
    errors: list[str] = []
    fetched: dict[str, bytes] = {}

    for schema in SCHEMA_FILES:
        url = SCHEMA_BASE_TEMPLATE.format(version=version, schema=schema)
        try:
            fetched[schema] = fetcher(url, schema)
        except Exception as exc:
            errors.append(f"Failed to fetch '{schema}' at ref '{version}': {exc}")

    if errors:
        return errors

    out_dir.mkdir(parents=True, exist_ok=True)
    for schema, content in fetched.items():
        (out_dir / schema).write_bytes(content)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Git tag to fetch schemas from, e.g. v0.25.2")
    parser.add_argument("--out-dir", required=True, help="Directory to write fetched schemas to")
    args = parser.parse_args()

    print(f"Fetching schemas from ref '{args.version}'")
    errors = fetch_schemas(args.version, Path(args.out_dir))

    if errors:
        for error in errors:
            print(f"::error::{error}")
        return 1

    print(f"Fetched all 5 schemas from ref '{args.version}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
