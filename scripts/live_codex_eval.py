"""Opt-in live Codex tasks: callbacks + original outputs, not an automatic quality grade.

Uses the current authenticated Codex configuration and incurs model usage. Requires
an already installed/trusted plugin. Does not grant trust or alter configuration.
Records no reasoning items. Keep output outside the public repository.
"""
import argparse
import json
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def run_case(codex, base, case, model):
    target = base / case['id']
    project = target / 'project'
    project.mkdir(parents=True)
    (target / 'input.json').write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding='utf-8')
    process = subprocess.Popen([codex, 'app-server'], cwd=project, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               text=True, encoding='utf-8')
    messages = queue.Queue()
    records, finals = [], []
    output = (target / 'events.jsonl').open('w', encoding='utf-8')

    def reader():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass

    threading.Thread(target=reader, daemon=True).start()

    def receive(timeout=45):
        message = messages.get(timeout=timeout)
        method = message.get('method')
        item = message.get('params', {}).get('item', {})
        if (method in ('hook/started', 'hook/completed', 'turn/completed', 'error')
                or method == 'item/completed' and item.get('type') != 'reasoning'):
            records.append(message)
            output.write(json.dumps(message, ensure_ascii=False) + '\n')
            output.flush()
        if method == 'item/completed' and item.get('type') == 'agentMessage':
            if item.get('phase') in (None, 'final_answer'):
                finals.append(item['text'])
        if 'id' in message and method:
            process.stdin.write(json.dumps({'id': message['id'], 'error': {
                'code': -32601, 'message': 'No interactive approvals or external writes in this evaluation'}}) + '\n')
            process.stdin.flush()
        return message

    def call(number, method, params):
        process.stdin.write(json.dumps({'id': number, 'method': method, 'params': params}) + '\n')
        process.stdin.flush()
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                message = receive()
            except queue.Empty:
                continue
            if message.get('id') == number and 'method' not in message:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message['result']
        raise TimeoutError('App-server request timed out')

    try:
        call(1, 'initialize', {'clientInfo': {'name': 'knowtether-live-eval', 'version': '1'},
                               'capabilities': {'experimentalApi': True}})
        listing = call(2, 'hooks/list', {'cwds': [str(project)]})
        hooks = [h for h in listing['data'][0]['hooks'] if h.get('pluginId') == 'knowtether@knowtether']
        if len(hooks) != 3 or not all(h['enabled'] and h['trustStatus'] == 'trusted' for h in hooks):
            raise RuntimeError('Install and review/trust the three hooks in Codex first')
        thread = call(3, 'thread/start', {'cwd': str(project), 'sandbox': 'read-only',
                      'approvalPolicy': 'never', 'ephemeral': True, 'model': model,
                      'config': {'web_search': case['web_search']}})['thread']['id']
        call(4, 'turn/start', {'threadId': thread, 'effort': 'medium',
                             'input': [{'type': 'text', 'text': case['prompt']}]})
        deadline = time.monotonic() + 900
        while time.monotonic() < deadline:
            try:
                message = receive()
            except queue.Empty:
                print(json.dumps({'case': case['id'], 'status': 'working'}), flush=True)
                continue
            if message.get('method') == 'turn/completed':
                if message['params']['turn']['status'] != 'completed':
                    raise RuntimeError(message['params']['turn'])
                break
        else:
            raise TimeoutError('Model turn exceeded 15 minutes')
        article = '\n\n'.join(finals)
        (target / 'output.md').write_text(article, encoding='utf-8')
        runs = [r['params']['run'] for r in records if r.get('method') == 'hook/completed'
                and r['params']['run'].get('statusMessage', '').startswith('KnowTether:')]
        packed = json.dumps([r for r in runs if r['eventName'] == 'userPromptSubmit'], ensure_ascii=False)
        result = {'case': case['id'], 'model': model, 'effort': 'medium',
                  'thread_id': thread, 'output_characters': len(article),
                  'hook_events': [{'event': r['eventName'], 'status': r['status']} for r in runs],
                  'reading_pack_complete': 'MINIMUM_READING ready' in packed and 'MINIMUM_READING end' in packed,
                  'project_files': [str(f.relative_to(project)) for f in project.rglob('*') if f.is_file()],
                  'semantic_grade': 'not-automatically-assessed'}
        (target / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        if ({r['eventName'] for r in runs} != {'sessionStart', 'userPromptSubmit', 'stop'}
                or not all(r['status'] == 'completed' for r in runs)
                or not result['reading_pack_complete'] or not article):
            raise RuntimeError('Lifecycle, minimum pack or final output missing; inspect saved records')
        return result
    finally:
        output.close()
        process.terminate()
        process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', default=shutil.which('codex'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model', default='gpt-6.1-sol')
    parser.add_argument('--case', action='append', help='Run only these case ids')
    args = parser.parse_args()
    if not args.codex or args.output.exists():
        parser.error('A Codex executable and a new output directory are required')
    cases = json.loads((Path(__file__).resolve().parents[1] / 'examples/live-cases.json').read_text(encoding='utf-8'))
    selected = [c for c in cases if not args.case or c['id'] in args.case]
    if not selected or args.case and set(args.case) - {c['id'] for c in selected}:
        parser.error('Unknown case id')
    args.output.mkdir(parents=True)
    for case in selected:
        print(json.dumps(run_case(args.codex, args.output, case, args.model)), flush=True)


if __name__ == '__main__':
    main()
