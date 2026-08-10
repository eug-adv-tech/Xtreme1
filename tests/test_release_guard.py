import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import config


class ReleaseGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_git_tag = os.environ.get("GIT_TAG")
        self._original_github_output = os.environ.get("GITHUB_OUTPUT")

    def tearDown(self) -> None:
        if self._original_git_tag is None:
            os.environ.pop("GIT_TAG", None)
        else:
            os.environ["GIT_TAG"] = self._original_git_tag

        if self._original_github_output is None:
            os.environ.pop("GITHUB_OUTPUT", None)
        else:
            os.environ["GITHUB_OUTPUT"] = self._original_github_output

        importlib.reload(config)

    def test_default_configuration_is_valid(self) -> None:
        config.validate_config()
        summary = config.get_release_summary()
        self.assertEqual(summary["config_version"], config.CONFIG_VERSION)
        self.assertEqual(summary["global_release_tag"], config.GLOBAL_RELEASE_TAG)
        self.assertEqual(summary["global_release_version"], config.GLOBAL_RELEASE_VERSION)
        self.assertEqual(summary["cluster_size"], config.CLUSTER_SIZE)

    def test_validate_config_rejects_release_tag_mismatch(self) -> None:
        original_tag = config.GLOBAL_RELEASE_TAG
        try:
            config.GLOBAL_RELEASE_TAG = "release-v0.9.0"
            with self.assertRaises(ValueError):
                config.validate_config()
        finally:
            config.GLOBAL_RELEASE_TAG = original_tag

    def test_validate_config_rejects_mismatched_git_tag(self) -> None:
        # Derive a tag that is guaranteed to differ from CONFIG_VERSION
        bumped = config.CONFIG_VERSION.replace("v", "v0.", 1) if not config.CONFIG_VERSION.startswith("v0.") else config.CONFIG_VERSION + ".1"
        os.environ["GIT_TAG"] = bumped
        with self.assertRaises(ValueError):
            config.validate_config()

    def test_validate_config_rejects_non_boolean_release_policy(self) -> None:
        original_value = config.RELEASE_COINCIDENCE_REQUIRED
        try:
            config.RELEASE_COINCIDENCE_REQUIRED = "yes"
            with self.assertRaises(ValueError):
                config.validate_config()
        finally:
            config.RELEASE_COINCIDENCE_REQUIRED = original_value

    def test_validate_config_rejects_invalid_compliance_tag(self) -> None:
        original_nodes = config.NODE_WALLETS
        try:
            invalid_nodes = [
                replace(node, compliance_tag="invalid-tag") if index == 0 else node
                for index, node in enumerate(original_nodes)
            ]
            config.NODE_WALLETS = invalid_nodes
            with self.assertRaises(ValueError):
                config.validate_config()
        finally:
            config.NODE_WALLETS = original_nodes

    def test_release_guard_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            output_path = Path(tempdir) / "github-output.txt"
            os.environ["GITHUB_OUTPUT"] = str(output_path)
            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "release_guard.py")],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(f"Release guard passed for {config.CONFIG_VERSION}", completed.stdout)
            self.assertTrue(output_path.exists())
            contents = output_path.read_text(encoding="utf-8")
            self.assertIn(f"config_version={config.CONFIG_VERSION}", contents)
            self.assertIn(f"global_release_tag={config.GLOBAL_RELEASE_TAG}", contents)
            self.assertIn(f"global_release_version={config.GLOBAL_RELEASE_VERSION}", contents)
            self.assertIn(f"cluster_size={config.CLUSTER_SIZE}", contents)


if __name__ == "__main__":
    unittest.main()
