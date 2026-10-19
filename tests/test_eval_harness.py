import importlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    paired = importlib.import_module('paired_codex_eval')
    source_quality = importlib.import_module('source_quality_eval')
    source_summary = importlib.import_module('summarize_source_quality_eval')
    integration = importlib.import_module('integration_eval')
finally:
    sys.path.pop(0)


class EvaluationHarnessTests(unittest.TestCase):
    def test_runtime_inventory_includes_every_snapshot_document_with_unicode_names(self):
        repo = Path(__file__).resolve().parents[1]
        names = integration.runtime_paths(repo, 'HEAD')
        snapshot = json.loads((repo / 'framework/kpdm/snapshot.json').read_text(encoding='utf-8'))
        required = {'framework/kpdm/' + row['path'] for row in snapshot['documents']}
        self.assertTrue(any(any(ord(c) > 127 for c in name) for name in required))
        self.assertTrue(required.issubset(set(names)), sorted(required - set(names)))

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

    def test_source_quality_schedule_is_balanced_with_neutral_unique_paths(self):
        tasks=[{'id':n} for n in ['report-complete','report-challenged','book-complete','book-challenged']]
        blocks=source_quality.schedule(tasks)
        ids=[r['id'] for b in blocks for r in b['runs']]
        self.assertEqual(len(set(ids)),24)
        self.assertTrue(all(n.startswith('S') and n[1:].isdigit() for n in ids))
        for task in tasks:
            repeats=sorted((b for b in blocks if b['task']==task['id']),key=lambda b:b['rep'])
            orders=[[r['arm'] for r in b['runs']] for b in repeats]
            self.assertEqual(orders[0],list(reversed(orders[1])))
            self.assertEqual(set(orders[0]),{'off','lean','full'})

    def test_review_redaction_preserves_math_and_only_removes_project_prefix(self):
        project=Path(__file__).resolve().parent/'neutral-project'
        prefix=str(project.resolve())
        text='[CSV]('+prefix.replace('\\','/')+'/records.csv) '+r'\(x\) and C:\other\file'
        self.assertEqual(source_summary.sanitize_answer(text,project),
                         '[CSV](records.csv) '+r'\(x\) and C:\other\file')

    def test_integration_schedule_keeps_all_four_tasks_and_reverses_each_pair(self):
        tasks = [{'id': n} for n in ('report-complete', 'report-challenged', 'book-complete', 'book-challenged')]
        blocks = integration.schedule(tasks)
        ids = [r['id'] for b in blocks for r in b['runs']]
        self.assertEqual(len(set(ids)), 16)
        for task in tasks:
            pair = sorted((b for b in blocks if b['task'] == task['id']), key=lambda b: b['rep'])
            orders = [[r['arm'] for r in b['runs']] for b in pair]
            self.assertEqual(orders[0], list(reversed(orders[1])))
            self.assertEqual(set(orders[0]), {'off', 'full'})
