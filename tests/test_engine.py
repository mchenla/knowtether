"""Rule and filesystem boundary tests; passing these is not KPDM validation."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from kpdm_hooks.engine import (
    check_project,
    check_work,
    context,
    knowledge_prompt,
    lint_text,
    load_work,
)


WORKSHEET_FIELDS = (
    "intent", "central_idea", "expression_structure", "evidence_and_scope",
    "delegation", "acceptance", "results_and_revisions", "human_decision",
)


def work() -> dict:
    """A complete record fixture, not a claim that its contents were verified."""
    return {
        "schema_version": 1,
        "enabled": True,
        "mode": "warn",
        "policy_version": "0.5.0-rc.2",
        "session_id": "current-session",
        "input_version": "input-1",
        "artifact_version": "draft-1",
        "status": "draft",
        "worksheet": {field: "未知" for field in WORKSHEET_FIELDS},
        "open_issues": [],
        "sources": [],
        "claims": [],
        "publication": {"usage": "internal", "q_target": "Q1"},
    }


def record(version: str = "draft-1") -> dict:
    return {"version": version, "evidence_ref": "review-record.md#decision-1"}


def source() -> dict:
    return {
        "id": "s1",
        "locator": "https://example.org/source#section-2",
        "verification": "human-verified",
        "rights_status": "permitted",
    }


def claim(kind: str = "fact") -> dict:
    return {
        "id": "c1",
        "type": kind,
        "source_ids": ["s1"],
        "support_note": "Section 2 gives the observation; scope is limited to this sample.",
    }


def codes(findings: list[dict]) -> set[str]:
    return {item["code"] for item in findings}


class PromptAndTextTests(unittest.TestCase):
    def test_knowledge_requests_and_explicit_marker(self):
        for text in ("请写一篇知识文章", "Explain the theory for a new reader", "[KPDM] 整理资料"):
            with self.subTest(text=text):
                self.assertTrue(knowledge_prompt(text))

    def test_obvious_non_knowledge_requests_do_not_opt_in(self):
        for text in ("Fix this Python syntax error", "登录我的账户", "", None):
            with self.subTest(text=text):
                self.assertFalse(knowledge_prompt(text))

    def test_context_keeps_candidate_and_baseline_distinct(self):
        guidance = context()
        self.assertIn("0.5.0-rc.2 candidate", guidance)
        self.assertIn("0.4.0 trial / conditional-pass", guidance)
        self.assertIn("advisory", guidance.lower())

    def test_citation_placeholders_in_both_languages(self):
        for text in ("A claim [citation needed].", "数据如下[待补来源]。"):
            with self.subTest(text=text):
                self.assertIn("CITATION_PLACEHOLDER", codes(lint_text(text)))

    def test_absolute_research_claim_is_only_a_review_signal(self):
        self.assertIn("ABSOLUTE_CLAIM", codes(lint_text("研究证明该方案100%有效。")))
        self.assertNotIn("ABSOLUTE_CLAIM", codes(lint_text("研究报告只覆盖一个样本，结论仍有不确定性。")))

    def test_independent_validation_language_needs_records(self):
        self.assertIn("STATUS_LANGUAGE", codes(lint_text("该成果已经过独立验证。")))

    def test_fenced_examples_are_not_linted_as_prose(self):
        text = "示例代码：\n```text\n[citation needed]\n研究证明100%有效\nindependently validated\n```\n请核对资料。"
        self.assertEqual([], lint_text(text))

    def test_style_hint_needs_a_cluster_and_words_are_not_banned(self):
        self.assertNotIn("LANGUAGE_PATTERN", codes(lint_text("用数据说明这个概念，赋能在此有具体定义。")))
        self.assertIn("LANGUAGE_PATTERN", codes(lint_text("赋能底座抓手闭环颗粒度认知升级")))

    def test_findings_have_a_stable_reviewable_shape(self):
        findings = lint_text("研究证明100%有效 [待补来源]。")
        self.assertTrue(findings)
        for item in findings:
            self.assertIsInstance(item["code"], str)
            self.assertIn(item["severity"], ("warning", "error", "info"))
            self.assertTrue(item["message"].strip())


class WorksheetTests(unittest.TestCase):
    def test_unknown_is_a_legitimate_explicit_answer(self):
        actual = codes(check_work(work()))
        self.assertNotIn("WORKSHEET_GAPS", actual)
        self.assertNotIn("END_RECORD", actual)

    def test_not_applicable_with_reason_is_accepted(self):
        state = work()
        state["worksheet"]["central_idea"] = "主张未定：本任务只探索问题。"
        state["worksheet"]["expression_structure"] = "不适用：本轮只形成来源清单。"
        self.assertNotIn("WORKSHEET_GAPS", codes(check_work(state)))

    def test_initial_and_end_records_are_reported_separately(self):
        state = work()
        state["worksheet"]["intent"] = "  "
        state["worksheet"]["human_decision"] = ""
        actual = codes(check_work(state))
        self.assertIn("WORKSHEET_GAPS", actual)
        self.assertIn("END_RECORD", actual)

    def test_missing_input_version_is_a_handoff_gap(self):
        state = work()
        state.pop("input_version")
        self.assertIn("WORKSHEET_GAPS", codes(check_work(state)))

    def test_open_issues_remain_visible(self):
        state = work()
        state["open_issues"] = ["Real reader task has not been run."]
        self.assertIn("OPEN_ISSUES", codes(check_work(state)))

    def test_old_session_has_only_handoff_and_no_inherited_authority(self):
        state = work()
        state["status"] = "release_approved"
        state["worksheet"] = {}
        self.assertEqual({"HANDOFF"}, codes(check_work(state, "new-session")))

    def test_manual_check_does_not_require_session_binding(self):
        state = work()
        state["session_id"] = "old-session"
        state["worksheet"]["intent"] = ""
        actual = codes(check_work(state))
        self.assertNotIn("HANDOFF", actual)
        self.assertIn("WORKSHEET_GAPS", actual)

    def test_current_session_runs_record_checks(self):
        state = work()
        state["worksheet"]["intent"] = ""
        self.assertIn("WORKSHEET_GAPS", codes(check_work(state, "current-session")))

    def test_disabled_work_is_not_active(self):
        state = work()
        state["enabled"] = False
        state["worksheet"] = {}
        self.assertEqual([], check_work(state, "another-session"))

    def test_bad_state_shape_is_reported(self):
        for state in ([], {"schema_version": 99}, {**work(), "worksheet": []},
                      {**work(), "open_issues": "not-a-list"},
                      {**work(), "sources": "not-a-list"},
                      {**work(), "claims": {}}, {**work(), "publication": []}):
            with self.subTest(state=state):
                self.assertIn("STATE_FORMAT", codes(check_work(state)))

    def test_policy_mismatch_is_not_silently_upgraded(self):
        state = work()
        state["policy_version"] = "0.4.0"
        self.assertIn("POLICY_VERSION", codes(check_work(state)))
        self.assertEqual("0.4.0", state["policy_version"])

    def test_checker_does_not_mutate_work(self):
        state = work()
        state["open_issues"] = ["Need original source"]
        state["status"] = "release_approved"
        before = deepcopy(state)
        check_work(state)
        self.assertEqual(before, state)


class StatusTests(unittest.TestCase):
    def test_unknown_status_cannot_imply_approval(self):
        for status in ("complete", "official", None, ["release_approved"]):
            with self.subTest(status=status):
                state = work()
                state["status"] = status
                self.assertIn("STATUS_UNKNOWN", codes(check_work(state)))

    def test_author_acceptance_needs_current_version_and_evidence(self):
        for approval in (None, {}, record("draft-0"), {"version": "draft-1", "evidence_ref": " "}):
            with self.subTest(approval=approval):
                state = work()
                state["status"] = "author_accepted"
                state["author_acceptance"] = approval
                self.assertIn("STATUS_EVIDENCE", codes(check_work(state)))

    def test_acceptance_record_is_not_a_release_decision(self):
        state = work()
        state["status"] = "release_approved"
        state["author_acceptance"] = record()
        findings = [item for item in check_work(state) if item["code"] == "STATUS_EVIDENCE"]
        self.assertEqual(2, len(findings))
        self.assertEqual("release_approved", state["status"])

    def test_all_release_record_references_must_match_artifact(self):
        state = work()
        state["status"] = "release_approved"
        for key in ("author_acceptance", "independent_validation", "release_decision"):
            state[key] = record()
        self.assertNotIn("STATUS_EVIDENCE", codes(check_work(state)))
        state["artifact_version"] = "draft-2"
        self.assertEqual(3, sum(item["code"] == "STATUS_EVIDENCE" for item in check_work(state)))

    def test_independent_record_is_a_different_requirement(self):
        state = work()
        state["status"] = "independently_verified"
        state["author_acceptance"] = record()
        self.assertIn("STATUS_EVIDENCE", codes(check_work(state)))
        state["independent_validation"] = record()
        self.assertNotIn("STATUS_EVIDENCE", codes(check_work(state)))


class SourceAndClaimTests(unittest.TestCase):
    def state_with_source_and_claim(self, kind: str = "fact") -> dict:
        state = work()
        state["sources"] = [source()]
        state["claims"] = [claim(kind)]
        return state

    def test_each_factual_claim_kind_requires_source_links(self):
        for kind in ("fact", "data", "quote", "cause"):
            with self.subTest(kind=kind):
                state = self.state_with_source_and_claim(kind)
                state["claims"][0]["source_ids"] = []
                self.assertIn("CLAIM_SOURCE", codes(check_work(state)))

    def test_source_links_must_resolve_and_have_valid_shape(self):
        for refs in (["missing"], "s1", [None], [{"id": "s1"}], [""]):
            with self.subTest(refs=refs):
                state = self.state_with_source_and_claim()
                state["claims"][0]["source_ids"] = refs
                self.assertIn("CLAIM_SOURCE", codes(check_work(state)))

    def test_hypotheses_do_not_require_external_fact_sources(self):
        state = work()
        state["claims"] = [{"id": "h1", "type": "hypothesis", "source_ids": []}]
        self.assertNotIn("CLAIM_SOURCE", codes(check_work(state)))

    def test_source_link_is_not_a_substitute_for_support_location(self):
        state = self.state_with_source_and_claim()
        state["claims"][0].pop("support_note")
        actual = codes(check_work(state))
        self.assertNotIn("CLAIM_SOURCE", actual)
        self.assertIn("CLAIM_SUPPORT", actual)

    def test_recorded_human_verification_is_distinct_from_a_url(self):
        state = self.state_with_source_and_claim()
        state["sources"][0]["verification"] = "link-accessible"
        self.assertIn("SOURCE_UNVERIFIED", codes(check_work(state)))
        state["sources"][0]["verification"] = "human-verified"
        self.assertNotIn("SOURCE_UNVERIFIED", codes(check_work(state)))

    def test_unknown_or_missing_rights_are_visible(self):
        for rights in (None, "", "unknown", "blocked-unknown-rights"):
            with self.subTest(rights=rights):
                state = self.state_with_source_and_claim()
                state["sources"][0]["rights_status"] = rights
                self.assertIn("SOURCE_RIGHTS", codes(check_work(state)))

    def test_missing_locator_and_duplicate_source_ids_are_reported(self):
        state = self.state_with_source_and_claim()
        state["sources"][0]["locator"] = ""
        state["sources"].append(source())
        actual = codes(check_work(state))
        self.assertIn("SOURCE_LOCATOR", actual)
        self.assertIn("SOURCE_FORMAT", actual)

    def test_invalid_source_or_claim_records_do_not_crash(self):
        state = work()
        state["sources"] = [None, {}, {"id": []}]
        state["claims"] = [None, {}, {"id": []}]
        actual = codes(check_work(state))
        self.assertIn("SOURCE_FORMAT", actual)
        self.assertIn("CLAIM_FORMAT", actual)


class PublicationTests(unittest.TestCase):
    def test_internal_draft_does_not_require_public_checks(self):
        actual = codes(check_work(work()))
        self.assertNotIn("PUBLIC_Q", actual)
        self.assertNotIn("PUBLIC_REVIEW", actual)
        self.assertNotIn("PUBLIC_INDEPENDENT", actual)

    def test_publication_below_q3_is_a_warning(self):
        state = work()
        state["publication"] = {"usage": "public", "q_target": "Q2"}
        actual = codes(check_work(state))
        self.assertIn("PUBLIC_Q", actual)
        self.assertIn("PUBLIC_REVIEW", actual)
        self.assertIn("PUBLIC_INDEPENDENT", actual)

    def test_q3_and_q4_are_targets_not_proof_of_reader_validation(self):
        for target in ("Q3", "Q4"):
            with self.subTest(target=target):
                state = work()
                state["publication"] = {"usage": "public", "q_target": target}
                actual = codes(check_work(state))
                self.assertNotIn("PUBLIC_Q", actual)
                self.assertIn("PUBLIC_REVIEW", actual)
                self.assertEqual("draft", state["status"])

    def test_reader_record_requires_current_version(self):
        state = work()
        state["publication"] = {"usage": "public", "q_target": "Q3", "reader_validation": record("draft-0")}
        state["independent_validation"] = record()
        self.assertIn("PUBLIC_REVIEW", codes(check_work(state)))
        state["publication"]["reader_validation"] = record()
        actual = codes(check_work(state))
        self.assertNotIn("PUBLIC_REVIEW", actual)
        self.assertNotIn("PUBLIC_INDEPENDENT", actual)
        self.assertEqual("draft", state["status"])


class ProjectReadTests(unittest.TestCase):
    def setUp(self):
        # Keep temporary fixtures beside the suite so restricted Windows test
        # runners do not rely on a writable system temp directory.
        self.temp = tempfile.TemporaryDirectory(prefix="kpdm-engine-test-", dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()

    def save_work(self, state: dict | None = None) -> Path:
        path = self.root / ".kpdm" / "work.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(state if state is not None else work()), encoding="utf-8")
        return path

    def test_missing_work_is_optional_for_explicit_artifact(self):
        self.assertIsNone(load_work(self.root))
        self.assertIn("NO_WORK", codes(check_project(self.root)))
        (self.root / "article.md").write_text("A draft [citation needed].", encoding="utf-8")
        actual = codes(check_project(self.root, "article.md"))
        self.assertIn("CITATION_PLACEHOLDER", actual)
        self.assertNotIn("NO_WORK", actual)

    def test_project_checks_combine_records_and_article_findings(self):
        state = work()
        state["open_issues"] = ["Review pending"]
        path = self.save_work(state)
        before = path.read_bytes()
        (self.root / "article.md").write_text("研究证明100%有效。", encoding="utf-8")
        actual = codes(check_project(self.root, "article.md", "current-session"))
        self.assertIn("OPEN_ISSUES", actual)
        self.assertIn("ABSOLUTE_CLAIM", actual)
        self.assertEqual(before, path.read_bytes())

    def test_utf8_bom_work_file_is_supported(self):
        path = self.save_work()
        path.write_text(json.dumps(work()), encoding="utf-8-sig")
        self.assertEqual("draft-1", load_work(self.root)["artifact_version"])

    def test_malformed_or_non_object_work_file_is_rejected(self):
        path = self.save_work()
        for text in ("{broken", "[]", '"not an object"'):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_work(self.root)

    def test_artifact_cannot_escape_project_with_parent_traversal(self):
        outside = self.base / "private.md"
        outside.write_text("Outside project", encoding="utf-8")
        with self.assertRaises(ValueError):
            check_project(self.root, "../private.md")

    def test_artifact_cannot_escape_project_with_absolute_path(self):
        outside = self.base / "private.md"
        outside.write_text("Outside project", encoding="utf-8")
        with self.assertRaises(ValueError):
            check_project(self.root, str(outside))

    def test_project_root_cannot_be_used_as_artifact(self):
        with self.assertRaises(ValueError):
            check_project(self.root, ".")

    def test_artifact_symlink_to_outside_is_rejected(self):
        outside = self.base / "private.md"
        outside.write_text("Outside project", encoding="utf-8")
        link = self.root / "linked.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        with self.assertRaises(ValueError):
            check_project(self.root, "linked.md")

    def test_work_directory_symlink_to_outside_is_rejected(self):
        outside = self.base / "external-state"
        outside.mkdir()
        (outside / "work.json").write_text(json.dumps(work()), encoding="utf-8")
        try:
            (self.root / ".kpdm").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        with self.assertRaises(ValueError):
            load_work(self.root)

    def test_oversized_artifact_is_rejected(self):
        path = self.root / "large.md"
        path.write_bytes(b"a" * 1_000_001)
        with self.assertRaises(ValueError):
            check_project(self.root, "large.md")


if __name__ == "__main__":
    unittest.main()
