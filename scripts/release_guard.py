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


def _write_github_output(summary: dict[str, object]) -> None:
    github_output = os.getenv("GITHUB_OUTPUT")
    if not github_output:
        return

    output_path = Path(github_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        for key, value in summary.items():
            handle.write(f"{key}={value}\n")
    print("Successfully wrote release parameters to GITHUB_OUTPUT.")


def main() -> int:
    try:
        config.validate_config()
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Release guard failed: {exc}", file=sys.stderr)
        return 1

<<<<<<< HEAD
    config_version = str(getattr(config, "CONFIG_VERSION", "")).strip()
    global_release_tag = str(getattr(config, "GLOBAL_RELEASE_TAG", "")).strip()
    global_release_version = str(getattr(config, "GLOBAL_RELEASE_VERSION", "")).strip()
=======
    summary = config.get_release_summary()

    config_version = str(summary.get("config_version", "")).strip()
    global_release_tag = str(summary.get("global_release_tag", "")).strip()
    global_release_version = str(summary.get("global_release_version", "")).strip()
>>>>>>> origin/main

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
<<<<<<< HEAD

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        try:
            with Path(github_output).open("a", encoding="utf-8") as handle:
                handle.write(f"config_version={config_version}\n")
                handle.write(f"global_release_tag={global_release_tag}\n")
                handle.write(f"global_release_version={global_release_version}\n")
            print("Successfully wrote release parameters to GITHUB_OUTPUT.")
        except Exception as exc:  # pragma: no cover - CLI error path
            print(f"Error: Failed to write to GITHUB_OUTPUT: {exc}", file=sys.stderr)
            return 1
=======
    print(f"CLUSTER_SIZE: {summary.get('cluster_size')}")

    try:
        _write_github_output(summary)
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Warning: Failed to write to GITHUB_OUTPUT: {exc}", file=sys.stderr)
>>>>>>> origin/main

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

