"""Reproduce six mechanical false passes in the preserved PR #2 implementation.

Only synthetic records are used. Does not create human verification or acceptance
for any actual manuscript. Run verify_integration.py first to create the report.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from kpdm_hooks.release import release_gate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='eab3c324b0b644966655f11365e01ef1bcc4348b')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    namespace = {'__name__': 'kpdm_hooks.release_before', '__package__': 'kpdm_hooks'}
    source = subprocess.check_output(['git', 'show', args.baseline + ':kpdm_hooks/release.py'], cwd=REPO)
    exec(compile(source, '<preserved-release-gate>', 'exec'), namespace)
    state = {'schema_version': 1, 'artifact_version': 'synthetic-v1',
             'claims': [{'id': 'C1', 'type': 'fact', 'source_ids': ['S1'], 'support_note': 'SYNTHETIC support'}],
             'sources': [{'id': 'S1', 'locator': 'SYNTHETIC location', 'verification': 'human-verified', 'rights_status': 'test-permitted'}],
             'author_acceptance': {'version': 'synthetic-v1', 'evidence_ref': 'SYNTHETIC TEST RECORD; not a human decision'}}
    rows = []
    with tempfile.TemporaryDirectory(prefix='kt-release-before-') as folder:
        root = Path(folder)
        (root / '.kpdm').mkdir()
        for name in ('null-claim', 'null-source', 'duplicate-source', 'untyped-extra-claim', 'rights-denied', 'empty-text'):
            record = copy.deepcopy(state)
            text = '合成回归测试文本。'
            if name == 'null-claim': record['claims'].append(None)
            if name == 'null-source': record['sources'].append(None)
            if name == 'duplicate-source': record['sources'].append(copy.deepcopy(record['sources'][0]))
            if name == 'untyped-extra-claim': record['claims'].append({'id': 'C2'})
            if name == 'rights-denied': record['sources'][0]['rights_status'] = 'denied'
            if name == 'empty-text': text = ' \n'
            (root / '.kpdm/work.json').write_text(json.dumps(record), encoding='utf-8')
            (root / 'final.md').write_text(text, encoding='utf-8')
            before = namespace['release_gate'](root, 'final.md')['verdict']
            try:
                after = release_gate(root, 'final.md')['verdict']
            except ValueError:
                after = 'input-error'
            assert before == 'pass' and after in ('fail', 'input-error'), (name, before, after)
            rows.append({'case': name, 'before': before, 'after': after})
    report = json.loads(args.output.read_text(encoding='utf-8'))
    report['release_regression_comparison'] = {'baseline_commit': args.baseline,
        'fixtures': 'explicitly synthetic records; pure functions, not a semantic-quality test', 'records': rows}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'reproduced_before_false_passes': len(rows), 'all_rejected_after': True}))


if __name__ == '__main__':
    main()
