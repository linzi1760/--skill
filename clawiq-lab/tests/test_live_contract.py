"""True subprocess contract test with a synthetic OpenClaw CLI, no paid calls."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from clawiq.cli import main

FAKE = r'''#!/usr/bin/env python3
import sys, json, os
from pathlib import Path
args = sys.argv[1:]
if "--help" in args:
    print("--message-file --cwd --json --code-mode --config-override --timeout --agent --session-id")
    sys.exit(0)
if args[:2] != ["agent", "exec"]:
    sys.exit(3)
def val(flag):
    return args[args.index(flag) + 1]
config=json.loads(val("--config-override"))
if config["tools"]["deny"] != ["*"]:
    sys.exit(4)
if config["agents"]["defaults"]["contextInjection"] != "never":
    sys.exit(5)
if not Path(val("--message-file")).is_file():
    sys.exit(6)
calls=1 if os.environ.get("CLAWIQ_TEST_FAKE_TOOLS") else 0
print(json.dumps({"ok":True,"status":"ok","final":'{"answer":null}',"toolSummary":{"calls":calls}}))
'''


@unittest.skipIf(os.name == "nt", "POSIX fake executable")
class LiveContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        binary=self.root/"bin"
        binary.mkdir()
        command=binary/"openclaw"
        command.write_text(FAKE, encoding="utf-8")
        command.chmod(0o755)
        self.test_path=str(binary)+os.pathsep+os.environ.get("PATH","")

    def test_preflight_and_12_question_process_pipeline(self):
        with patch.dict(os.environ, {"PATH":self.test_path}):
            self.assertEqual(main(["doctor"]),0)
            folder=self.root/"live"
            self.assertEqual(main(["run","--out",str(folder),"--ack-provider-calls"]),0)
            self.assertEqual(main(["verify",str(folder)]),0)
            report=json.loads((folder/"report.json").read_text(encoding="utf-8"))
            self.assertFalse(report["demo"])
            self.assertEqual(report["mode"],"openclaw-exec")
            self.assertEqual(report["sample_size"],12)

    def test_nonzero_tool_calls_do_not_produce_a_report(self):
        with patch.dict(os.environ, {"PATH":self.test_path,"CLAWIQ_TEST_FAKE_TOOLS":"1"}):
            folder=self.root/"not-valid"
            self.assertEqual(main(["run","--out",str(folder),"--ack-provider-calls"]),2)
            self.assertFalse((folder/"report.json").exists())
            self.assertTrue((folder/"responses.checkpoint.private.json").exists())

    def test_missing_cli_keeps_output_dir_absent(self):
        with patch("clawiq.runner.shutil.which",return_value=None):
            folder=self.root/"missing"
            self.assertEqual(main(["run","--out",str(folder),"--ack-provider-calls"]),1)
            self.assertFalse(folder.exists())
