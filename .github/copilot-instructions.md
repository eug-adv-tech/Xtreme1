# Copilot instructions for Xtreme1

This repository contains the release configuration for a Solana validator smart-node wallet cluster. Treat `config.py` as the source of truth for release policy and node-level release metadata.

## Release safety rules

- Keep the release constants aligned in `config.py`:
  - `CONFIG_VERSION` must use the `vX.Y.Z` format.
  - `GLOBAL_RELEASE_TAG` must be `release-<CONFIG_VERSION>`.
  - `GLOBAL_RELEASE_VERSION` must be `<CONFIG_VERSION>` without the leading `v`.
  - Every node wallet must keep matching `release_tag` and `release_version` values.
  - `CLUSTER_SIZE` must remain `70`.
- Before changing release-related files, run `python scripts/release_guard.py`.
- If you edit `config.py`, `scripts/release_guard.py`, `.github/workflows/release.yml`, or `docs/release-process.md`, verify that the release guard still passes.

## Security expectations

- Do not add private keys, secrets, or credentials to source control.
- Keep public keys only in configuration and sample data.
- Preserve the existing deterministic placeholder behavior for generated wallet metadata.

## Change management

- Keep changes small and targeted; avoid unrelated refactors when adjusting release behavior.
- Preserve compatibility for both manual workflow runs and pushes to `main`.
- Update the release documentation when behavior changes in the workflow or policy.
