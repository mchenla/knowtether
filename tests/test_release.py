import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from kpdm_hooks.hooks import handle
from kpdm_hooks.release import RULES, release_gate

REPO = Path(__file__).resolve().parents[1]

GOOD_TEXT = "# 复盘记录怎样写\n\n团队在三月把复盘改为每两周一次（见内部记录）。\n\n```python\n# TODO: code examples are ignored\n```\n"
GOOD_STATE = {
    "schema_version": 1, "enabled": True, "mode": "warn", "session_id": "s",
    "policy_version": "0.5.0-rc.2", "input_version": "task-1", "artifact_version": "v3",
    "status": "draft", "open_issues": [], "worksheet": {},
    "claims": [{"id": "C1", "text": "三月改为每两周一次", "type": "fact",
                "source_ids": ["S1"], "support_note": "会议纪要第2段"}],
    "sources": [{"id": "S1", "locator": "records/2026-03.md#2", "rights_status": "internal-permitted",
                 "verification": "human-verified"}],
    "author_acceptance": {"version": "v3", "evidence_ref": "作者在会话中接受 v3，2026-10-18"},
}


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix='release-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, state=GOOD_STATE, text=GOOD_TEXT):
        if state is not None:
            (self.root / '.kpdm').mkdir(exist_ok=True)
            (self.root / '.kpdm/work.json').write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
        (self.root / 'final.md').write_text(text, encoding='utf-8')
        return release_gate(self.root, 'final.md')

    def codes(self, result):
        return {item['code'] for item in result['blocking']}

    def test_complete_records_pass_and_code_blocks_are_ignored(self):
        result = self.write()
        self.assertEqual(result['verdict'], 'pass', result['blocking'])
        self.assertEqual(result['rules'], list(RULES))
        self.assertIn('cannot detect', result['limits'])

    def test_rule_1_unverified_or_missing_sources_block(self):
        cases = []
        state = copy.deepcopy(GOOD_STATE); state['sources'][0]['verification'] = 'agent-checked'; cases.append(state)
        state = copy.deepcopy(GOOD_STATE); state['sources'][0]['locator'] = ''; cases.append(state)
        state = copy.deepcopy(GOOD_STATE); state['claims'][0]['source_ids'] = []; cases.append(state)
        state = copy.deepcopy(GOOD_STATE); state['claims'][0]['source_ids'] = ['S9']; cases.append(state)
        state = copy.deepcopy(GOOD_STATE); del state['claims'][0]['support_note']; cases.append(state)
        state = copy.deepcopy(GOOD_STATE); state['claims'] = []; cases.append(state)
        for state in cases:
            result = self.write(state)
            self.assertEqual(result['verdict'], 'fail')
            self.assertIn('RELEASE_SOURCE', self.codes(result))

    def test_rule_1_explicit_no_external_facts_declaration(self):
        state = copy.deepcopy(GOOD_STATE)
        state['claims'] = [{"id": "C1", "type": "method", "source_ids": []}]
        state['sources'] = []
        self.assertIn('RELEASE_SOURCE', self.codes(self.write(state)))
        state['publication'] = {"external_facts": "none"}
        self.assertEqual(self.write(state)['verdict'], 'pass')

    def test_rule_2_placeholders_block_with_line_numbers(self):
        for marker in ('[citation needed]', 'TODO', 'TBD', '[待补来源]', '【待核实】', '（待补）', '<SOURCE_TODO>'):
            result = self.write(text=GOOD_TEXT + '\n结论成立' + marker + '。\n')
            self.assertEqual(self.codes(result), {'RELEASE_PLACEHOLDER'}, marker)
            self.assertIn('L9', result['blocking'][0]['message'])
        self.assertEqual(self.write(text=GOOD_TEXT + '\nMake a todo list.\n')['verdict'], 'pass')

    def test_rule_3_unknown_rights_block(self):
        for value in ('unknown', 'blocked-unknown-rights', '待定', '', None):
            state = copy.deepcopy(GOOD_STATE); state['sources'][0]['rights_status'] = value
            self.assertEqual(self.codes(self.write(state)), {'RELEASE_RIGHTS'}, value)

    def test_rule_4_acceptance_must_match_the_released_version(self):
        state = copy.deepcopy(GOOD_STATE); state['author_acceptance']['version'] = 'v2'
        self.assertEqual(self.codes(self.write(state)), {'RELEASE_ACCEPTANCE'})
        state = copy.deepcopy(GOOD_STATE); state['author_acceptance']['evidence_ref'] = ''
        self.assertEqual(self.codes(self.write(state)), {'RELEASE_ACCEPTANCE'})
        state = copy.deepcopy(GOOD_STATE); del state['author_acceptance']
        self.assertEqual(self.codes(self.write(state)), {'RELEASE_ACCEPTANCE'})

    def test_rule_5_workflow_labels_block(self):
        for label in ('候选发布版', '内部草稿', '供张三审阅', 'DRAFT', 'WIP', 'Candidate release', '初稿DRAFT'):
            result = self.write(text='# 标题（' + label + '）\n' + GOOD_TEXT)
            self.assertEqual(self.codes(result), {'RELEASE_WORKFLOW_LABEL'}, label)
        self.assertEqual(self.write(text=GOOD_TEXT + '\n写好初稿后再请同事读一遍。\n')['verdict'], 'pass')

    def test_missing_work_record_fails(self):
        result = self.write(state=None)
        self.assertEqual(result['verdict'], 'fail')
        self.assertEqual(self.codes(result), {'RELEASE_SOURCE', 'RELEASE_ACCEPTANCE'})

    def test_bundled_entry_exit_codes_without_pip(self):
        argv = [sys.executable, '-B', str(REPO / 'hooks/entry.py'), 'release', '--root', str(self.root), '--artifact', 'final.md']
        self.write()
        passed = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertEqual(json.loads(passed.stdout)['verdict'], 'pass')
        self.write(text=GOOD_TEXT + '\n[citation needed]\n')
        failed = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(json.loads(failed.stdout)['verdict'], 'fail')

    def test_artifact_outside_project_is_refused(self):
        self.write()
        argv = [sys.executable, '-B', str(REPO / 'hooks/entry.py'), 'release', '--root', str(self.root), '--artifact', '../outside.md']
        result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(result.returncode, 2)

    def test_daily_hooks_stay_advisory_when_the_gate_would_fail(self):
        self.write(text=GOOD_TEXT + '\n[citation needed] 候选发布版\n')
        self.assertEqual(release_gate(self.root, 'final.md')['verdict'], 'fail')
        event = {'hook_event_name': 'Stop', 'cwd': str(self.root),
                 'last_assistant_message': '研究报告解释知识：[citation needed] 候选发布版'}
        response = handle(event, self.root, 'Stop', plugin=True)
        self.assertNotIn('decision', response)
        self.assertNotIn('continue', response)
        self.assertEqual(set(response), {'systemMessage'})
        hooks = (REPO / 'hooks/hooks.json').read_text(encoding='utf-8')
        self.assertNotIn('release', hooks)


if __name__ == '__main__':
    unittest.main()
