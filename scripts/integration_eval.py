"""Frozen 0.7.0 automatic-hook on/off study; existing source packets, no tags.

Requires an isolated, normally installed and trusted HOME. Does not grant trust,
copy credentials, or manufacture human decisions. Retains every completed draft.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess

from live_codex_eval import run_case
from paired_codex_eval import switch_config


def runtime_paths(repo, ref):
    # Git quotes non-ASCII names without -z; quoted paths evade prefix filters.
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', ref], cwd=repo).decode('utf-8').split('\0')
    return [name for name in paths if name.startswith(('kpdm_hooks/', 'hooks/', 'policy/', 'framework/', 'skills/', 'claude/'))
            or name in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json')]


def schedule(tasks):
    rng = random.Random(700019)
    blocks = []
    for task in tasks:
        first = ['off', 'full']
        rng.shuffle(first)
        blocks.extend([{'task': task['id'], 'rep': 1, 'arms': first},
                       {'task': task['id'], 'rep': 2, 'arms': list(reversed(first))}])
    rng.shuffle(blocks)
    ids = list(range(1, 1 + len(tasks) * 4))
    rng.shuffle(ids)
    for block in blocks:
        block['runs'] = [{'arm': arm, 'id': f'S{ids.pop():03d}'} for arm in block.pop('arms')]
    return blocks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('home', 'bundle', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--codex', required=True)
    parser.add_argument('--runtime', required=True, help='Frozen committed candidate')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    home = args.home.resolve(strict=True)
    bundle = args.bundle.resolve(strict=True)
    base = args.output.resolve()
    if home == (Path.home() / '.codex').resolve() or base.exists() != args.resume:
        parser.error('Use an isolated trusted HOME and fresh output, or explicit --resume')
    repo = Path(__file__).resolve().parents[1]
    runtime = subprocess.check_output(['git', 'rev-parse', args.runtime], cwd=repo, text=True).strip()
    for name in runtime_paths(repo, runtime):
        assert (bundle / name).read_bytes() == subprocess.check_output(['git', 'show', runtime + ':' + name], cwd=repo), name
    raw = (repo / 'examples/source-quality-cases.json').read_bytes()
    tasks = json.loads(raw)
    protocol = {
        'runtime_commit': runtime, 'version': '0.7.0',
        'export_prefix': 'integration-0.7.0',
        'tasks_sha256': hashlib.sha256(raw).hexdigest(),
        'model': 'gpt-6.1-sol', 'effort': 'medium', 'web_search': 'disabled', 'seed': 700019,
        'design': '2 genres x complete/challenged sources x off/on x 2 reversed-order repeats =16 drafts; serial fresh readonly projects',
        'arms': {'off': 'whole plugin disabled', 'full': '0.7.0 automatic hooks; explicit packet arithmetic enabled'},
        'scope': 'Same public historical data and deliberate faults as the0.6.0 source-quality pilot; new model runs, no old output reuse',
        'review': 'neutral directories and path-sanitized masked IDs; development AI, not independent or strict blind review',
        'primary': 'six frozen content criteria; six fault handling statuses; false findings in clean packets; no total quality score',
        'secondary': 'wall/hook/tool durations, actual injected characters, first and cumulative input/cache tokens, source-read tool counts',
        'release_gate': 'Separate mechanical CLI checks; no human-verified or acceptance records invented; not automatically invoked by writing hooks',
        'schedule': schedule(tasks), 'planned_outputs': 16,
    }
    base.mkdir(parents=True, exist_ok=args.resume)
    if args.resume:
        assert json.loads((base / 'protocol.json').read_text()) == protocol
        assert (base / 'frozen-cases.json').read_bytes() == raw
    else:
        (base / 'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
        (base / 'frozen-cases.json').write_bytes(raw)
    config = home / 'config.toml'
    original = config.read_text(encoding='utf-8')
    env = dict(os.environ, CODEX_HOME=str(home), PYTHONUTF8='1', KNOWTETHER_CONTROLLED_EVAL='1')
    results = []
    try:
        for block in protocol['schedule']:
            task = next(t for t in tasks if t['id'] == block['task'])
            for item in block['runs']:
                arm = item['arm']
                config.write_text(switch_config(original, arm != 'off'), encoding='utf-8', newline='\n')
                case = {'id': item['id'], 'prompt': task['prompt'], 'web_search': 'disabled', 'materials': dict(task['materials'])}
                case['materials']['.kpdm/config.json'] = json.dumps({'schema_version': 1, 'evidence': arm == 'full'})
                folder = base / item['id']
                saved = folder / 'summary.json'
                if saved.exists():
                    assert args.resume
                    result = json.loads(saved.read_text(encoding='utf-8'))
                    assert json.loads((folder / 'input.json').read_text(encoding='utf-8')) == case
                    assert result['runtime_commit'] == runtime and result['plugin_enabled'] == (arm != 'off')
                    for name, digest in result['provided_files_sha256'].items():
                        assert hashlib.sha256((folder / 'project' / name).read_bytes()).hexdigest() == digest
                    assert (folder / 'output.md').read_text(encoding='utf-8')
                else:
                    result = run_case(args.codex, base, case, protocol['model'], env=env, enabled=arm != 'off')
                result.update(task=task['id'], genre=task['genre'], variant=task['variant'], arm=arm,
                              repetition=block['rep'], runtime_commit=runtime)
                assert result['materials_unchanged'] and not result['project_files']
                (folder / 'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                results.append(result)
                (base / 'progress.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
                print(json.dumps({'completed': item['id'], 'n': len(results), 'planned': 16,
                                  'seconds': result['elapsed_seconds'], 'hook_ms': result['timing']['hook_milliseconds']}), flush=True)
    finally:
        config.write_text(original, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
