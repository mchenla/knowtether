"""Install using real Codex commands in a NEW isolated home; never change the user's setup."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


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
        for name in ('.codex-plugin', 'assets', 'hooks', 'kpdm_hooks', 'skills', 'docs', 'policy'):
            shutil.copytree(workspace / name, bundle / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('plugin.json', 'README.md', 'README.en.md', 'LICENSE', 'NOTICE', 'SECURITY.md'):
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
    expected_version = json.loads((workspace / 'plugin.json').read_text(encoding='utf-8'))['version']
    assert install['pluginId'] == 'knowtether@knowtether'
    assert install['version'] == expected_version
    assert any(item['pluginId'] == 'knowtether@knowtether' and item['enabled'] is True
               and item['version'] == expected_version for item in listing['installed'])
    installed = Path(install['installedPath']).resolve(strict=True)
    cache = (codex_home / 'plugins/cache').resolve(strict=True)
    assert cache in installed.parents, 'Installation must remain in the isolated cache'
    assert (installed / 'skills/knowtether/SKILL.md').is_file()
    hooks = json.loads((installed / 'hooks/codex-hooks.json').read_text(encoding='utf-8'))
    project = home / 'creative-project'
    project.mkdir()
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
        records.append({'event': event, 'response': response, 'exit_code': result.returncode})
    assert list(project.iterdir()) == [], 'Hooks must not create project files'
    (home / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'installed': True, 'version': expected_version, 'skill_found': True, 'hook_commands_checked': 3,
                      'source': args.source, 'trust_modified': False,
                      'note': 'Isolated install and command execution; no model turn or global configuration changed.'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
