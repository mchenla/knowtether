import json
from pathlib import Path
import tempfile
import unittest

from kpdm_hooks.evidence import paired_table, compile_task, audit_product
from kpdm_hooks.hooks import handle


class EvidenceTests(unittest.TestCase):
    spec = {'path':'records.csv','group':'task','pair':'rep','condition':'arm',
            'baseline':'off','treatment':'new','metrics':['seconds']}
    data = b'task,rep,arm,seconds\na,1,off,10\na,1,new,20\na,2,off,100\na,2,new,100\n'

    def bundle(self, root):
        (root/'.kpdm').mkdir()
        manifest={'schema_version':1,'table':self.spec,'context':'context.json',
                  'product':{'kind':'slides','pages':2,'max_body_chars':80}}
        (root/'.kpdm/task.json').write_text(json.dumps(manifest),encoding='utf-8')
        (root/'context.json').write_text('{"scope":"a small paired pilot"}')
        (root/'records.csv').write_bytes(self.data)
        return manifest

    def test_pairing_precedes_aggregation_and_zero_and_unmatched_are_visible(self):
        result=paired_table(self.data,self.spec)['a']['metrics']['seconds']
        self.assertEqual(result['median_paired_change_pct'],50)
        self.assertNotAlmostEqual(100*(result['treatment_median']/result['baseline_median']-1),50)
        result=paired_table(self.data+b'a,3,off,0\na,3,new,5\na,4,new,12\n',self.spec)['a']
        self.assertEqual(result['matched_pairs'],3)
        self.assertEqual(result['unmatched_pairs'],['4'])
        self.assertEqual(result['metrics']['seconds']['zero_baselines_excluded_from_pct'],1)

    def test_duplicate_invalid_and_unexpected_data_are_rejected(self):
        for bad in [self.data+b'a,1,off,10\n',self.data+b'a,3,new,nan\n',self.data+b'a,3,new,-1\n',self.data+b'a,3,other,10\n']:
            with self.assertRaises(ValueError): paired_table(bad,self.spec)

    def test_opt_in_receipts_and_failures_do_not_expose_other_project_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.assertIsNone(compile_task(root))
            manifest=self.bundle(root)
            pack=compile_task(root)
            self.assertEqual(pack['status'],'ready')
            self.assertEqual(len(pack['receipts']),3)
            before=sorted(str(p.relative_to(root)) for p in root.rglob('*'))
            manifest['context']='../outside.json'
            (root/'.kpdm/task.json').write_text(json.dumps(manifest))
            self.assertEqual(compile_task(root)['code'],'EVIDENCE_UNAVAILABLE')
            self.assertEqual(before,sorted(str(p.relative_to(root)) for p in root.rglob('*')))

    def test_page_budget_excludes_notes_but_does_not_certify_layout(self):
        product={'kind':'slides','pages':2,'max_body_chars':80}
        text='### 第1页｜结论\n'+('文'*81)+'\n**讲述提示**\n'+('稿'*400)+'\n### 第2页｜决定\n简短\n'
        notes=audit_product(text,product)
        self.assertEqual([n['code'] for n in notes],['SLIDE_TEXT_BUDGET'])
        self.assertIn('不',notes[0]['message'])
        self.assertEqual(audit_product('### 第1页\n短文',product)[0]['code'],'SLIDE_COUNT')
        self.assertEqual(audit_product('正文',product)[0]['code'],'SLIDE_STRUCTURE_UNKNOWN')

    def test_hook_compiles_explicit_sources_and_ablation_switch_works(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.bundle(root)
            event={'hook_event_name':'UserPromptSubmit','prompt':'写一份工作汇报PPT'}
            text=handle(event,root,'UserPromptSubmit',plugin=True)['hookSpecificOutput']['additionalContext']
            self.assertIn('PROJECT_EVIDENCE',text)
            self.assertIn('median_paired_change_pct',text)
            (root/'.kpdm/config.json').write_text('{"schema_version":1,"evidence":false}')
            text=handle(event,root,'UserPromptSubmit',plugin=True)['hookSpecificOutput']['additionalContext']
            self.assertNotIn('PROJECT_EVIDENCE',text)

    def test_slide_manifest_does_not_audit_ordinary_code_answer(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.bundle(root)
            result=handle({'hook_event_name':'Stop','last_assistant_message':
                           'Fixed the import and ran the unit tests.'},root,'Stop',plugin=True)
            self.assertEqual(result,{})
            result=handle({'hook_event_name':'Stop','last_assistant_message':
                           '### 第1页\n决定'},root,'Stop',plugin=True)
            self.assertIn('SLIDE_COUNT',result['systemMessage'])

