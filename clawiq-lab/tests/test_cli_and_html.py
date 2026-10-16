import json
import tempfile
import unittest
from pathlib import Path
from clawiq.cli import main
from clawiq.reporting import render_html


class E2EOffline(unittest.TestCase):
    def test_demo_verify_and_render(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            out=root/'demo'
            self.assertEqual(main(['demo','--seed','19','--out',str(out)]),0)
            self.assertEqual(main(['verify',str(out)]),0)
            demo=json.loads((out/'report.json').read_text())
            self.assertTrue(demo['demo'])
            self.assertEqual(demo['mode'],'synthetic')
            self.assertTrue((out/'report.html').exists())
            self.assertIn('合成示例数据', (out/'report.html').read_text())
            self.assertEqual(main(['demo','--out',str(out)]),1)  # no overwrite
            self.assertEqual(main(['render','--report',str(out/'report.json'), '--out',str(root/'copy.html')]),0)
            self.assertTrue((root/'copy.html').exists())

    def test_generation_and_manual_score(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            form=root/'quiz'
            self.assertEqual(main(['generate','--seed','12','--out',str(form)]),0)
            key=json.loads((form/'answer-key.private.json').read_text())
            rows=[{'id':x['id'],'raw':json.dumps({'answer':x['expected']},ensure_ascii=False)} for x in key['answers']]
            response_path=root/'input.json'
            response_path.write_text(json.dumps(rows,ensure_ascii=False))
            dest=root/'result'
            self.assertEqual(main(['score','--form-dir',str(form),'--responses',str(response_path),'--out',str(dest)]),0)
            self.assertEqual(main(['verify',str(dest)]),0)
            report=json.loads((dest/'report.json').read_text())
            self.assertEqual(report['overall'],100)
            self.assertFalse(report['demo'])

    def test_live_requires_explicit_cost_ack(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'not-created'
            self.assertEqual(main(['run','--out',str(target)]),1)
            self.assertFalse(target.exists())

    def test_unsafe_html_is_escaped(self):
        s=render_html({'agent_label':'</script><script>alert(1)</script>'})
        self.assertNotIn('</script><script>alert(1)',s)
        self.assertIn('\\u003c/script',s)

class GatewayGateTests(unittest.TestCase):
    def test_gateway_requires_separate_consent(self):
        with tempfile.TemporaryDirectory() as folder:
            result=Path(folder)/'not-created'
            self.assertEqual(main(['run','--backend','gateway','--out',str(result),'--ack-provider-calls']),1)
            self.assertFalse(result.exists())
