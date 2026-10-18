import importlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    paired = importlib.import_module('paired_codex_eval')
finally:
    sys.path.pop(0)


class EvaluationHarnessTests(unittest.TestCase):
    def test_condition_switch_changes_only_target_flag(self):
        text = '[other]\nenabled = true\n[plugins."knowtether@knowtether"]\nenabled = true\n\n[windows]\nsandbox = "elevated"\n'
        result = paired.switch_config(text, False)
        self.assertEqual(result, text.replace('knowtether"]\nenabled = true', 'knowtether"]\nenabled = false'))
        self.assertEqual(paired.switch_config(result, True), text)

    def test_missing_or_duplicate_flags_rejected(self):
        for text in ('', '[plugins."knowtether@knowtether"]\n', '[plugins."knowtether@knowtether"]\nenabled=true\nenabled=false\n'):
            with self.assertRaises(ValueError):
                paired.switch_config(text, False)

    def test_seeded_schedule_balances_order_for_each_case(self):
        cases = [{'id': 'one'}, {'id': 'two'}]
        schedule = paired.plan(cases, 2, 20261017)
        self.assertEqual(schedule, paired.plan(cases, 2, 20261017))
        for case in cases:
            orders = [p['order'] for p in schedule if p['case'] == case['id']]
            self.assertEqual(sorted(orders), [[False, True], [True, False]])
