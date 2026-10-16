"""Verify the documented python -m entry point, without live provider calls."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_live_contract import FAKE


class ModuleExitTests(unittest.TestCase):
    def run_cli(self, *args, env=None):
        return subprocess.run([sys.executable, "-m", "clawiq", *args],
                              capture_output=True, text=True, env=env, timeout=30)

    def test_missing_ack_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "result"
            result = self.run_cli("run", "--out", str(out))
            self.assertEqual(result.returncode, 1)
            self.assertIn("--ack-provider-calls", result.stderr)
            self.assertFalse(out.exists())

    def test_missing_cli_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, PATH=tmp)
            result = self.run_cli("doctor", env=env)
            self.assertEqual(result.returncode, 1)
            self.assertIn("not installed", result.stderr)

    def test_demo_and_verify_succeed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "demo")
            self.assertEqual(self.run_cli("demo", "--out", out).returncode, 0)
            self.assertEqual(self.run_cli("verify", out).returncode, 0)
            self.assertEqual(self.run_cli("demo", "--out", out).returncode, 1)

    @unittest.skipIf(os.name == "nt", "POSIX fake executable")
    def test_tool_violation_is_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = root / "openclaw"
            command.write_text(FAKE, encoding="utf-8")
            command.chmod(0o755)
            env = dict(os.environ, PATH=tmp + os.pathsep + os.environ.get("PATH", ""),
                       CLAWIQ_TEST_FAKE_TOOLS="1")
            out = root / "result"
            result = self.run_cli("run", "--out", str(out), "--ack-provider-calls", env=env)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((out / "report.json").exists())
            self.assertTrue((out / "responses.checkpoint.private.json").exists())
