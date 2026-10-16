import json
import unittest
from clawiq.core import generate
from clawiq.scoring import parse, score, verify_report


def oracle(form):
    return [{"id": a['id'], "raw": json.dumps({"answer":a['expected']}, ensure_ascii=False)} for a in form.key['answers']]


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.form = generate(444)
        self.rows = oracle(self.form)

    def test_all_pass(self):
        x=score(self.form.public,self.form.key,self.rows)
        self.assertEqual(x['status'],'complete')
        self.assertEqual(x['overall'],100)
        self.assertEqual(x['brain_score'],100)
        self.assertEqual(x['task_score'],100)
        self.assertTrue(verify_report(x,self.form.public,self.form.key,self.rows))

    def test_wrong_json_is_failed_not_missing(self):
        self.rows[0]['raw'] = 'The answer is 123'
        r=score(self.form.public,self.form.key,self.rows)
        self.assertEqual(r['status'],'complete')
        self.assertLess(r['overall'],100)
        self.assertTrue(any(c['error']=='invalid-json' for c in r['cases']))

    def test_partial_or_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            score(self.form.public,self.form.key,self.rows[:-1])
        with self.assertRaises(ValueError):
            score(self.form.public,self.form.key,self.rows+self.rows[:1])
        with self.assertRaises(ValueError):
            score(self.form.public,self.form.key,self.rows+[{'id':'wrong','raw':'{}'}])

    def test_provider_error_invalidates_run(self):
        self.rows[1]['error'] = 'process-error'
        r=score(self.form.public,self.form.key,self.rows)
        self.assertEqual(r['status'],'invalid')
        self.assertIsNone(r['overall'])
        self.assertIsNone(r['brain_score'])
        self.assertIsNone(r['task_score'])

    def test_verification_detects_tampered_report(self):
        r=score(self.form.public,self.form.key,self.rows)
        r['overall']=99
        with self.assertRaises(ValueError):
            verify_report(r,self.form.public,self.form.key,self.rows)

    def test_strict_types(self):
        self.assertFalse(__import__('clawiq.scoring',fromlist=['_equal'])._equal(True,1))
        self.assertEqual(parse('{"answer":null}'),(None,None))
        self.assertEqual(parse('{"answer":1,"extra":1}')[1],'invalid-shape')
        self.assertEqual(parse('```json\n{"answer":1}\n```')[1],'invalid-json')

    def test_dont_echo_untrusted_response_to_public_report(self):
        self.rows[0]['raw'] = json.dumps({'answer':'PRIVATE_KEY_DO_NOT_LEAK'})
        r=score(self.form.public,self.form.key,self.rows)
        self.assertNotIn('PRIVATE_KEY_DO_NOT_LEAK', json.dumps(r,ensure_ascii=False))

    def test_all_type_paths(self):
        f=generate(79,'standard')
        r=score(f.public,f.key,oracle(f))
        self.assertEqual(r['sample_size'],40)
        self.assertTrue(all(v['correct']==v['count'] for v in r['dimensions'].values()))
