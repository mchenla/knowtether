"""Validate frozen adaptive runs and mask condition labels before content review."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--old-bundle', type=Path, required=True)
    args = parser.parse_args()
    base = args.run.resolve(strict=True)
    protocol = json.loads((base/'protocol.json').read_text(encoding='utf-8'))
    frozen = (base/'frozen-tasks.json').read_bytes()
    assert hashlib.sha256(frozen).hexdigest() == protocol['tasks_sha256']
    source = (base/'sources.md').read_text(encoding='utf-8')
    assert hashlib.sha256(source.encode()).hexdigest() == protocol['source_sha256']
    tasks = {t['id']: t for t in json.loads(frozen)}
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from kpdm_hooks.routing import prompt_context
    old = subprocess.check_output([sys.executable, '-I', '-B', '-c',
        "import sys;sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,sys.argv[1]);"
        "from kpdm_hooks.reading import reading_context;print(reading_context(),end='')",
        str(args.old_bundle.resolve(strict=True))], text=True, encoding='utf-8')
    rows = []
    for block in protocol['schedule']:
        for arm in block['arms']:
            name = f"{block['task']}-r{block['rep']}-{arm}"
            folder = base/name
            summary = json.loads((folder/'summary.json').read_text(encoding='utf-8'))
            incoming = json.loads((folder/'input.json').read_text(encoding='utf-8'))
            assert incoming['prompt'] == tasks[block['task']]['prompt']
            assert summary['arm'] == arm and summary['plugin_enabled'] == (arm != 'off')
            assert summary['materials_unchanged'] and not summary['project_files']
            expected_files = {} if block['task'] == 'light' else {'sources.md': protocol['source_sha256']}
            assert summary['provided_files_sha256'] == expected_files
            events = [json.loads(s) for s in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()]
            inventory = events[0]['condition_inventory']
            assert inventory['enabled'] == (arm != 'off')
            runs = [e['params']['run'] for e in events if e.get('method') == 'hook/completed']
            prompt_contexts = [entry['text'] for r in runs if r.get('statusMessage') == 'KnowTether: UserPromptSubmit'
                               for entry in r['entries'] if entry['kind'] == 'context']
            if arm == 'off':
                assert not runs and not prompt_contexts and not inventory['active_knowtether_skills']
            else:
                expected = old if arm == 'old' else prompt_context(incoming['prompt'])
                assert prompt_contexts == [expected], 'Unexpected context: ' + name
                assert len(runs) == 3 and all(r['status'] == 'completed' for r in runs)
            answer = (folder/'output.md').read_text(encoding='utf-8')
            assert answer
            rows.append(dict(summary, output_sha256=hashlib.sha256(answer.encode()).hexdigest()))
    assert len(rows) == protocol['planned_valid_outputs'] == 18
    order = list(rows)
    random.Random(501018).shuffle(order)
    mapping, packets = {}, []
    for index, row in enumerate(order, 1):
        label = f'K{index:02d}'
        mapping[label] = row['case']
        task = tasks[row['task']]
        packets.append({'id': label, 'task': row['task'], 'criteria': task['criteria'],
                        'answer': (base/row['case']/'output.md').read_text(encoding='utf-8')})
    for name, value in [('validated-results.json', rows), ('private-mapping.json', mapping),
                        ('masked-review.json', packets)]:
        (base/name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'validated': len(rows), 'masked_packets': len(packets),
                      'exact_context_and_materials': True, 'semantic_review': 'pending'}))


if __name__ == '__main__':
    main()
