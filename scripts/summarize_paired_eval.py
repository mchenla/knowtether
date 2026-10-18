"""Validate a complete pilot and prepare masked answers; no semantic grading.

Run after all scheduled turns. Mapping and summaries stay in the private run
directory until the masked rubric review is frozen. Timing is descriptive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--allow-incomplete', action='store_true', help='Report missing pairs explicitly; never silently fill them')
    args = parser.parse_args()
    base = args.run.resolve(strict=True)
    protocol = json.loads((base / 'protocol.json').read_text(encoding='utf-8'))
    frozen = (base / 'frozen-cases.json').read_bytes()
    assert hashlib.sha256(frozen).hexdigest() == protocol['cases_sha256']
    tasks = {c['id']: c for c in json.loads(frozen)}
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from kpdm_hooks.reading import reading_context
    expected = reading_context()
    rows, missing = [], []
    for pair in protocol['schedule']:
        expected_names = [f"{pair['case']}-r{pair['repetition']}-{'on' if enabled else 'off'}" for enabled in pair['order']]
        absent = [name for name in expected_names if not (base / name / 'summary.json').is_file()]
        if absent:
            if not args.allow_incomplete:
                raise SystemExit('Incomplete pilot; missing summaries: ' + ', '.join(absent))
            missing.append({'task': pair['case'], 'repetition': pair['repetition'], 'missing': absent,
                            'paired_analysis': 'not included; no fabricated output or quality score'})
            continue
        for enabled in pair['order']:
            name = f"{pair['case']}-r{pair['repetition']}-{'on' if enabled else 'off'}"
            target = base / name
            if not (target / 'summary.json').is_file():
                raise SystemExit('Incomplete pilot; missing summary: ' + name)
            summary = json.loads((target / 'summary.json').read_text(encoding='utf-8'))
            events = [json.loads(s) for s in (target / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
            incoming = json.loads((target / 'input.json').read_text(encoding='utf-8'))
            assert incoming['prompt'] == tasks[pair['case']]['prompt']
            assert summary['plugin_enabled'] == enabled
            assert summary['active_knowtether_skills'] == int(enabled)
            runs = [e['params']['run'] for e in events if e.get('method') == 'hook/completed']
            contexts = [entry['text'] for r in runs if r.get('statusMessage') == 'KnowTether: UserPromptSubmit'
                        for entry in r['entries'] if entry['kind'] == 'context']
            if enabled:
                assert contexts == [expected], 'Reading pack mismatch: ' + name
                assert len(runs) == 3 and all(r['status'] == 'completed' for r in runs)
            else:
                assert not runs and not contexts, 'Control contaminated: ' + name
            assert not summary['project_files']
            text = (target / 'output.md').read_text(encoding='utf-8')
            prose = re.sub(r'```.*?```', '', text, flags=re.S)
            row = dict(summary, task=pair['case'], repetition=pair['repetition'],
                       output_sha256=hashlib.sha256(text.encode()).hexdigest(),
                       raw_numeric_long_dash_count=len(re.findall(r'\d+(?:\.\d+)?[ \t]*[—–]+[ \t]*\d+(?:\.\d+)?', prose)))
            rows.append(row)
    assert len(rows) + 2 * len(missing) == 24
    # Do not print this mapping before the content review is recorded.
    order = list(range(len(rows)))
    random.Random(41017).shuffle(order)
    packets, mapping = [], {}
    prior_path = base / 'private-mapping.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8')) if prior_path.exists() else {}
    old_labels = {name: label for label, name in prior.items()}
    available = iter(f'B{i:02d}' for i in range(1, len(rows) + 1) if f'B{i:02d}' not in prior)
    for number, index in enumerate(order, 1):
        row = rows[index]
        label = old_labels.get(row['case']) or next(available)
        mapping[label] = row['case']
        packets.append({'id': label, 'task': row['task'], 'prompt': tasks[row['task']]['prompt'],
                        'criteria': tasks[row['task']]['criteria'],
                        'answer': (base / row['case'] / 'output.md').read_text(encoding='utf-8')})
    (base / 'masked-review.json').write_text(json.dumps(packets, ensure_ascii=False, indent=2), encoding='utf-8')
    (base / 'private-mapping.json').write_text(json.dumps(mapping, indent=2), encoding='utf-8')
    (base / 'validated-results.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    (base / 'missing-pairs.json').write_text(json.dumps(missing, indent=2), encoding='utf-8')
    (base / 'expected-context.txt').write_text(expected, encoding='utf-8')
    print(json.dumps({'validated_turns': len(rows), 'exact_context_characters': len(expected),
                      'context_sha256': hashlib.sha256(expected.encode()).hexdigest(),
                      'masked_packets_ready': len(packets), 'planned_turns': 24, 'missing_pairs': missing,
                      'semantic_grade': 'pending masked AI review'}))


if __name__ == '__main__':
    main()
