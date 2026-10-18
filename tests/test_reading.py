"""Reading evidence, failure honesty, bounded delivery and project isolation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from kpdm_hooks.hooks import handle
from kpdm_hooks.reading import MAX_CONTEXT_CHARS, SELECTION, prepare, reading_context

REPO = Path(__file__).resolve().parents[1]


class ReadingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix="reading-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def bundle(self):
        for relative in ("framework/kpdm/snapshot.json", "policy/collaboration.md",
                         *("framework/kpdm/" + name for name, _ in SELECTION)):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, target)
        return self.root

    def test_pack_passages_are_exact_and_locatable_not_invented_summaries(self):
        pack = prepare(REPO)
        self.assertEqual(pack["status"], "ready")
        self.assertEqual(len(pack["documents"]), 3)
        for doc in pack["documents"]:
            raw = (REPO / doc["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), doc["sha256"])
            lines = raw.decode("utf-8").splitlines(keepends=True)
            for section in doc["sections"]:
                self.assertEqual(section["text"], "".join(lines[section["first_line"] - 1:section["last_line"]]))
        self.assertEqual(pack["adaptation"]["text"], (REPO / "policy/collaboration.md").read_text(encoding="utf-8"))
        context = reading_context()
        self.assertLessEqual(len(context), MAX_CONTEXT_CHARS)
        self.assertIn("MINIMUM_READING end", context)
        self.assertIn("认知诚实与反迎合", context)
        self.assertIn("MECE", context)

    def test_changed_missing_and_oversize_files_never_report_ready(self):
        root = self.bundle()
        name = root / "framework/kpdm" / SELECTION[0][0]
        original = name.read_bytes()
        for raw in (b"truncated", b"x" * 100001, None):
            with self.subTest(raw=None if raw is None else len(raw)):
                if raw is None:
                    name.unlink()
                else:
                    name.write_bytes(raw)
                report = prepare(root)
                self.assertEqual(report["status"], "degraded")
                self.assertNotIn("documents", report)
                name.write_bytes(original)

    def test_changed_section_identity_and_missing_policy_degrade(self):
        root = self.bundle()
        with patch("kpdm_hooks.reading.SELECTION", ((SELECTION[0][0], ("not present",)),)):
            self.assertEqual(prepare(root)["status"], "degraded")
        (root / "policy/collaboration.md").unlink()
        self.assertEqual(prepare(root)["code"], "READING_UNAVAILABLE")

    def test_manifest_cannot_redirect_selected_read_to_project_data(self):
        root = self.bundle()
        path = root / "framework/kpdm/snapshot.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["documents"][0]["path"] = "../../secret.md"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(prepare(root)["status"], "degraded")

    def test_user_prompt_reads_before_generation_without_tags_or_writes(self):
        event = {"hook_event_name": "UserPromptSubmit", "prompt": "给研究生写一篇文献综述方法文章。"}
        result = handle(event, self.root, "UserPromptSubmit", plugin=True)
        text = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("MINIMUM_READING ready", text)
        self.assertIn("## 六项约束", text)
        self.assertEqual(list(self.root.iterdir()), [])
        event["prompt"] = "Fix the unit test"
        self.assertEqual(handle(event, self.root, "UserPromptSubmit", plugin=True), {})
        with patch("kpdm_hooks.reading.prepare", return_value={"status": "degraded", "message": "missing"}):
            event["prompt"] = "write a 1500 words knowledge article"
            text = handle(event, self.root, "UserPromptSubmit", plugin=True)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("READING_UNAVAILABLE", text)
            self.assertNotIn("ready", text)

    def test_cli_prepare_reads_bundle_not_current_directory(self):
        run = subprocess.run([sys.executable, "-B", str(REPO / "hooks/entry.py"), "prepare"],
                             cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=15)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["status"], "ready")
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
