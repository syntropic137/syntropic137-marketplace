"""Tests for fetch_schemas.py."""

from __future__ import annotations

from pathlib import Path

from fetch_schemas import SCHEMA_FILES, fetch_schemas


def test_all_five_succeed_returns_ref(tmp_path: Path) -> None:
    def fake_fetcher(url: str, schema: str) -> bytes:
        return f'{{"schema": "{schema}", "url": "{url}"}}'.encode()

    out_dir = tmp_path / "schemas"
    errors = fetch_schemas("v0.25.2", out_dir, fetcher=fake_fetcher)

    assert errors == []
    for schema in SCHEMA_FILES:
        assert (out_dir / schema).exists()
        assert "v0.25.2" in (out_dir / schema).read_text()


def test_single_failure_reports_offending_file_and_does_not_retry_main(tmp_path: Path) -> None:
    urls_tried: list[str] = []

    def fake_fetcher(url: str, schema: str) -> bytes:
        urls_tried.append(url)
        if schema == "triggers.schema.json":
            raise RuntimeError("HTTP 404")
        return b"{}"

    out_dir = tmp_path / "schemas"
    errors = fetch_schemas("v0.25.2", out_dir, fetcher=fake_fetcher)

    assert len(errors) == 1
    assert "triggers.schema.json" in errors[0]
    assert "v0.25.2" in errors[0]
    assert not any("/main/" in url for url in urls_tried)


def test_no_partial_writes_on_failure(tmp_path: Path) -> None:
    def fake_fetcher(url: str, schema: str) -> bytes:
        if schema == "workflow.schema.json":
            raise RuntimeError("network error")
        return b"{}"

    out_dir = tmp_path / "schemas"
    errors = fetch_schemas("v0.25.2", out_dir, fetcher=fake_fetcher)

    assert errors
    assert not out_dir.exists() or list(out_dir.iterdir()) == []


def test_all_fetch_from_the_same_requested_ref(tmp_path: Path) -> None:
    urls_tried: list[str] = []

    def fake_fetcher(url: str, schema: str) -> bytes:
        urls_tried.append(url)
        return b"{}"

    out_dir = tmp_path / "schemas"
    fetch_schemas("v0.27.0", out_dir, fetcher=fake_fetcher)

    assert len(urls_tried) == len(SCHEMA_FILES)
    assert all("/v0.27.0/" in url for url in urls_tried)
