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
    files = git('ls-tree', '-r', '--name-only', 'HEAD').decode('utf-8').splitlines()
    roots = ('.codex-plugin/', 'assets/', 'hooks/', 'kpdm_hooks/', 'skills/', 'docs/', 'policy/', 'examples/')
    names = {'README.md', 'README.en.md', 'LICENSE', 'NOTICE', 'SECURITY.md', 'CONTRIBUTING.md', 'CHANGELOG.md'}
    included = [name for name in files if name in names or name.startswith(roots)]
    with zipfile.ZipFile(plugin, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in included:
            archive.writestr('knowtether/' + name, git('show', 'HEAD:' + name))
    with zipfile.ZipFile(plugin) as archive:
        entries = archive.namelist()
        required = ('.codex-plugin/plugin.json', 'hooks/hooks.json',
                    'hooks/plugin_entry.py', 'kpdm_hooks/hooks.py', 'skills/knowtether/SKILL.md',
                    'assets/knowtether.svg', 'docs/codex-plugin.md')
        assert all('knowtether/' + name in entries for name in required)
        assert all('/.agents/' not in name and '/.kpdm/' not in name and '/.venv/' not in name for name in entries)
        metadata = json.loads(archive.read('knowtether/.codex-plugin/plugin.json'))
        assert metadata['name'] == 'knowtether' and metadata['version'] == version
    sums = output / ('v' + version) / 'SHA256SUMS'
    sums.parent.mkdir(exist_ok=True)
    with sums.open('w', encoding='ascii', newline='\n') as stream:
        for artifact in (plugin, wheel, source):
            stream.write(hashlib.sha256(artifact.read_bytes()).hexdigest() + '  ' + artifact.name + '\n')
    print(json.dumps({'version': version, 'plugin_files': len(included),
                      'artifacts': [plugin.name, wheel.name, source.name, sums.name]}))


if __name__ == '__main__':
    main()
