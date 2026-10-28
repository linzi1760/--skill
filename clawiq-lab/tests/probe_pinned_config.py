"""Read-only official CLI schema probe; never launches agent/model execution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clawiq.runner import minimal_config
CANDIDATE = minimal_config()
with tempfile.TemporaryDirectory(prefix="clawiq-config-probe-") as tmp:
    root = Path(tmp)
    config = root / "openclaw.json"
    config.write_text(json.dumps(CANDIDATE), encoding="utf-8")
    config.chmod(0o600)
    guard = root / "no-network.cjs"
    guard.write_text('''const fail = () => { throw new Error("CLAWIQ_PROBE_NETWORK_BLOCKED"); };
require("node:net").Socket.prototype.connect = fail;
require("node:tls").connect = fail;
require("node:dgram").Socket.prototype.send = fail;
require("node:dgram").Socket.prototype.connect = fail;
globalThis.fetch = fail;
''')
    env = {"PATH": os.environ["PATH"], "HOME": tmp, "USERPROFILE": tmp,
           "XDG_CONFIG_HOME": tmp, "OPENCLAW_STATE_DIR": str(root / "state"),
           "OPENCLAW_CONFIG_PATH": str(config), "OPENCLAW_CONFIG_READONLY": "1",
           "NODE_OPTIONS": "--require=" + str(guard)}
    before = config.read_bytes()
    for args in (["agent", "exec", "--help"], ["config", "validate", "--json"]):
        result = subprocess.run(["openclaw", *args], env=env, cwd=tmp,
                                capture_output=True, text=True, timeout=45)
        print("COMMAND", " ".join(args), "EXIT", result.returncode)
        print(result.stdout)
        print(result.stderr)
        assert result.returncode == 0, "Official CLI probe failed"
        if args[-1] == "--help":
            assert "--config <path>" in result.stdout
        else:
            assert json.loads(result.stdout)["valid"] is True
    assert config.read_bytes() == before, "Read-only probe changed config"
    print("PASS: candidate schema and --config flag; NOT model/tool-enforcement E2E")
