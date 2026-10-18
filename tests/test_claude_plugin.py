import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from kpdm_hooks import __version__
from kpdm_hooks.hooks import handle
from kpdm_hooks.install import configure

REPO = Path(__file__).resolve().parents[1]
COMMANDS = ('start', 'research', 'draft', 'check', 'release', 'handoff', 'adopt')
AGENTS = ('verifier', 'researcher', 'reader-sim')


def front_matter(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise AssertionError(f'{path} has no front matter')
    block = text.split('---\n', 2)[1]
    return dict(line.split(':', 1) for line in block.splitlines() if line and not line.startswith(' '))


class ClaudeManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((REPO / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))

    def test_manifest_matches_codex_identity_and_version(self):
        codex = json.loads((REPO / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(self.manifest['name'], 'knowtether')
        self.assertEqual(self.manifest['version'], __version__)
        for key in ('homepage', 'repository', 'license'):
            self.assertEqual(self.manifest[key], codex[key])

    def test_component_paths_stay_inside_the_repository(self):
        for relative in [self.manifest['skills'], *self.manifest['agents']]:
            self.assertTrue(relative.startswith('./'), relative)
            target = (REPO / relative).resolve(strict=True)
            self.assertIn(REPO, target.parents)

    def test_marketplace_installs_this_repository_root(self):
        market = json.loads((REPO / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
        self.assertEqual(market['name'], 'knowtether')
        self.assertEqual([entry['name'] for entry in market['plugins']], ['knowtether'])
        self.assertEqual(market['plugins'][0]['source'], './')

    def test_claude_only_commands_are_outside_the_codex_skill_scan(self):
        codex_skills = {path.parent.name for path in (REPO / 'skills').glob('*/SKILL.md')}
        self.assertTrue(codex_skills.isdisjoint(COMMANDS))
        for name in COMMANDS:
            meta = front_matter(REPO / 'claude/skills' / name / 'SKILL.md')
            self.assertEqual(meta['name'].strip(), name)
            self.assertTrue(meta['description'].strip())
        for name in AGENTS:
            meta = front_matter(REPO / 'claude/agents' / (name + '.md'))
            self.assertEqual(meta['name'].strip(), name)

    def test_referenced_bundle_files_exist(self):
        pattern = re.compile(r'\$\{CLAUDE_PLUGIN_ROOT\}/([^`\s<]+?\.(?:py|md))')
        for path in (REPO / 'claude').rglob('*.md'):
            for relative in pattern.findall(path.read_text(encoding='utf-8')):
                if '<lang>' in relative:
                    continue
                self.assertTrue((REPO / relative).is_file(), f'{path}: {relative}')
        for lang in ('en', 'zh-CN'):
            for name in ('worksheet.md', 'knowledge-overview.md', 'handoff.md'):
                self.assertTrue((REPO / 'claude/templates' / lang / name).is_file())

    def test_adapted_templates_carry_cc_by_notice(self):
        notice = (REPO / 'claude/templates/README.md').read_text(encoding='utf-8')
        self.assertIn('CC BY 4.0', notice)
        self.assertIn('Changes:', notice)
        self.assertIn('claude/templates', (REPO / 'LICENSING.md').read_text(encoding='utf-8'))


class ClaudeHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix='claude-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @unittest.skipIf(os.name == 'nt', 'POSIX shell expansion')
    def test_shared_hook_command_resolves_claude_plugin_root(self):
        manifest = json.loads((REPO / 'hooks/hooks.json').read_text(encoding='utf-8'))
        command = manifest['hooks']['SessionStart'][0]['hooks'][0]['command']
        env = {k: v for k, v in os.environ.items() if k != 'PLUGIN_ROOT'}
        env['CLAUDE_PLUGIN_ROOT'] = str(REPO)
        event = json.dumps({'hook_event_name': 'SessionStart', 'cwd': str(self.root)})
        result = subprocess.run(['/bin/sh', '-c', command], input=event, text=True, encoding='utf-8',
                                capture_output=True, env=env, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('hookSpecificOutput', json.loads(result.stdout))

    def test_plugin_yields_to_claude_project_install_only_under_claude(self):
        configure(self.root, 'claude')
        event = {'hook_event_name': 'SessionStart', 'cwd': str(self.root)}
        self.assertEqual(handle(event, self.root, 'SessionStart', plugin=True, host='claude'), {})
        self.assertIn('hookSpecificOutput', handle(event, self.root, 'SessionStart', plugin=True, host='codex'))

    def test_entry_detects_claude_from_environment(self):
        configure(self.root, 'claude')
        env = {k: v for k, v in os.environ.items() if k != 'PLUGIN_ROOT'}
        event = json.dumps({'hook_event_name': 'SessionStart', 'cwd': str(self.root)})
        argv = [sys.executable, '-B', str(REPO / 'hooks/plugin_entry.py'), 'SessionStart']
        env['CLAUDE_PLUGIN_ROOT'] = str(REPO)
        claude = subprocess.run(argv, input=event, text=True, encoding='utf-8', capture_output=True, env=env, timeout=15)
        self.assertEqual(json.loads(claude.stdout), {})
        env['PLUGIN_ROOT'] = str(REPO)
        codex = subprocess.run(argv, input=event, text=True, encoding='utf-8', capture_output=True, env=env, timeout=15)
        self.assertIn('hookSpecificOutput', json.loads(codex.stdout))


if __name__ == '__main__':
    unittest.main()
