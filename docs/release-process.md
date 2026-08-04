# Release Process (Xtreme1)

This repository uses an automated release workflow based on `config.py`.

## Triggers

- Automatic: push to `main` when `config.py` (or release workflow/guard) changes.
- Manual: Actions → **Release from config** → **Run workflow**.

## Required coincidence rules

In `config.py`:

- `CONFIG_VERSION` must be set (example: `v1.0.0`)
- `GLOBAL_RELEASE_TAG` must equal `release-{CONFIG_VERSION}`
- `GLOBAL_RELEASE_VERSION` must equal `CONFIG_VERSION` without leading `v`
- Per-node `release_tag` and `release_version` must match globals
- Cluster must validate at exactly 70 nodes

## What the workflow does

1. Runs `scripts/release_guard.py`
2. Extracts release constants from `config.py`
3. Ensures policy coincidence is correct
4. Creates and pushes an annotated git tag `CONFIG_VERSION` when it is missing
5. Creates or updates the GitHub release for that tag

## Operator checklist

- Update `CONFIG_VERSION` for each new release (e.g., `v1.0.1`)
- Update `GLOBAL_RELEASE_TAG` and `GLOBAL_RELEASE_VERSION` accordingly
- Ensure node-level release fields remain consistent
- Merge to `main` or manually run workflow

## Visibility note

Repository visibility is controlled in GitHub settings and cannot be changed by workflow files.
To make the repository private:

1. Go to **Settings** → **General**
2. Scroll to **Danger Zone**
3. Select **Change repository visibility** → **Make private**
