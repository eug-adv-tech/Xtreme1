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
from typing import List

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

def _validate_release_policy():
    expected_tag = f"release-{CONFIG_VERSION}"
    if GLOBAL_RELEASE_TAG != expected_tag:
        raise ValueError(
            f"GLOBAL_RELEASE_TAG mismatch: expected {expected_tag}, got {GLOBAL_RELEASE_TAG}"
        )

    expected_release_version = CONFIG_VERSION[1:] if CONFIG_VERSION.startswith("v") else CONFIG_VERSION
    if GLOBAL_RELEASE_VERSION != expected_release_version:
        raise ValueError(
            f"GLOBAL_RELEASE_VERSION mismatch: expected {expected_release_version}, got {GLOBAL_RELEASE_VERSION}"
        )

def validate_config() -> None:
    _validate_release_policy()

    if len(NODE_WALLETS) != CLUSTER_SIZE:
        raise ValueError(f"Cluster size mismatch: expected {CLUSTER_SIZE}, got {len(NODE_WALLETS)}")

    seen_ids = set()
    seen_labels = set()
    for node in NODE_WALLETS:
        if node.node_id in seen_ids:
            raise ValueError(f"Duplicate node_id detected: {node.node_id}")
        if node.wallet_label in seen_labels:
            raise ValueError(f"Duplicate wallet_label detected: {node.wallet_label}")
        seen_ids.add(node.node_id)
        seen_labels.add(node.wallet_label)

        for field_name, key in (
            ("vote_account_pubkey", node.vote_account_pubkey),
            ("identity_pubkey", node.identity_pubkey),
            ("withdraw_authority_pubkey", node.withdraw_authority_pubkey),
        ):
            if not _looks_like_base58_pubkey(key):
                raise ValueError(f"Node {node.node_id} invalid {field_name}: {key!r}")

        if not COMPLIANCE_TAG_FORMAT.match(node.compliance_tag):
            raise ValueError(f"Node {node.node_id} invalid compliance_tag: {node.compliance_tag}")

        if RELEASE_COINCIDENCE_REQUIRED:
            if node.release_tag != GLOBAL_RELEASE_TAG:
                raise ValueError(f"Node {node.node_id} release_tag mismatch")
            if node.release_version != GLOBAL_RELEASE_VERSION:
                raise ValueError(f"Node {node.node_id} release_version mismatch")

    if GIT_TAG_COINCIDENCE_REQUIRED:
        runtime_tag = os.getenv("GIT_TAG", "").strip()
        if runtime_tag and runtime_tag != CONFIG_VERSION:
            raise ValueError(f"CONFIG_VERSION ({CONFIG_VERSION}) != GIT_TAG ({runtime_tag})")

validate_config()