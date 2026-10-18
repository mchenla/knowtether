"""Narrow advisory range coverage; legitimate punctuation is not a style ban."""
import unittest
from kpdm_hooks.engine import lint_text
from kpdm_hooks.reading import reading_context


class ExpressionTests(unittest.TestCase):
    def test_numeric_dash_hint_with_chinese_units_and_decimal_ranges(self):
        for text in ('第1—2天整理资料。', '初稿800–1200字。', '范围1.5 —— 2.5小时。'):
            self.assertIn('NUMERIC_RANGE_DASH', {i['code'] for i in lint_text(text)}, text)

    def test_normal_ranges_parenthetical_dash_and_code_are_not_flagged(self):
        for text in ('第1 - 2天；800 - 1200字。', '要复查——尤其是数字与单位。',
                     '```python\ntext="1—2"\n```'):
            self.assertNotIn('NUMERIC_RANGE_DASH', {i['code'] for i in lint_text(text)}, text)

    def test_hint_does_not_modify_prose_or_claim_semantic_certainty(self):
        text = '引文：“第1—2天”。'
        note = next(i for i in lint_text(text) if i['code'] == 'NUMERIC_RANGE_DASH')
        self.assertIn('直接引文', note['message'])
        self.assertEqual(text, '引文：“第1—2天”。')

    def test_expression_source_and_calibrated_wording_are_in_reading_pack(self):
        pack = reading_context()
        self.assertIn('## 模型语言指纹与文字温度', pack)
        self.assertIn('现有材料不足以支持该结论', pack)
        self.assertIn('第1 - 2天', pack)
        self.assertIn('MINIMUM_READING end', pack)
