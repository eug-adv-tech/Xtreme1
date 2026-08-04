import importlib
import os
import subprocess
import sys
import tempfile
import unittest
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
        self.assertEqual(summary["config_version"], "v1.0.0")
        self.assertEqual(summary["global_release_tag"], "release-v1.0.0")
        self.assertEqual(summary["global_release_version"], "1.0.0")
        self.assertEqual(summary["cluster_size"], 70)

    def test_validate_config_rejects_release_tag_mismatch(self) -> None:
        original_tag = config.GLOBAL_RELEASE_TAG
        try:
            config.GLOBAL_RELEASE_TAG = "release-v0.9.0"
            with self.assertRaises(ValueError):
                config.validate_config()
        finally:
            config.GLOBAL_RELEASE_TAG = original_tag

    def test_validate_config_rejects_mismatched_git_tag(self) -> None:
        os.environ["GIT_TAG"] = "v1.0.1"
        with self.assertRaises(ValueError):
            config.validate_config()

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
            self.assertIn("Release guard passed for v1.0.0", completed.stdout)
            self.assertTrue(output_path.exists())
            contents = output_path.read_text(encoding="utf-8")
            self.assertIn("config_version=v1.0.0", contents)
            self.assertIn("global_release_tag=release-v1.0.0", contents)
            self.assertIn("global_release_version=1.0.0", contents)
            self.assertIn("cluster_size=70", contents)


if __name__ == "__main__":
    unittest.main()
