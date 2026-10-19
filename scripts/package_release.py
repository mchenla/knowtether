"""Package only committed public files; keep plugin ZIP free of marketplace wrappers."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def main():
    repo = Path(__file__).resolve().parents[1]

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo)

    if git('status', '--porcelain', '--untracked-files=no').strip():
        raise SystemExit('Commit tracked changes before packaging a release')
    version = json.loads(git('show', 'HEAD:.codex-plugin/plugin.json'))['version']
    output = repo / 'dist'
    output.mkdir(exist_ok=True)
    wheel = output / ('kpdm_hooks-' + version + '-py3-none-any.whl')
    if not wheel.is_file():
        raise SystemExit('Build the matching Python wheel before packaging')
    source = output / ('knowtether-' + version + '-source.zip')
    subprocess.run(['git', 'archive', '--format=zip', '--prefix=knowtether-' + version + '/',
                    '--output=' + str(source), 'HEAD'], cwd=repo, check=True)
    plugin = output / ('knowtether-' + version + '-plugin.zip')
    files = [name for name in git('ls-tree', '-r', '-z', '--name-only', 'HEAD').decode('utf-8').split('\0') if name]
    roots = ('.codex-plugin/', 'claude/', 'assets/', 'hooks/', 'kpdm_hooks/', 'skills/', 'docs/', 'policy/', 'examples/', 'framework/')
    names = {'.claude-plugin/plugin.json', 'README.md', 'README.en.md', 'LICENSE', 'LICENSING.md', 'NOTICE', 'SECURITY.md', 'CONTRIBUTING.md', 'CHANGELOG.md'}
    included = [name for name in files if name in names or name.startswith(roots)]
    with zipfile.ZipFile(plugin, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in included:
            archive.writestr('knowtether/' + name, git('show', 'HEAD:' + name))
    with zipfile.ZipFile(plugin) as archive:
        entries = archive.namelist()
        required = ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json',
                    'claude/skills/release/SKILL.md', 'claude/agents/verifier.md',
                    'claude/scripts/fingerprint_check.py', 'claude/templates/README.md', 'hooks/hooks.json',
                    'hooks/plugin_entry.py', 'kpdm_hooks/hooks.py', 'skills/knowtether/SKILL.md',
                    'assets/knowtether.svg', 'docs/codex-plugin.md',
                    'framework/kpdm/README.md', 'framework/kpdm/LICENSE', 'framework/kpdm/snapshot.json', 'LICENSING.md')
        assert all('knowtether/' + name in entries for name in required)
        assert all('/.agents/' not in name and '/.kpdm/' not in name and '/.venv/' not in name for name in entries)
        snapshot = json.loads(archive.read('knowtether/framework/kpdm/snapshot.json'))
        for document in snapshot['documents']:
            data = archive.read('knowtether/framework/kpdm/' + document['path'])
            assert hashlib.sha256(data).hexdigest() == document['published_sha256'], document['path']
        metadata = json.loads(archive.read('knowtether/.codex-plugin/plugin.json'))
        assert metadata['name'] == 'knowtether' and metadata['version'] == version
        claude = json.loads(archive.read('knowtether/.claude-plugin/plugin.json'))
        assert claude['name'] == metadata['name'] and claude['version'] == version
        assert 'knowtether/.claude-plugin/marketplace.json' not in entries
        for relative in [claude['skills'], *claude['agents']]:
            prefix = 'knowtether/' + relative.removeprefix('./').rstrip('/')
            assert any(n == prefix or n.startswith(prefix + '/') for n in entries), relative
    framework = output / 'kpdm-0.5.0-rc.2-public-snapshot.zip'
    with zipfile.ZipFile(framework, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            if name.startswith('framework/kpdm/'):
                archive.writestr('kpdm/' + name.removeprefix('framework/kpdm/'), git('show', 'HEAD:' + name))
    with zipfile.ZipFile(framework) as archive:
        assert 'kpdm/LICENSE' in archive.namelist() and 'kpdm/spec/README.md' in archive.namelist()
        snapshot = json.loads(archive.read('kpdm/snapshot.json'))
        for document in snapshot['documents']:
            assert hashlib.sha256(archive.read('kpdm/' + document['path'])).hexdigest() == document['published_sha256']
    with zipfile.ZipFile(wheel) as archive:
        assert not any(name.startswith('framework/') for name in archive.namelist())
    sums = output / ('v' + version) / 'SHA256SUMS'
    sums.parent.mkdir(exist_ok=True)
    with sums.open('w', encoding='ascii', newline='\n') as stream:
        for artifact in (plugin, wheel, source, framework):
            stream.write(hashlib.sha256(artifact.read_bytes()).hexdigest() + '  ' + artifact.name + '\n')
    print(json.dumps({'version': version, 'plugin_files': len(included),
                      'artifacts': [plugin.name, wheel.name, source.name, framework.name, sums.name]}))


if __name__ == '__main__':
    main()
