"""Local component checks, not a Claude model-session or quality certificate.

All human-labelled records below are explicitly synthetic test data. Nothing is
written into an author's worksheet. Output is suitable for public verification.
"""
import argparse
import ast
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-bash', type=Path)
    parser.add_argument('--claude', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = {'scope': 'synthetic release-gate fixtures and real local launchers; not Claude end-to-end or independent quality review',
              'release_cases': [], 'launchers': [], 'claude_validation': []}
    state = {'schema_version': 1, 'artifact_version': 'synthetic-test-v1',
             'claims': [{'id': 'C1', 'type': 'fact', 'source_ids': ['S1'], 'support_note': 'SYNTHETIC fixture paragraph1'}],
             'sources': [{'id': 'S1', 'locator': 'SYNTHETIC fixture paragraph1', 'rights_status': 'test-permitted', 'verification': 'human-verified'}],
             'author_acceptance': {'version': 'synthetic-test-v1', 'evidence_ref': 'SYNTHETIC TEST RECORD; not a real human decision'}}
    text = '# 合成测试\n\n这是一条仅用于机械回归的合成事实。\n'
    cases = [('synthetic-complete-control', state, text, 0)]
    for name, edit in [('unverified', lambda s: s['sources'][0].update(verification='agent-checked')),
                       ('rights-unknown', lambda s: s['sources'][0].update(rights_status='unknown')),
                       ('rights-denied', lambda s: s['sources'][0].update(rights_status='denied')),
                       ('acceptance-wrong-version', lambda s: s['author_acceptance'].update(version='other')),
                       ('null-claim', lambda s: s['claims'].append(None)),
                       ('duplicate-source', lambda s: s['sources'].append(copy.deepcopy(s['sources'][0]))),
                       ('missing-type', lambda s: s['claims'][0].pop('type'))]:
        changed = copy.deepcopy(state)
        edit(changed)
        cases.append((name, changed, text, 1))
    cases.extend([('placeholder', state, text + '\n[citation needed]', 1),
                  ('workflow-label', state, '# 内部草稿\n' + text, 1),
                  ('empty-text', state, ' \n', 2),
                  ('no-human-records', None, text, 1)])
    with tempfile.TemporaryDirectory(prefix='kt-integration-') as temp:
        root = Path(temp)
        (root / '.kpdm').mkdir()
        for name, record, artifact, expected in cases:
            path = root / '.kpdm/work.json'
            if record is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(json.dumps(record), encoding='utf-8')
            (root / 'final.md').write_text(artifact, encoding='utf-8')
            start = time.perf_counter()
            done = subprocess.run([sys.executable, '-B', str(repo / 'hooks/entry.py'), 'release',
                                   '--root', str(root), '--artifact', 'final.md'], capture_output=True, text=True, encoding='utf-8', timeout=20)
            elapsed = round(time.perf_counter() - start, 6)
            assert done.returncode == expected, (name, done.stdout, done.stderr)
            result = json.loads(done.stdout) if done.stdout.strip() else {}
            output['release_cases'].append({'case': name, 'exit_code': done.returncode, 'expected_exit_code': expected,
                'wall_seconds': elapsed, 'verdict': result.get('verdict', 'input-error'),
                'codes': sorted({f['code'] for f in result.get('blocking', [])})})
        (root / '.kpdm/work.json').unlink(missing_ok=True)
        hooks = json.loads((repo / 'hooks/hooks.json').read_text())['hooks']
        for host in (['codex-windows'] if os.name == 'nt' else []) + (['claude-git-bash'] if args.git_bash else []):
            env = {k: v for k, v in os.environ.items() if k not in ('PLUGIN_ROOT', 'CLAUDE_PLUGIN_ROOT')}
            env['PLUGIN_ROOT' if host == 'codex-windows' else 'CLAUDE_PLUGIN_ROOT'] = str(repo)
            for event in ('SessionStart', 'UserPromptSubmit', 'Stop'):
                item = hooks[event][0]['hooks'][0]
                command = item['commandWindows'] if host == 'codex-windows' else [str(args.git_bash), '-c', item['command']]
                payload = {'hook_event_name': event, 'cwd': str(root), 'prompt': '请写一份关于知识管理的研究报告，给出适用条件。',
                           'last_assistant_message': '研究报告结论需要来源：[citation needed]。'}
                start = time.perf_counter()
                done = subprocess.run(command, input=json.dumps(payload), capture_output=True, text=True,
                                      encoding='utf-8', env=env, timeout=20)
                result = json.loads(done.stdout)
                assert done.returncode == 0 and result and 'CHECK_SKIPPED' not in done.stdout and 'PYTHON_REQUIRED' not in done.stdout, (host, event, done.stderr)
                assert not any(k in result for k in ('decision', 'continue'))
                if event != 'Stop':
                    assert result['hookSpecificOutput']['additionalContext']
                output['launchers'].append({'host': host, 'event': event, 'exit_code': done.returncode,
                    'wall_seconds': round(time.perf_counter() - start, 6),
                    'context_characters': len(result.get('hookSpecificOutput', {}).get('additionalContext', '')),
                    'scope': 'launcher executed with real host environment variable; not a Claude model session'})
    if args.claude:
        output['claude_version'] = subprocess.check_output([str(args.claude), '--version'], text=True).strip()
        for target in ('.', '.claude-plugin/plugin.json'):
            done = subprocess.run([str(args.claude), 'plugin', 'validate', target, '--strict'], cwd=repo, capture_output=True, text=True)
            assert done.returncode == 0, done.stdout + done.stderr
            output['claude_validation'].append({'target': target, 'exit_code': done.returncode})
    # Preserve the pending PR's exact source; syntax-check without importing its SDK or running cloud calls.
    raw = subprocess.check_output(['git', 'show', 'origin/content-review-agent:managed-agents/content-reviewer/run_review.py'], cwd=repo)
    ast.parse(raw)
    output['managed_agent'] = {'pr': 3, 'status': 'pending; preserved on original branch', 'python_syntax': 'pass',
        'cloud_session': 'not-run', 'reasons': ['ant unavailable on PATH and Claude CLI not authenticated',
        'cloud schema, repository mount, Python availability and actual costs not verified'],
        'review_findings': ['README network restriction does not prevent the initial manuscript upload to cloud',
                            'downloaded filenames and selected artifact path need containment validation before deployment']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'release_cases': len(output['release_cases']), 'launchers': len(output['launchers']),
                      'claude_validations': len(output['claude_validation']), 'cloud_sessions': 0}))


if __name__ == '__main__':
    main()
