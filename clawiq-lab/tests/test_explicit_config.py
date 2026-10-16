"""Offline safety and process contracts for the explicit-model configuration."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from clawiq.runner import (check_openclaw_cli, invoke_configured_openclaw,
                           minimal_config, validate_model_options, RunnerUnavailable)
from test_live_contract import FAKE

HELP = '--message-file --cwd --json --code-mode --timeout --config <path> --model <provider/model>'

class ExplicitConfigTests(unittest.TestCase):
    @patch('clawiq.runner.shutil.which', return_value='/usr/bin/openclaw')
    @patch('clawiq.runner.subprocess.run')
    def test_config_only_requires_explicit_model(self, run, _):
        run.return_value = Mock(returncode=0, stdout=HELP, stderr='')
        with self.assertRaisesRegex(RunnerUnavailable, 'explicit --model'):
            check_openclaw_cli()
        self.assertEqual(check_openclaw_cli(model='openai/test'), 'config')

    def test_env_and_model_inputs_restricted(self):
        for model, env in [(None, ['OPENAI_API_KEY']), ('bad', []),
                           ('openai/test', ['NODE_OPTIONS']), ('openai/test', ['HOME']),
                           ('openai/test', ['OPENCLAW_CONFIG_PATH'])]:
            with self.assertRaises(ValueError):
                validate_model_options(model, env)

    @patch('clawiq.runner.shutil.which', return_value='/usr/bin/openclaw')
    @patch('clawiq.runner.subprocess.run')
    def test_no_ambient_state_secret_files_or_plugins(self, run, _):
        roots = []
        def fake(args, **kwargs):
            root = Path(kwargs['cwd']); roots.append(root)
            config = Path(args[args.index('--config') + 1])
            self.assertEqual(json.loads(config.read_text()), minimal_config())
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)
            self.assertNotIn('synthetic-test-key', config.read_text())
            env = kwargs['env']
            self.assertEqual(env['HOME'], str(root))
            self.assertEqual(env['OPENAI_API_KEY'], 'synthetic-test-key')
            self.assertNotIn('ANTHROPIC_API_KEY', env)
            self.assertNotIn('NODE_OPTIONS', env)
            self.assertNotIn('OPENCLAW_AUTH_TOKEN', env)
            self.assertNotIn('--auth-env-only', args)
            self.assertNotIn('--config-override', args)
            return Mock(returncode=0, stdout=json.dumps({'ok':True,'status':'ok','final':'{"answer":1}','toolSummary':{'calls':0}}))
        run.side_effect = fake
        with patch.dict(os.environ, {'OPENAI_API_KEY':'synthetic-test-key', 'ANTHROPIC_API_KEY':'unselected',
                                     'NODE_OPTIONS':'not-forwarded', 'OPENCLAW_AUTH_TOKEN':'not-forwarded'}):
            invoke_configured_openclaw('synthetic prompt', model='openai/test', provider_env=['OPENAI_API_KEY'])
        self.assertTrue(all(not root.exists() for root in roots))

    @patch('clawiq.runner.shutil.which', return_value='/usr/bin/openclaw')
    @patch('clawiq.runner.subprocess.run')
    def test_unknown_tool_evidence_fails_closed(self, run, _):
        for summary in (None, {}, {'calls':1}, {'calls':False}):
            run.return_value=Mock(returncode=0, stdout=json.dumps({'ok':True,'status':'ok','final':'{"answer":1}','toolSummary':summary}))
            with self.assertRaises(RunnerUnavailable):
                invoke_configured_openclaw('synthetic', model='openai/test', provider_env=[])

    @unittest.skipIf(os.name == 'nt', 'POSIX fake executable')
    def test_config_only_full_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); command=root/'openclaw'
            fake=FAKE.replace('--config-override --timeout', '--config <path> --model <provider/model> --timeout')
            fake=fake.replace('config=json.loads(val("--config-override"))', 'config=json.loads(Path(val("--config")).read_text())\nassert config["plugins"]["enabled"] is False\nassert os.environ["HOME"] == val("--cwd")')
            command.write_text(fake); command.chmod(0o755)
            env=dict(os.environ, PATH=tmp+os.pathsep+os.environ.get('PATH',''))
            out=root/'result'
            result=subprocess.run([sys.executable,'-m','clawiq','run','--model','openai/test',
                                   '--out',str(out),'--ack-provider-calls'],env=env,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads((out/'report.json').read_text())
            self.assertEqual(report['sample_size'],12)
            self.assertEqual(report['mode'],'openclaw-exec-config')
            verified=subprocess.run([sys.executable,'-m','clawiq','verify',str(out)],capture_output=True,text=True)
            self.assertEqual(verified.returncode,0,verified.stderr)
