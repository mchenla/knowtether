import base64
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from kpdm_hooks import __version__
from kpdm_hooks.hooks import EVENTS, handle
from kpdm_hooks.install import configure

REPO = Path(__file__).resolve().parents[1]


class PluginPackageTests(unittest.TestCase):
    def test_marketplace_points_to_the_existing_repository(self):
        market = json.loads((REPO / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        self.assertEqual(market['name'], 'knowtether')
        self.assertEqual(len(market['plugins']), 1)
        entry = market['plugins'][0]
        self.assertEqual(entry['name'], 'knowtether')
        self.assertEqual(entry['source'], {'source': 'url', 'url': 'https://github.com/mchenla/knowtether.git', 'ref': 'main'})

    def test_manifests_share_identity_metadata_and_contained_components(self):
        portable = json.loads((REPO / 'plugin.json').read_text(encoding='utf-8'))
        legacy = json.loads((REPO / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(portable['$schema'], 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json')
        for key in ('name', 'version', 'description', 'author', 'license', 'repository'):
            self.assertEqual(portable[key], legacy[key])
        self.assertEqual(portable['version'], __version__)
        extension = portable['extensions']['com.openai']
        self.assertEqual(extension['interface'], legacy['interface'])
        self.assertEqual(extension['hooks'], legacy['hooks'])
        self.assertLessEqual(len(extension['interface']['shortDescription']), 30)
        for relative in (legacy['hooks'], legacy['skills'], legacy['interface']['logo']):
            target = (REPO / relative).resolve(strict=True)
            self.assertIn(REPO, target.parents)
        skill = (REPO / 'skills/knowtether/SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(skill.startswith('---\nname: knowtether\n'))
        self.assertIn('0.5.0-rc.2 candidate', skill)
        self.assertIn('0.4.0 trial / conditional-pass', skill)
        for target in ('docs/rules.md', 'docs/codex-plugin.md', 'policy/source-map.json'):
            self.assertTrue((REPO / target).is_file())

    def test_hook_manifest_is_generated_and_never_requests_continuation(self):
        spec = importlib.util.spec_from_file_location('hook_builder', REPO / 'scripts/build_plugin_hooks.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        actual = json.loads((REPO / 'hooks/codex-hooks.json').read_text(encoding='utf-8'))
        self.assertEqual(actual, module.definition())
        self.assertEqual(set(actual['hooks']), set(EVENTS))
        for event, groups in actual['hooks'].items():
            handler = groups[0]['hooks'][0]
            self.assertEqual(handler['type'], 'command')
            self.assertIn('$PLUGIN_ROOT/hooks/run-posix.sh', handler['command'])
            encoded = handler['commandWindows'].split('-EncodedCommand ')[1]
            script = base64.b64decode(encoded).decode('utf-16le')
            self.assertIn("hooks/run-windows.ps1", script)
            self.assertIn("-Event '" + event + "'", script)
            self.assertNotIn('BypassHookTrust', script)
        self.assertNotIn('additionalContextLimit', actual['hooks']['Stop'][0]['hooks'][0])


class PluginRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix='plugin-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def invoke(self, event, expected='SessionStart'):
        return subprocess.run([sys.executable, '-B', str(REPO / 'hooks/plugin_entry.py'), expected],
                              input=json.dumps(event, ensure_ascii=False), text=True, encoding='utf-8',
                              capture_output=True, cwd=self.root, timeout=15)

    def test_plugin_needs_no_project_config_and_legacy_stays_opt_in(self):
        event = {'hook_event_name': 'SessionStart', 'cwd': str(self.root), 'session_id': 'new'}
        self.assertEqual(handle(event, self.root, 'SessionStart'), {})
        result = self.invoke(event)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('KnowTether', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_explicit_project_disable_is_respected(self):
        (self.root / '.kpdm').mkdir()
        (self.root / '.kpdm/config.json').write_text('{"schema_version":1,"enabled":false}')
        result = self.invoke({'hook_event_name': 'SessionStart', 'cwd': str(self.root)})
        self.assertEqual(json.loads(result.stdout), {})

    def test_plugin_yields_to_existing_project_registration_for_the_same_event(self):
        configure(self.root, 'codex')
        event = {'hook_event_name': 'SessionStart', 'cwd': str(self.root)}
        self.assertEqual(handle(event, self.root, 'SessionStart', plugin=True), {})
        self.assertIn('hookSpecificOutput', handle(event, self.root, 'SessionStart'))

    def test_unrelated_project_hooks_do_not_suppress_the_plugin(self):
        (self.root / '.codex').mkdir()
        (self.root / '.codex/hooks.json').write_text(json.dumps({'hooks': {'SessionStart': [{'hooks': [{'command': 'echo other'}]}]}}))
        result = self.invoke({'hook_event_name': 'SessionStart', 'cwd': str(self.root)})
        self.assertIn('hookSpecificOutput', json.loads(result.stdout))

    def test_invalid_event_and_working_directory_fail_open(self):
        cases = [[], {'hook_event_name': 'Stop', 'cwd': str(self.root)},
                 {'hook_event_name': 'SessionStart', 'cwd': '.'},
                 {'hook_event_name': 'SessionStart', 'cwd': str(self.root / 'absent')}]
        for event in cases:
            result = self.invoke(event)
            self.assertEqual(result.returncode, 0)
            self.assertIn('CHECK_SKIPPED', json.loads(result.stdout)['systemMessage'])

    def test_prompt_and_stop_contracts_work_without_installing_a_python_package(self):
        event = {'hook_event_name': 'UserPromptSubmit', 'cwd': str(self.root), 'prompt': '[kpdm] 写一篇文章'}
        self.assertIn('hookSpecificOutput', json.loads(self.invoke(event, 'UserPromptSubmit').stdout))
        event['prompt'] = 'Fix the unit test'
        self.assertEqual(json.loads(self.invoke(event, 'UserPromptSubmit').stdout), {})
        event.update(hook_event_name='Stop', last_assistant_message='研究报告解释知识：[citation needed]')
        response = json.loads(self.invoke(event, 'Stop').stdout)
        self.assertEqual(set(response), {'systemMessage'})
        self.assertIn('CITATION_PLACEHOLDER', response['systemMessage'])
        event['stop_hook_active'] = True
        self.assertEqual(json.loads(self.invoke(event, 'Stop').stdout), {})

    def test_project_data_is_read_from_event_cwd_not_process_cwd(self):
        project = self.root / 'project space 文稿'
        (project / '.kpdm').mkdir(parents=True)
        (project / '.kpdm/config.json').write_text('{"schema_version":1,"enabled":false}')
        result = self.invoke({'hook_event_name': 'SessionStart', 'cwd': str(project)})
        self.assertEqual(json.loads(result.stdout), {})

    @unittest.skipUnless(os.name == 'nt', 'Windows command override')
    def test_windows_override_with_real_environment_and_hostile_path_characters(self):
        bundle = self.root / "bundle space 文稿 O'Neil & $x %x%"
        bundle.mkdir()
        for name in ('hooks', 'kpdm_hooks'):
            shutil.copytree(REPO / name, bundle / name, ignore=shutil.ignore_patterns('__pycache__'))
        manifest = json.loads((REPO / 'hooks/codex-hooks.json').read_text(encoding='utf-8'))
        command = manifest['hooks']['SessionStart'][0]['hooks'][0]['commandWindows']
        env = dict(os.environ, PLUGIN_ROOT=str(bundle))
        event = json.dumps({'hook_event_name': 'SessionStart', 'cwd': str(self.root)})
        for shell in ('cmd', 'powershell'):
            if shell == 'cmd':
                argv = [os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/s', '/c', command]
            else:
                argv = [shutil.which('powershell'), '-NoProfile', '-Command', command]
            result = subprocess.run(argv, input=event, text=True, encoding='utf-8', capture_output=True, env=env, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('hookSpecificOutput', json.loads(result.stdout))
        self.assertFalse(list(bundle.rglob('__pycache__')))

    @unittest.skipIf(os.name == 'nt', 'POSIX launcher')
    def test_posix_launcher_with_and_without_python(self):
        env = dict(os.environ, PLUGIN_ROOT=str(REPO))
        event = json.dumps({'hook_event_name': 'SessionStart', 'cwd': str(self.root)})
        argv = ['/bin/sh', str(REPO / 'hooks/run-posix.sh'), 'SessionStart']
        result = subprocess.run(argv, input=event, text=True, encoding='utf-8', capture_output=True, env=env, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('hookSpecificOutput', json.loads(result.stdout))
        env['PATH'] = ''
        result = subprocess.run(argv, input=event, text=True, encoding='utf-8', capture_output=True, env=env, timeout=15)
        self.assertEqual(result.returncode, 0)
        self.assertIn('PYTHON_REQUIRED', json.loads(result.stdout)['systemMessage'])


if __name__ == '__main__':
    unittest.main()
