"""Run a preregistered on/off pilot in an ALREADY prepared isolated Codex home.

Does not install, authorize, copy credentials, change trust or score semantics.
Creates fresh read-only projects. CLI per-process overrides switch the entire
plugin, not merely project hook output. All attempts, outputs and timing remain.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import random
import shutil

from live_codex_eval import run_case


def plan(cases, repetitions, seed):
    rng = random.Random(seed)
    pairs = []
    for case in cases:
        for repetition in range(repetitions):
            # Two repetitions use opposite order; randomize the first one.
            if repetition % 2 == 0:
                first = rng.choice([True, False])
            order = [first, not first] if repetition % 2 == 0 else [not first, first]
            pairs.append({'case': case['id'], 'repetition': repetition + 1, 'order': order})
    rng.shuffle(pairs)
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--codex', default=shutil.which('codex'))
    parser.add_argument('--model', default='gpt-6.1-sol')
    parser.add_argument('--seed', type=int, default=20261017)
    parser.add_argument('--repetitions', type=int, default=2)
    args = parser.parse_args()
    home, base = args.home.resolve(strict=True), args.output.resolve()
    if base.exists() or not args.codex or args.repetitions != 2:
        parser.error('Use a new output directory, an installed CLI and two balanced repetitions')
    if home == Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).resolve():
        parser.error('Use an isolated test home, not your normal Codex home')
    cases_path = Path(__file__).resolve().parents[1] / 'examples/paired-cases.json'
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    schedule = plan(cases, args.repetitions, args.seed)
    base.mkdir(parents=True)
    protocol = {'design': 'targeted pilot; six tasks x two repeats x on/off = 24 model turns',
                'model': args.model, 'effort': 'medium', 'web_search': 'disabled',
                'seed': args.seed, 'cases_sha256': hashlib.sha256(cases_path.read_bytes()).hexdigest(),
                'schedule': schedule, 'workers': 2,
                'review': 'masked output IDs then AI rubric review; not independent human evaluation',
                'primary_measures': ['numeric long-dash ranges in generated prose',
                                     'claim calibration and source fidelity per task rubric'],
                'secondary_measures': ['task fulfillment', 'unnecessary disagreement/procedure',
                                       'output length', 'elapsed time', 'token counts when exposed'],
                'analysis': 'report each task, all ties/regressions/missing outputs; no total quality score or population effect claim'}
    (base / 'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    (base / 'frozen-cases.json').write_bytes(cases_path.read_bytes())
    env = dict(os.environ, CODEX_HOME=str(home), KNOWTETHER_CONTROLLED_EVAL='1', PYTHONUTF8='1')
    lookup = {c['id']: c for c in cases}

    def pair_run(pair):
        results = []
        for enabled in pair['order']:
            case = dict(lookup[pair['case']])
            case['id'] = f"{pair['case']}-r{pair['repetition']}-{'on' if enabled else 'off'}"
            result = run_case(args.codex, base, case, args.model, env=env, enabled=enabled)
            results.append(result)
            print(json.dumps({'completed': case['id'], 'characters': result['output_characters'],
                              'seconds': result['elapsed_seconds']}), flush=True)
        return results

    failures, completed = [], []
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = {pool.submit(pair_run, pair): pair for pair in schedule}
        for future in as_completed(jobs):
            try:
                completed.extend(future.result())
            except Exception as exc:
                failure = {'pair': jobs[future], 'error': str(exc)}
                failures.append(failure)
                print(json.dumps({'failed': failure}), flush=True)
            (base / 'progress.json').write_text(json.dumps({'completed': completed, 'failures': failures}, indent=2), encoding='utf-8')
    if failures:
        raise SystemExit('Some pairs failed; preserve every attempt and inspect progress.json')
    print(json.dumps({'completed_turns': len(completed), 'pairs': len(schedule)}), flush=True)


if __name__ == '__main__':
    main()
