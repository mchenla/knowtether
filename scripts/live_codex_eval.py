"""Opt-in live Codex tasks: callbacks + original outputs, not an automatic quality grade.

Uses the current authenticated Codex configuration and incurs model usage. Requires
an already installed/trusted plugin. Does not grant trust or alter configuration.
Records no reasoning items. Keep output outside the public repository.
"""
import argparse
import hashlib
import json
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def run_case(codex, base, case, model, *, env=None, enabled=True):
    target = base / case['id']
    project = target / 'project'
    project.mkdir(parents=True)
    provided = {}
    for name, content in case.get('materials', {}).items():
        path = (project / name).resolve()
        if project.resolve() not in path.parents:
            raise ValueError('Material path escapes the project')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='\n')
        provided[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (target / 'input.json').write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding='utf-8')
    started = time.monotonic()
    override = 'plugins."knowtether@knowtether".enabled=' + str(enabled).lower()
    process = subprocess.Popen([codex, '-c', override, 'app-server'], cwd=project, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               text=True, encoding='utf-8')
    messages = queue.Queue()
    records, finals = [], []
    milestones = {}
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
        if (method in ('hook/started', 'hook/completed', 'turn/completed', 'error', 'thread/tokenUsage/updated')
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
        milestones['initialized_seconds'] = round(time.monotonic()-started, 3)
        listing = call(2, 'hooks/list', {'cwds': [str(project)]})
        hooks = [h for h in listing['data'][0]['hooks'] if h.get('pluginId') == 'knowtether@knowtether']
        if enabled and (len(hooks) != 3 or not all(h['enabled'] and h['trustStatus'] == 'trusted' for h in hooks)):
            raise RuntimeError('Install and review/trust the three hooks in Codex first')
        if not enabled and any(h['enabled'] for h in hooks):
            raise RuntimeError('Control condition still has active plugin hooks')
        skills_result = call(20, 'skills/list', {'cwds': [str(project)], 'forceReload': True})
        skills = [s for row in skills_result['data'] for s in row['skills']
                  if s.get('enabled', True) and (s.get('pluginId') == 'knowtether@knowtether'
                     or s.get('name') in ('knowtether', 'knowtether:knowtether'))]
        if not enabled and skills:
            raise RuntimeError('Plugin skill condition does not match requested on/off state')
        if env is not None and env.get('KNOWTETHER_CONTROLLED_EVAL') == '1':
            others = [h for row in listing['data'] for h in row['hooks']
                      if h.get('enabled') and h.get('pluginId') != 'knowtether@knowtether']
            if others:
                raise RuntimeError('Other active hooks would confound this controlled evaluation')
        output.write(json.dumps({'condition_inventory': {'enabled': enabled, 'hook_count': len(hooks),
                                  'active_knowtether_skills': len(skills)}}, ensure_ascii=False) + '\n')
        output.flush()
        milestones['inventory_seconds'] = round(time.monotonic()-started, 3)
        thread = call(3, 'thread/start', {'cwd': str(project), 'sandbox': 'read-only',
                      'approvalPolicy': 'never', 'ephemeral': True, 'model': model,
                      'config': {'web_search': case['web_search']}})['thread']['id']
        milestones['thread_started_seconds'] = round(time.monotonic()-started, 3)
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
        milestones['turn_complete_seconds'] = round(time.monotonic()-started, 3)
        (target / 'output.md').write_text(article, encoding='utf-8')
        runs = [r['params']['run'] for r in records if r.get('method') == 'hook/completed'
                and r['params']['run'].get('statusMessage', '').startswith('KnowTether:')]
        packed = json.dumps([r for r in runs if r['eventName'] == 'userPromptSubmit'], ensure_ascii=False)
        light = '[KnowTether LIGHT]' in packed
        contexts = [e['text'] for r in runs for e in r['entries'] if e['kind'] == 'context']
        result = {'case': case['id'], 'model': model, 'effort': 'medium',
                  'thread_id': thread, 'output_characters': len(article),
                  'hook_events': [{'event': r['eventName'], 'status': r['status']} for r in runs],
                  'reading_pack_complete': 'MINIMUM_READING ready' in packed and 'MINIMUM_READING end' in packed,
                  'guidance_mode': 'light' if light else ('focused' if 'ROUTE' in packed else 'full'),
                  'context_characters': sum(len(t) for t in contexts),
                  'plugin_enabled': enabled, 'active_knowtether_skills': len(skills),
                  'elapsed_seconds': round(time.monotonic() - started, 3),
                  'timing': dict(milestones,
                      hook_milliseconds=sum(r.get('durationMs',0) for r in runs),
                      tool_milliseconds=sum(r['params']['item'].get('durationMs',0) or 0 for r in records if r.get('method')=='item/completed' and r['params']['item']['type']=='commandExecution')),
                  'tool_items': [r['params']['item']['type'] for r in records
                                 if r.get('method') == 'item/completed'
                                 and r['params']['item']['type'] not in ('userMessage', 'agentMessage')],
                  'token_usage': next((r['params'].get('tokenUsage') for r in reversed(records)
                                       if r.get('method') == 'thread/tokenUsage/updated'), None),
                  'provided_files_sha256': provided,
                  'materials_unchanged': all(hashlib.sha256((project/n).read_bytes()).hexdigest()==h for n,h in provided.items()),
                  'project_files': [str(f.relative_to(project)) for f in project.rglob('*')
                                    if f.is_file() and str(f.relative_to(project)) not in provided],
                  'semantic_grade': 'not-automatically-assessed'}
        (target / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        if enabled and ({r['eventName'] for r in runs} != {'sessionStart', 'userPromptSubmit', 'stop'}
                or not all(r['status'] == 'completed' for r in runs)
                or not (result['reading_pack_complete'] or light) or not article):
            raise RuntimeError('Lifecycle, minimum pack or final output missing; inspect saved records')
        if not enabled and (runs or result['reading_pack_complete'] or not article):
            raise RuntimeError('Control received plugin callbacks/context or has no output')
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
    # app-server resolves cwd relative to its own process cwd. Passing a relative
    # output path here otherwise repeats its parent segments in thread/start.
    args.output = args.output.resolve()
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
