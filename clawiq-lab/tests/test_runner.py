import json
import unittest
from unittest.mock import patch, Mock
from clawiq.runner import extract_openclaw_text, invoke_openclaw, RunnerUnavailable


class RunnerTests(unittest.TestCase):
    def test_exec_json(self):
        data={'ok':True,'status':'ok','final':'{"answer":42}', 'usage':{'total':150}}
        self.assertEqual(extract_openclaw_text(json.dumps(data)),'{"answer":42}')

    def test_failed_not_scored(self):
        for payload in ('bad', '{}', '{"ok":false}', '{"ok":true,"status":"error","final":"ok"}'):
            with self.assertRaises(RunnerUnavailable):
                extract_openclaw_text(payload)

    @patch('clawiq.runner.shutil.which',return_value='/usr/local/bin/openclaw')
    @patch('clawiq.runner.subprocess.run')
    def test_sandbox_flags_and_invocation(self, run, which):
        run.return_value = Mock(returncode=0,stdout=json.dumps({'ok':True,'status':'ok','final':'{"answer":5}','usage':{'total':10}}))
        result=invoke_openclaw('fake prompt')
        self.assertEqual(result['raw'],'{"answer":5}')
        self.assertEqual(result['usage']['total'],10)
        args=run.call_args.args[0]
        self.assertIn('--message-file',args)
        self.assertIn('--cwd',args)
        self.assertIn('--config-override',args)
        self.assertIn('"profile":"minimal"',args[-1])
        self.assertIn('--code-mode',args)
        self.assertNotIn('--deliver',args)

    @patch('clawiq.runner.shutil.which',return_value=None)
    def test_without_openclaw(self, _):
        with self.assertRaises(RunnerUnavailable):
            invoke_openclaw('example')

class GatewayTests(unittest.TestCase):
    @patch('clawiq.runner.shutil.which',return_value='/usr/bin/openclaw')
    @patch('clawiq.runner.subprocess.run')
    def test_gateway_payload_and_flags(self, run, which):
        run.return_value = Mock(returncode=0,stdout=json.dumps({'ok':True,'result':{'payloads':[{'text':'{"answer":7}'}]}}))
        from clawiq.runner import invoke_gateway_agent
        val=invoke_gateway_agent('prompt',agent_id='main')
        self.assertEqual(val['raw'],'{"answer":7}')
        args=run.call_args.args[0]
        self.assertIn('--session-id',args)
        self.assertIn('--agent',args)
        self.assertNotIn('--deliver',args)

    @patch('clawiq.runner.shutil.which',return_value='/usr/bin/openclaw')
    @patch('clawiq.runner.subprocess.run')
    def test_gateway_rejects_ambiguous_response(self, run, which):
        from clawiq.runner import invoke_gateway_agent
        run.return_value = Mock(returncode=0,stdout=json.dumps({'ok':False, 'status':'error'}))
        with self.assertRaises(RunnerUnavailable):
            invoke_gateway_agent('test')
