"""
Xtreme1 configuration for a Solana validator smart-node wallet cluster.

Security:
- No private keys in source control.
- Public keys only.
- Runtime validation fails fast on policy drift.

Release coincidence policy:
- CONFIG_VERSION must align with GLOBAL_RELEASE_TAG/GLOBAL_RELEASE_VERSION.
- Optional runtime GIT_TAG check enforces deployment/version integrity.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List

# -----------------------------
# Global release/compliance policy
# -----------------------------
CONFIG_VERSION = "v1.0.0"
GLOBAL_RELEASE_TAG = "release-v1.0.0"
GLOBAL_RELEASE_VERSION = "1.0.0"

RELEASE_COINCIDENCE_REQUIRED = True
GIT_TAG_COINCIDENCE_REQUIRED = True

# Required cluster size
CLUSTER_SIZE = 70

# Compliance
COMPLIANCE_TAG_PREFIX = "SOL-CMP"
COMPLIANCE_TAG_FORMAT = re.compile(r"^SOL-CMP-[A-Z0-9]{8}$")

# Versioning and release validation patterns
CONFIG_VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+$")
RELEASE_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# Solana defaults
SOLANA_CLUSTER = "mainnet-beta"
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
SOLANA_WS_URL = os.getenv("SOLANA_WS_URL", "wss://api.mainnet-beta.solana.com")

@dataclass(frozen=True)
class NodeWalletConfig:
    node_id: int
    wallet_label: str
    vote_account_pubkey: str
    identity_pubkey: str
    withdraw_authority_pubkey: str
    release_tag: str
    release_version: str
    compliance_tag: str
    enabled: bool = True


_BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def _looks_like_base58_pubkey(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if not (32 <= len(value) <= 44):
        return False
    return all(ch in _BASE58 for ch in value)

def _generate_placeholder_pubkey(seed: int) -> str:
    """Deterministic placeholder ONLY (not cryptographic, not real identity)."""
    out = []
    n = seed * 7919
    for i in range(44):
        n = (n * 1103515245 + 12345 + i) & 0x7FFFFFFF
        out.append(_BASE58[n % len(_BASE58)])
    return "".join(out)

def _generate_compliance_tag(node_id: int) -> str:
    return f"{COMPLIANCE_TAG_PREFIX}-{node_id:08X}"

def _build_default_nodes() -> List[NodeWalletConfig]:
    nodes: List[NodeWalletConfig] = []
    for i in range(1, CLUSTER_SIZE + 1):
        nodes.append(
            NodeWalletConfig(
                node_id=i,
                wallet_label=f"asi-smart-node-{i:02d}",
                vote_account_pubkey=_generate_placeholder_pubkey(i),
                identity_pubkey=_generate_placeholder_pubkey(i + 1000),
                withdraw_authority_pubkey=_generate_placeholder_pubkey(i + 2000),
                release_tag=GLOBAL_RELEASE_TAG,
                release_version=GLOBAL_RELEASE_VERSION,
                compliance_tag=_generate_compliance_tag(i),
                enabled=True,
            )
        )
    return nodes

NODE_WALLETS: List[NodeWalletConfig] = _build_default_nodes()

def _validate_release_policy() -> None:
    config_version = str(CONFIG_VERSION).strip()
    global_release_tag = str(GLOBAL_RELEASE_TAG).strip()
    global_release_version = str(GLOBAL_RELEASE_VERSION).strip()

    if not config_version:
        raise ValueError("CONFIG_VERSION must be a non-empty string")
    if not CONFIG_VERSION_PATTERN.match(config_version):
        raise ValueError(
            f"CONFIG_VERSION must match {CONFIG_VERSION_PATTERN.pattern!r}, got {config_version!r}"
        )

    if not global_release_tag:
        raise ValueError("GLOBAL_RELEASE_TAG must be a non-empty string")
    if not global_release_version:
        raise ValueError("GLOBAL_RELEASE_VERSION must be a non-empty string")

    expected_tag = f"release-{config_version}"
    if global_release_tag != expected_tag:
        raise ValueError(
            f"GLOBAL_RELEASE_TAG mismatch: expected {expected_tag}, got {global_release_tag}"
        )

    expected_release_version = config_version[1:] if config_version.startswith("v") else config_version
    if not RELEASE_VERSION_PATTERN.match(expected_release_version):
        raise ValueError(
            f"Computed release version must match {RELEASE_VERSION_PATTERN.pattern!r}, got {expected_release_version!r}"
        )
    if global_release_version != expected_release_version:
        raise ValueError(
            f"GLOBAL_RELEASE_VERSION mismatch: expected {expected_release_version}, got {global_release_version}"
        )

def _require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {value!r}")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must be a non-empty string")
    return cleaned


def _validate_release_policy() -> None:
    config_version = _require_string(CONFIG_VERSION, "CONFIG_VERSION")
    global_release_tag = _require_string(GLOBAL_RELEASE_TAG, "GLOBAL_RELEASE_TAG")
    global_release_version = _require_string(GLOBAL_RELEASE_VERSION, "GLOBAL_RELEASE_VERSION")
    compliance_prefix = _require_string(COMPLIANCE_TAG_PREFIX, "COMPLIANCE_TAG_PREFIX")

    if not isinstance(RELEASE_COINCIDENCE_REQUIRED, bool):
        raise ValueError(f"RELEASE_COINCIDENCE_REQUIRED must be a boolean, got {RELEASE_COINCIDENCE_REQUIRED!r}")
    if not isinstance(GIT_TAG_COINCIDENCE_REQUIRED, bool):
        raise ValueError(f"GIT_TAG_COINCIDENCE_REQUIRED must be a boolean, got {GIT_TAG_COINCIDENCE_REQUIRED!r}")

    if not CONFIG_VERSION_PATTERN.match(config_version):
        raise ValueError(
            f"CONFIG_VERSION must match {CONFIG_VERSION_PATTERN.pattern!r}, got {config_version!r}"
        )

    expected_tag = f"release-{config_version}"
    if global_release_tag != expected_tag:
        raise ValueError(
            f"GLOBAL_RELEASE_TAG mismatch: expected {expected_tag}, got {global_release_tag}"
        )

    expected_release_version = config_version[1:] if config_version.startswith("v") else config_version
    if not RELEASE_VERSION_PATTERN.match(expected_release_version):
        raise ValueError(
            f"Computed release version must match {RELEASE_VERSION_PATTERN.pattern!r}, got {expected_release_version!r}"
        )
    if global_release_version != expected_release_version:
        raise ValueError(
            f"GLOBAL_RELEASE_VERSION mismatch: expected {expected_release_version}, got {global_release_version}"
        )

    sample_tag = f"{compliance_prefix}-00000000"
    if not COMPLIANCE_TAG_FORMAT.fullmatch(sample_tag):
        raise ValueError(
            f"COMPLIANCE_TAG_FORMAT does not match COMPLIANCE_TAG_PREFIX {compliance_prefix!r}"
        )


def get_release_summary() -> Dict[str, object]:
    return {
        "config_version": str(CONFIG_VERSION).strip(),
        "global_release_tag": str(GLOBAL_RELEASE_TAG).strip(),
        "global_release_version": str(GLOBAL_RELEASE_VERSION).strip(),
        "cluster_size": CLUSTER_SIZE,
        "compliance_tag_prefix": COMPLIANCE_TAG_PREFIX,
    }


def validate_config() -> None:
    _validate_release_policy()

    if not isinstance(CLUSTER_SIZE, int) or CLUSTER_SIZE <= 0:
        raise ValueError(f"CLUSTER_SIZE must be a positive integer, got {CLUSTER_SIZE!r}")

    if not isinstance(NODE_WALLETS, list):
        raise ValueError(f"NODE_WALLETS must be a list, got {type(NODE_WALLETS)!r}")
    if len(NODE_WALLETS) != CLUSTER_SIZE:
        raise ValueError(f"Cluster size mismatch: expected {CLUSTER_SIZE}, got {len(NODE_WALLETS)}")

    seen_ids = set()
    seen_labels = set()
    for node in NODE_WALLETS:
        if not isinstance(node, NodeWalletConfig):
            raise ValueError(f"Node entry must be a NodeWalletConfig, got {type(node)!r}")
        if not isinstance(node.node_id, int) or node.node_id <= 0:
            raise ValueError(f"Node has invalid node_id: {node.node_id!r}")
        if node.node_id in seen_ids:
            raise ValueError(f"Duplicate node_id detected: {node.node_id}")
        if not isinstance(node.wallet_label, str) or not node.wallet_label.strip():
            raise ValueError(f"Node {node.node_id} invalid wallet_label: {node.wallet_label!r}")
        if node.wallet_label in seen_labels:
            raise ValueError(f"Duplicate wallet_label detected: {node.wallet_label}")
        if node.wallet_label != f"asi-smart-node-{node.node_id:02d}":
            raise ValueError(f"Node {node.node_id} invalid wallet_label: {node.wallet_label}")
        if not isinstance(node.enabled, bool):
            raise ValueError(f"Node {node.node_id} invalid enabled flag: {node.enabled!r}")
        seen_ids.add(node.node_id)
        seen_labels.add(node.wallet_label)

        for field_name, key in (
            ("vote_account_pubkey", node.vote_account_pubkey),
            ("identity_pubkey", node.identity_pubkey),
            ("withdraw_authority_pubkey", node.withdraw_authority_pubkey),
        ):
            if not _looks_like_base58_pubkey(key):
                raise ValueError(f"Node {node.node_id} invalid {field_name}: {key!r}")

        if not isinstance(node.compliance_tag, str) or not node.compliance_tag.strip():
            raise ValueError(f"Node {node.node_id} invalid compliance_tag: {node.compliance_tag!r}")
        if not COMPLIANCE_TAG_FORMAT.match(node.compliance_tag):
            raise ValueError(f"Node {node.node_id} invalid compliance_tag: {node.compliance_tag}")

        if RELEASE_COINCIDENCE_REQUIRED:
            if not isinstance(node.release_tag, str) or not node.release_tag.strip():
                raise ValueError(f"Node {node.node_id} invalid release_tag: {node.release_tag!r}")
            if not isinstance(node.release_version, str) or not node.release_version.strip():
                raise ValueError(f"Node {node.node_id} invalid release_version: {node.release_version!r}")
            if node.release_tag != GLOBAL_RELEASE_TAG:
                raise ValueError(f"Node {node.node_id} release_tag mismatch")
            if node.release_version != GLOBAL_RELEASE_VERSION:
                raise ValueError(f"Node {node.node_id} release_version mismatch")

    if GIT_TAG_COINCIDENCE_REQUIRED:
        runtime_tag = os.getenv("GIT_TAG", "").strip()
        if runtime_tag and runtime_tag != CONFIG_VERSION:
            raise ValueError(f"CONFIG_VERSION ({CONFIG_VERSION}) != GIT_TAG ({runtime_tag})")


if __name__ == "__main__":
    validate_config()
    print("Configuration validation passed")