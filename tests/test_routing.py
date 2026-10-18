from pathlib import Path
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

    def test_invisible_characters_are_hints_not_watermark_verdicts(self):
        notes = lint_text('知识说明中有\u200b不可见字符。')
        item = next(n for n in notes if n['code'] == 'INVISIBLE_CHARACTERS')
        self.assertIn('不证明', item['message'])
        self.assertFalse(any(n['code']=='INVISIBLE_CHARACTERS' for n in lint_text('正常中文和👩‍💻表情。')))

    def test_praise_hint_does_not_ban_positive_factual_results(self):
        self.assertTrue(any(n['code']=='EVALUATIVE_PRAISE' for n in lint_text('您的观点确实高瞻远瞩。')))
        self.assertFalse(any(n['code']=='EVALUATIVE_PRAISE' for n in lint_text('该组平均分提高了10分。')))
