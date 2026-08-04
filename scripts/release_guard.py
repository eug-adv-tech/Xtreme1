#!/usr/bin/env python3
"""Validate release policy and cluster configuration before a release."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import config


def main() -> int:
    try:
        config.validate_config()
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Release guard failed: {exc}", file=sys.stderr)
        return 1

    print(f"Release guard passed for {config.CONFIG_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
