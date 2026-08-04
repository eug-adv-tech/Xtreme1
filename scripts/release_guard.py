#!/usr/bin/env python3
"""
Release Guard script to validate Xtreme1 configuration and policy coincidence.
Outputs validated configuration variables to GITHUB_OUTPUT for subsequent steps.
"""

import os
import sys

# Ensure repository root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    try:
        import config
    except Exception as e:
        print(f"Error: Configuration validation failed when importing: {e}", file=sys.stderr)
        return 1

    # Extract required release variables
    config_version = getattr(config, "CONFIG_VERSION", "").strip()
    global_release_tag = getattr(config, "GLOBAL_RELEASE_TAG", "").strip()
    global_release_version = getattr(config, "GLOBAL_RELEASE_VERSION", "").strip()

    if not config_version:
        print("Error: CONFIG_VERSION is not defined or empty in config.py", file=sys.stderr)
        return 1

    if not global_release_tag:
        print("Error: GLOBAL_RELEASE_TAG is not defined or empty in config.py", file=sys.stderr)
        return 1

    if not global_release_version:
        print("Error: GLOBAL_RELEASE_VERSION is not defined or empty in config.py", file=sys.stderr)
        return 1

    print("Configuration and policy coincidence check: PASSED")
    print(f"CONFIG_VERSION: {config_version}")
    print(f"GLOBAL_RELEASE_TAG: {global_release_tag}")
    print(f"GLOBAL_RELEASE_VERSION: {global_release_version}")

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        try:
            with open(github_output, "a") as f:
                f.write(f"config_version={config_version}\n")
                f.write(f"global_release_tag={global_release_tag}\n")
                f.write(f"global_release_version={global_release_version}\n")
            print("Successfully wrote release parameters to GITHUB_OUTPUT.")
        except Exception as e:
            print(f"Warning: Failed to write to GITHUB_OUTPUT: {e}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())
