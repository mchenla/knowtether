from pathlib import Path
import hashlib
import shutil
import tempfile
from unittest.mock import patch
import unittest
from kpdm_hooks.routing import route, prompt_context
from kpdm_hooks.engine import lint_text


class RoutingTests(unittest.TestCase):
    def test_light_does_not_read_framework_or_launch_any_tool(self):
        with patch('kpdm_hooks.reading.prepare', side_effect=AssertionError('unexpected reading')):
            text = prompt_context('写一篇约150字的知识分享，给三个阅读建议。')
        self.assertIn('[KnowTether LIGHT]', text)
        self.assertIn('未读KPDM原文', text)
        self.assertLess(len(text), 700)

    def test_complex_profile_reads_only_matching_passages(self):
        report = prompt_context('写一份研究报告，论证是否应推广AI。')
        book = prompt_context('写一个工具书章节，教人评估AI项目。')
        self.assertIn('Profile D｜报告', report)
        self.assertNotIn('Profile B｜书籍', report)
        self.assertIn('Profile B｜书籍', book)
        self.assertLess(len(report), 4000)
        self.assertIn('MINIMUM_READING end', report)

    def test_complexity_override_and_expression_drilldown(self):
        self.assertEqual(route('请展开完整KPDM工作流')['tier'], 'full')
        text = prompt_context('为工具书改写一个1500字章节，调整文风。')
        self.assertIn('模型语言指纹与文字温度', text)
        self.assertIn('Profile B｜书籍', text)

    def test_explicit_full_request_reaches_hook_without_product_keywords(self):
        from kpdm_hooks.hooks import handle
        with tempfile.TemporaryDirectory() as folder:
            for prompt in ['请按完整KPDM处理', '请按KPDM完整流程处理', 'Use full KPDM']:
                result = handle({'hook_event_name': 'UserPromptSubmit', 'prompt': prompt}, Path(folder), 'UserPromptSubmit', plugin=True)
                text = result['hookSpecificOutput']['additionalContext']
                self.assertIn('MINIMUM_READING ready', text)
                self.assertIn('full policy', text)
                self.assertIn('一、从一句话任务开始', text)

    def test_focused_receipts_match_source_and_missing_type_degrades(self):
        from kpdm_hooks.reading import prepare
        repo = Path(__file__).resolve().parents[1]
        profile = route('为管理者写一份决策报告')
        pack = prepare(repo, profile=profile)
        self.assertEqual(pack['status'], 'ready')
        for doc in pack['documents']:
            raw = (repo/doc['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), doc['sha256'])
            lines = raw.decode('utf-8').splitlines(keepends=True)
            for section in doc['sections']:
                self.assertEqual(section['text'], ''.join(lines[section['first_line']-1:section['last_line']]))
        self.assertEqual(hashlib.sha256(pack['adaptation']['text'].encode()).hexdigest(), pack['adaptation']['sha256'])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ['framework/kpdm/snapshot.json', 'policy/collaboration.md', pack['documents'][0]['path']]:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(repo/name, target)
            self.assertEqual(prepare(root, profile=profile)['code'], 'READING_UNAVAILABLE')

    def test_invisible_characters_are_hints_not_watermark_verdicts(self):
        notes = lint_text('知识说明中有\u200b不可见字符。')
        item = next(n for n in notes if n['code'] == 'INVISIBLE_CHARACTERS')
        self.assertIn('不证明', item['message'])
        self.assertFalse(any(n['code']=='INVISIBLE_CHARACTERS' for n in lint_text('正常中文和👩‍💻表情。')))

    def test_praise_hint_does_not_ban_positive_factual_results(self):
        self.assertTrue(any(n['code']=='EVALUATIVE_PRAISE' for n in lint_text('您的观点确实高瞻远瞩。')))
        self.assertFalse(any(n['code']=='EVALUATIVE_PRAISE' for n in lint_text('该组平均分提高了10分。')))
