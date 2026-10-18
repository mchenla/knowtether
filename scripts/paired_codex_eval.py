"""Run a preregistered on/off pilot in an ALREADY prepared isolated Codex home.

Does not install, authorize, copy credentials, change trust or score semantics.
Temporarily changes only the isolated plugin flag, serially, and restores it.
Creates fresh read-only projects. CLI per-process overrides switch the entire
plugin together with the isolated config flag, not merely project hook output.
All attempts, outputs and timing remain.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil

from live_codex_eval import run_case


def switch_config(text, enabled):
    """Change one isolated plugin flag, leaving every other line unchanged."""
    pattern = r'(?ms)(^\[plugins\."knowtether@knowtether"\][ \t]*\n)(.*?)(?=^\[|\Z)'
    def replace(match):
        body, count = re.subn(r'(?m)^enabled[ \t]*=[ \t]*(?:true|false)[ \t]*$',
                              'enabled = ' + str(enabled).lower(), match.group(2))
        if count != 1:
            raise ValueError('Expected exactly one isolated plugin flag')
        return match.group(1) + body
    result, count = re.subn(pattern, replace, text)
    if count != 1:
        raise ValueError('Expected exactly one isolated plugin section')
    return result


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
                'schedule': schedule, 'workers': 1,
                'switch': 'isolated config file flag plus matching CLI override; serialized to avoid races',
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
            config_path.write_text(switch_config(original_config, enabled), encoding='utf-8', newline='\n')
            case = dict(lookup[pair['case']])
            case['id'] = f"{pair['case']}-r{pair['repetition']}-{'on' if enabled else 'off'}"
            result = run_case(args.codex, base, case, args.model, env=env, enabled=enabled)
            results.append(result)
            print(json.dumps({'completed': case['id'], 'characters': result['output_characters'],
                              'seconds': result['elapsed_seconds']}), flush=True)
        return results

    failures, completed = [], []
    config_path = home / 'config.toml'
    original_config = config_path.read_text(encoding='utf-8')
    try:
        for pair in schedule:
            try:
                completed.extend(pair_run(pair))
            except Exception as exc:
                failure = {'pair': pair, 'error': str(exc)}
                failures.append(failure)
                print(json.dumps({'failed': failure}), flush=True)
            (base / 'progress.json').write_text(json.dumps({'completed': completed, 'failures': failures}, indent=2), encoding='utf-8')
            if failures:
                break  # Stop at the first invalid pair; do not waste or contaminate later tasks.
    finally:
        config_path.write_text(original_config, encoding='utf-8', newline='\n')
    if failures:
        raise SystemExit('Some pairs failed; preserve every attempt and inspect progress.json')
    print(json.dumps({'completed_turns': len(completed), 'pairs': len(schedule)}), flush=True)


if __name__ == '__main__':
    main()
