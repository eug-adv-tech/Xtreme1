#!/usr/bin/env python3
"""Validate release policy and cluster configuration before a release."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import config


def _escape_github_output_value(value: object) -> str:
    return str(value).replace("\r", "%0D").replace("\n", "%0A")


def _resolve_github_output_path() -> Path | None:
    github_output = os.getenv("GITHUB_OUTPUT")
    if not github_output:
        return None

    raw_path = github_output.strip()
    if not raw_path:
        raise ValueError("GITHUB_OUTPUT must be a non-empty string")

    output_path = Path(raw_path)
    if not output_path.is_absolute():
        raise ValueError(f"GITHUB_OUTPUT must be an absolute path, got {github_output!r}")
    if any(part == ".." for part in output_path.parts):
        raise ValueError(f"GITHUB_OUTPUT path must not contain parent directory traversal, got {github_output!r}")

    try:
        resolved_path = output_path.resolve(strict=False)
    except OSError as exc:  # pragma: no cover - defensive path handling
        raise ValueError(f"GITHUB_OUTPUT path is invalid: {github_output!r}") from exc

    if resolved_path == resolved_path.parent:
        raise ValueError(f"GITHUB_OUTPUT path must refer to a file, got {github_output!r}")
    if resolved_path.exists() and resolved_path.is_dir():
        raise ValueError(f"GITHUB_OUTPUT path must refer to a file, got {github_output!r}")
    if resolved_path.exists() and resolved_path.is_symlink():
        raise ValueError(f"GITHUB_OUTPUT path must not be a symbolic link, got {github_output!r}")

    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def _write_github_output(summary: dict[str, object]) -> None:
    output_path = _resolve_github_output_path()
    if output_path is None:
        return

    with output_path.open("a", encoding="utf-8") as handle:
        for key, value in summary.items():
            handle.write(f"{key}={value}\n")
            handle.write(f"{key}={_escape_github_output_value(value)}\n")
    print("Successfully wrote release parameters to GITHUB_OUTPUT.")


def main() -> int:
    try:
        config.validate_config()
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Release guard failed: {exc}", file=sys.stderr)
        return 1

    summary = config.get_release_summary()

    config_version = str(summary.get("config_version", "")).strip()
    global_release_tag = str(summary.get("global_release_tag", "")).strip()
    global_release_version = str(summary.get("global_release_version", "")).strip()

    if not config_version:
        print("Error: CONFIG_VERSION is not defined or empty in config.py", file=sys.stderr)
        return 1

    if not global_release_tag:
        print("Error: GLOBAL_RELEASE_TAG is not defined or empty in config.py", file=sys.stderr)
        return 1

    if not global_release_version:
        print("Error: GLOBAL_RELEASE_VERSION is not defined or empty in config.py", file=sys.stderr)
        return 1

    print(f"Release guard passed for {config_version}")
    print(f"CONFIG_VERSION: {config_version}")
    print(f"GLOBAL_RELEASE_TAG: {global_release_tag}")
    print(f"GLOBAL_RELEASE_VERSION: {global_release_version}")
    print(f"CLUSTER_SIZE: {summary.get('cluster_size')}")

    try:
        _write_github_output(summary)
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Error: Failed to write to GITHUB_OUTPUT: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

