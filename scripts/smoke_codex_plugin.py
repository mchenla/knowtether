"""Install using real Codex commands in a NEW isolated home; never change the user's setup."""
import argparse
import json
import os
import queue
import threading
from pathlib import Path
import shutil
import subprocess
import sys


def discover_hooks(codex, env, project):
    """Ask the actual host to load hooks; executing commands alone misses manifests."""
    process = subprocess.Popen([codex, 'app-server'], env=env, cwd=project,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, encoding='utf-8')
    messages = queue.Queue()

    def read_messages():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass
    threading.Thread(target=read_messages, daemon=True).start()

    def call(request_id, method, params):
        process.stdin.write(json.dumps({'id': request_id, 'method': method, 'params': params}) + '\n')
        process.stdin.flush()
        while True:
            message = messages.get(timeout=45)
            if message.get('id') == request_id:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message['result']
    try:
        call(1, 'initialize', {'clientInfo': {'name': 'knowtether-install-check', 'version': '1'},
                               'capabilities': {'experimentalApi': True}})
        return call(2, 'hooks/list', {'cwds': [str(project)]})
    finally:
        process.terminate()
        process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path, help='New test directory, must not exist')
    parser.add_argument('--source', default='local', help='local snapshot or a public owner/repo source')
    parser.add_argument('--codex', default=shutil.which('codex'))
    args = parser.parse_args()
    if not args.codex:
        parser.error('Codex CLI is required')
    workspace = Path(__file__).resolve().parents[1]
    home = args.home.resolve()
    if home.exists():
        parser.error('Use a new directory; existing data is never overwritten')
    home.mkdir(parents=True)
    codex_home = home / 'codex-home'
    codex_home.mkdir()
    env = dict(os.environ, CODEX_HOME=str(codex_home))
    source = args.source
    if source == 'local':
        market = home / 'fixture-market'
        bundle = market / 'plugins/knowtether'
        bundle.mkdir(parents=True)
        for name in ('.codex-plugin', 'assets', 'hooks', 'kpdm_hooks', 'skills', 'docs', 'policy', 'framework'):
            shutil.copytree(workspace / name, bundle / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('README.md', 'README.en.md', 'LICENSE', 'LICENSING.md', 'NOTICE', 'SECURITY.md'):
            shutil.copyfile(workspace / name, bundle / name)
        catalog = json.loads((workspace / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        catalog['plugins'][0]['source'] = {'source': 'local', 'path': './plugins/knowtether'}
        path = market / '.agents/plugins/marketplace.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(catalog, ensure_ascii=False), encoding='utf-8')
        source = str(market)
    commands = [
        ['plugin', 'marketplace', 'add', source, '--json'],
        ['plugin', 'add', 'knowtether@knowtether', '--json'],
        ['plugin', 'list', '--marketplace', 'knowtether', '--json'],
    ]
    records = []
    for command in commands:
        result = subprocess.run([args.codex, *command], env=env, text=True, encoding='utf-8',
                                capture_output=True, cwd=home, timeout=180)
        records.append({'command': command, 'exit_code': result.returncode,
                        'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            (home / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
            print(result.stderr or result.stdout, file=sys.stderr)
            return result.returncode
    install = json.loads(records[1]['stdout'])
    listing = json.loads(records[2]['stdout'])
    expected_version = json.loads((workspace / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    assert install['pluginId'] == 'knowtether@knowtether'
    assert install['version'] == expected_version
    assert any(item['pluginId'] == 'knowtether@knowtether' and item['enabled'] is True
               and item['version'] == expected_version for item in listing['installed'])
    installed = Path(install['installedPath']).resolve(strict=True)
    cache = (codex_home / 'plugins/cache').resolve(strict=True)
    assert cache in installed.parents, 'Installation must remain in the isolated cache'
    assert (installed / 'skills/knowtether/SKILL.md').is_file()
    assert (installed / 'framework/kpdm/README.md').is_file()
    assert (installed / 'framework/kpdm/LICENSE').is_file()
    assert (installed / 'framework/kpdm/spec/00 Start/快速入门.md').is_file()
    assert (installed / 'framework/kpdm/spec/04 Templates/轻量工作单模板.md').is_file()
    hooks = json.loads((installed / 'hooks/hooks.json').read_text(encoding='utf-8'))
    project = home / 'creative-project'
    project.mkdir()
    discovered = discover_hooks(args.codex, env, project)
    records.append({'host_hook_discovery': discovered})
    (home / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = discovered['data']
    assert len(rows) == 1 and not rows[0]['errors'], discovered
    found = [item for item in rows[0]['hooks'] if 'knowtether@knowtether:' in item['key']]
    assert {item['eventName'] for item in found} == {'sessionStart', 'userPromptSubmit', 'stop'}, discovered
    for event in ('SessionStart', 'UserPromptSubmit', 'Stop'):
        payload = {'hook_event_name': event, 'cwd': str(project), 'session_id': 'smoke',
                   'prompt': '[kpdm] Write a research article',
                   'last_assistant_message': 'Research report: explain knowledge [citation needed]'}
        handler = hooks['hooks'][event][0]['hooks'][0]
        hook_env = dict(env, PLUGIN_ROOT=str(installed))
        if os.name == 'nt':
            argv = [os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/s', '/c', handler['commandWindows']]
        else:
            argv = ['/bin/sh', '-c', handler['command']]
        result = subprocess.run(argv, input=json.dumps(payload), text=True, encoding='utf-8',
                                capture_output=True, env=hook_env, cwd=project, timeout=20)
        response = json.loads(result.stdout)
        assert result.returncode == 0, result.stderr
        if event == 'Stop':
            assert set(response) == {'systemMessage'}, response
            assert 'CITATION_PLACEHOLDER' in response['systemMessage'], response
        else:
            assert response['hookSpecificOutput']['hookEventName'] == event, response
            if event == 'UserPromptSubmit':
                context = response['hookSpecificOutput']['additionalContext']
                assert 'MINIMUM_READING ready' in context and 'MINIMUM_READING end' in context
                assert '## 六项约束' in context and 'MECE' in context
        records.append({'event': event, 'response': response, 'exit_code': result.returncode})
    assert list(project.iterdir()) == [], 'Hooks must not create project files'
    (home / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'installed': True, 'version': expected_version, 'skill_found': True, 'framework_found': True, 'host_hooks_discovered': 3, 'hook_commands_checked': 3,
                      'source': args.source, 'trust_modified': False,
                      'note': 'Isolated install, host discovery and command execution; no model turn or global configuration changed.'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
