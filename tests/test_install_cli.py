import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from kpdm_hooks.install import _ours, configure

REPO = Path(__file__).resolve().parents[1]


class InstallAndCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix="fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, "-m", "kpdm_hooks", *args, "--root", str(self.root)],
                              input=stdin, text=True, encoding="utf-8", capture_output=True,
                              cwd=REPO, timeout=15)

    def test_dry_run_has_no_filesystem_side_effects(self):
        result = configure(self.root, "codex", dry_run=True)
        self.assertTrue(result["changed"])
        self.assertFalse((self.root / ".codex").exists())
        self.assertFalse((self.root / ".kpdm").exists())

    def test_similar_third_party_markers_are_preserved(self):
        self.assertFalse(_ours({"command": "third-party --adapter-id kpdm-hooks-v10"}))
        self.assertFalse(_ours({"command": "third-party", "args": ["--adapter-id", "other", "--note", "kpdm-hooks-v1"]}))
        self.assertFalse(_ours({"command": "third-party --note 'contains --adapter-id kpdm-hooks-v1'"}))
        self.assertTrue(_ours({"command": "python -m kpdm_hooks hook '--adapter-id' 'kpdm-hooks-v1'"}))

    def test_merge_idempotency_backup_and_uninstall(self):
        for host, relative in (("codex", ".codex/hooks.json"), ("claude", ".claude/settings.local.json")):
            with self.subTest(host=host):
                path = self.root / relative
                path.parent.mkdir(parents=True)
                other = {"type": "command", "command": "echo keep-me"}
                original = {"other_setting": 42, "hooks": {"Stop": [{"matcher": "", "hooks": [other]}]}}
                path.write_text(json.dumps(original), encoding="utf-8")
                first = configure(self.root, host)
                self.assertEqual(json.loads(Path(first["backup"]).read_text()), original)
                installed = json.loads(path.read_text())
                self.assertEqual(installed["other_setting"], 42)
                self.assertEqual(installed["hooks"]["Stop"][0]["hooks"][0], other)
                second = configure(self.root, host)
                self.assertFalse(second["changed"])
                self.assertNotIn("backup", second)
                self.assertEqual(installed, json.loads(path.read_text()))
                configure(self.root, host, remove=True)
                self.assertEqual(json.loads(path.read_text()), original)

    def test_malformed_existing_settings_are_never_overwritten(self):
        path = self.root / ".codex/hooks.json"
        path.parent.mkdir()
        for raw in ("broken", '{"hooks":[]}', '{"hooks":{"Stop":[null]}}'):
            with self.subTest(raw=raw):
                path.write_text(raw, encoding="utf-8")
                with self.assertRaises(ValueError):
                    configure(self.root, "codex")
                self.assertEqual(path.read_text(), raw)
                self.assertFalse((self.root / ".kpdm").exists())

    def test_uninstall_survives_a_broken_adapter_config(self):
        configure(self.root, "codex")
        (self.root / ".kpdm/config.json").write_text("broken", encoding="utf-8")
        self.assertTrue(configure(self.root, "codex", remove=True)["changed"])
        self.assertEqual(json.loads((self.root / ".codex/hooks.json").read_text()), {})

    def test_rights_metadata_must_be_a_nonempty_string(self):
        from kpdm_hooks.engine import check_work
        for rights in ([], {}, "   ", " UNKNOWN ", "Blocked-Unknown-Rights"):
            state = {"schema_version": 1, "policy_version": "0.5.0-rc.2", "worksheet": {},
                     "sources": [{"id": "s1", "locator": "p1", "verification": "human-verified", "rights_status": rights}]}
            self.assertIn("SOURCE_RIGHTS", {item["code"] for item in check_work(state)})

    def test_untrusted_ids_have_bounded_single_line_diagnostics(self):
        from kpdm_hooks.engine import check_work
        state = {"schema_version": 1, "policy_version": "0.5.0-rc.2", "worksheet": {},
                 "sources": [{"id": "untrusted\n" + "x" * 10000}]}
        for item in check_work(state):
            self.assertLess(len(item["message"]), 500)
            self.assertNotIn("\n", item["message"])

    def test_cli_init_never_clobbers_work_and_bind_is_explicit(self):
        first = self.cli("init", "--session-id", "first")
        self.assertEqual(first.returncode, 0, first.stderr)
        path = self.root / ".kpdm/work.json"
        initial = path.read_bytes()
        self.assertEqual(self.cli("init", "--session-id", "second").returncode, 2)
        self.assertEqual(path.read_bytes(), initial)
        self.assertEqual(self.cli("bind", "--session-id", "second").returncode, 0)
        self.assertEqual(json.loads(path.read_text())["session_id"], "second")
        self.assertEqual(self.cli("close").returncode, 0)
        self.assertFalse(json.loads(path.read_text())["enabled"])

    def test_check_exit_codes_distinguish_findings_and_input_errors(self):
        path = self.root / "article.md"
        path.write_text("[citation needed]", encoding="utf-8")
        advisory = self.cli("check", "--artifact", "article.md")
        strict = self.cli("check", "--artifact", "article.md", "--strict")
        broken = self.cli("check", "--artifact", "missing.md", "--strict")
        self.assertEqual(advisory.returncode, 0)
        self.assertEqual(strict.returncode, 1)
        self.assertEqual(broken.returncode, 2)
        report = json.loads(strict.stdout)
        self.assertEqual(report["semantic_review"], "requires-human-review")
        self.assertEqual(report["release_approval"], "not-assessed")

    def test_hook_protocol_on_stdin_and_malformed_input_fails_open(self):
        configure(self.root, "codex")
        for raw in ("broken", "[]", json.dumps({"hook_event_name": "Stop"}), "x" * 1_000_001):
            result = self.cli("hook", "--event", "SessionStart", stdin=raw)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("CHECK_SKIPPED", json.loads(result.stdout)["systemMessage"])
        result = self.cli("hook", "--event", "SessionStart", stdin=json.dumps({"hook_event_name": "SessionStart", "session_id": "test"}))
        self.assertEqual(result.returncode, 0)
        self.assertIn("additionalContext", json.loads(result.stdout)["hookSpecificOutput"])

    def test_generated_claude_exec_handler_runs_without_shell(self):
        configure(self.root, "claude")
        settings = json.loads((self.root / ".claude/settings.local.json").read_text())
        handler = settings["hooks"]["SessionStart"][0]["hooks"][0]
        result = subprocess.run([handler["command"], *handler["args"]],
                                input='{"hook_event_name":"SessionStart","session_id":"test"}',
                                text=True, encoding="utf-8", capture_output=True, cwd=self.root, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["hookEventName"], "SessionStart")

    @unittest.skipUnless(os.name == "nt", "Windows shell integration")
    def test_generated_codex_command_runs_in_powershell(self):
        configure(self.root, "codex")
        settings = json.loads((self.root / ".codex/hooks.json").read_text())
        handler = settings["hooks"]["SessionStart"][0]["hooks"][0]
        pwsh = shutil.which("pwsh") or shutil.which("powershell")
        if not pwsh:
            self.skipTest("PowerShell unavailable")
        result = subprocess.run([pwsh, "-NoProfile", "-Command", handler["command"]],
                                input='{"hook_event_name":"SessionStart","session_id":"test"}',
                                text=True, encoding="utf-8", capture_output=True, cwd=self.root, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("additionalContext", json.loads(result.stdout)["hookSpecificOutput"])

    @unittest.skipUnless(os.name == "nt", "Windows cmd fallback integration")
    def test_generated_codex_command_runs_in_cmd_fallback(self):
        configure(self.root, "codex")
        settings = json.loads((self.root / ".codex/hooks.json").read_text())
        handler = settings["hooks"]["SessionStart"][0]["hooks"][0]
        result = subprocess.run([os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", handler["command"]],
                                input='{"hook_event_name":"SessionStart","session_id":"test"}',
                                text=True, encoding="utf-8", capture_output=True, cwd=self.root, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("additionalContext", json.loads(result.stdout)["hookSpecificOutput"])


if __name__ == "__main__":
    unittest.main()
