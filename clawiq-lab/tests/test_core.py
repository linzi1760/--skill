import json
import unittest
from clawiq.core import DIMENSIONS, SUITES, fingerprint, generate, validate_form


class GenerationTests(unittest.TestCase):
    def test_repeatable(self):
        for name in SUITES:
            a = generate(43, name)
            b = generate(43, name)
            self.assertEqual(a, b)
            validate_form(a.public, a.key)

    def test_varies_by_seed(self):
        a, b = generate(43), generate(44)
        self.assertNotEqual(a.public, b.public)
        self.assertNotEqual(a.key, b.key)

    def test_unique_questions_and_dimensions(self):
        for name, spec in SUITES.items():
            a = generate(49, name)
            ids = [q['id'] for q in a.public['items']]
            self.assertEqual(len(ids), sum(spec.values()))
            self.assertEqual(len(set(ids)), len(ids))
            self.assertEqual(len(a.key['answers']), len(ids))
            self.assertEqual(set(q['dimension'] for q in a.public['items']), set(DIMENSIONS))
            self.assertEqual(set(x['id'] for x in a.key['answers']), set(ids))
            self.assertEqual(sum(a.public['items'][0]['dimension'] == d for d in DIMENSIONS), 1)

    def test_answer_key_not_leaked_in_public(self):
        a = generate(123)
        self.assertNotIn('expected', json.dumps(a.public))
        self.assertNotIn('solution', json.dumps(a.public))
        self.assertNotIn('explanation', json.dumps(a.public))
        self.assertIn('commitment', a.public)
        self.assertEqual(fingerprint({k:v for k,v in a.public.items() if k != 'commitment'}), a.public['commitment'])

    def test_mutated_answer_key_is_rejected(self):
        a = generate(8)
        a.key['answers'][0]['expected'] = 'cheated'
        with self.assertRaises(ValueError):
            validate_form(a.public, a.key)

    def test_bad_suite_and_seed(self):
        for v in ('wrong', '', None):
            with self.assertRaises(ValueError):
                generate(42, v)
        for v in (-1, 2**32, True, '17'):
            with self.assertRaises(ValueError):
                generate(v)

    def test_generated_answers_are_valid_facts(self):
        # Cross-check by reproducing explicit numeric logic in prompts would require
        # an external oracle; here we cover all question templates and structures.
        for suite in ('quick', 'standard'):
            for seed in (2, 11, 42, 101, 20261016):
                f = generate(seed, suite)
                self.assertEqual(len(f.public['items']), len(f.key['answers']))
                for q in f.public['items']:
                    self.assertIn('仅输出一个严格合法的JSON对象', q['prompt'])
                answers = {a['id']:a['expected'] for a in f.key['answers']}
                for q in f.public['items']:
                    a = answers[q['id']]
                    if q['dimension'] == 'reliability':
                        self.assertIn(a['status'], ('supported','unknown','conflict'))
                    if q['dimension'] == 'instruction':
                        self.assertIsInstance(a,list)
                    if q['dimension'] in ('reasoning','workflow'):
                        self.assertIsInstance(a,int)
