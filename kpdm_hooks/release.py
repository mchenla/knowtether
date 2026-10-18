"""Explicit release gate. Blocks on five record and text rules; hooks never call it.

The gate checks records and the final text mechanically. It cannot tell whether a
record is truthful or whether a cited source supports a claim; people still check that.
"""
from __future__ import annotations

from pathlib import Path
import re

from . import __version__
from .engine import _label, _record, finding, load_work, present, read_text, safe_path

RULES = ("RELEASE_SOURCE", "RELEASE_PLACEHOLDER", "RELEASE_RIGHTS",
         "RELEASE_ACCEPTANCE", "RELEASE_WORKFLOW_LABEL")
FACTUAL = ("fact", "data", "quote", "cause")
UNKNOWN_RIGHTS = {"unknown", "blocked-unknown-rights", "pending", "tbd", "未知", "待定", "待确认"}
# Upper-case TODO/TBD only, so ordinary prose such as "a todo list" passes.
# ASCII boundaries: Python's \b sees no boundary between Chinese text and TODO.
PLACEHOLDER = re.compile(
    r"(?i:\[citation needed\])|<SOURCE_TODO>|(?<![A-Za-z0-9_])(?:TODO|TBD)(?![A-Za-z0-9_])"
    r"|[\[【（(]\s*(?:待补[^\]】）)\n]{0,10}|来源待补|待核实|待核对|(?i:source\?))\s*[\]】）)]")
WORKFLOW_LABEL = re.compile(
    r"候选发布版|候选版本|内部探讨参考|仅供内部(?:讨论|参考|审阅)|内部草稿|供[^。，,\n]{1,12}审阅"
    r"|(?<![A-Za-z0-9_])(?:DRAFT|WIP)(?![A-Za-z0-9_])|(?i:candidate release|for internal review|work in progress|not for distribution)")
LIMITS = ("Checks records and final text only. It cannot detect facts that were never registered "
          "as claims, false records, or sources that do not support a claim; people still check those.")


def _without_code(text: str) -> str:
    """Blank fenced code but keep line numbers stable."""
    return re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def _hits(pattern: re.Pattern, text: str) -> list[str]:
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        for match in pattern.finditer(line):
            found.append(f"L{number} {_label(match.group(0))}")
    return found


def _source_rule(state: dict) -> list[dict]:
    claims, sources = state.get("claims"), state.get("sources", [])
    if not isinstance(claims, list) or not isinstance(sources, list):
        return [finding("RELEASE_SOURCE", "claims与sources必须是列表；发布前需登记成品中的主张。", "error")]
    by_id = {s["id"]: s for s in sources if isinstance(s, dict) and present(s.get("id"))}
    factual = [c for c in claims if isinstance(c, dict) and c.get("type") in FACTUAL]
    publication = state.get("publication") if isinstance(state.get("publication"), dict) else {}
    if not factual and publication.get("external_facts") != "none":
        return [finding("RELEASE_SOURCE", "没有登记任何事实、数据、引文或因果主张。若成品确实不含外部事实，"
                        "由人在publication.external_facts写\"none\"；否则先登记主张与来源。", "error")]
    notes = []
    for claim in factual:
        name = _label(str(claim.get("id", "?")))
        refs = claim.get("source_ids")
        if not isinstance(refs, list) or not refs:
            notes.append(finding("RELEASE_SOURCE", name + "没有登记来源。", "error"))
            continue
        if not present(claim.get("support_note")):
            notes.append(finding("RELEASE_SOURCE", name + "没有说明来源中哪一部分支持它。", "error"))
        for ref in refs:
            source = by_id.get(ref) if isinstance(ref, str) else None
            if source is None:
                notes.append(finding("RELEASE_SOURCE", name + "引用的来源" + _label(str(ref)) + "不存在。", "error"))
                continue
            if not present(source.get("locator")):
                notes.append(finding("RELEASE_SOURCE", _label(ref) + "缺少原文位置。", "error"))
            if source.get("verification") != "human-verified":
                notes.append(finding("RELEASE_SOURCE", _label(ref) + "未标记为human-verified（人已核对原文）。", "error"))
    return notes


def _rights_rule(state: dict) -> list[dict]:
    notes = []
    for source in state.get("sources", []) if isinstance(state.get("sources"), list) else []:
        if not isinstance(source, dict):
            continue
        rights = source.get("rights_status")
        if not present(rights) or rights.strip().lower() in UNKNOWN_RIGHTS:
            notes.append(finding("RELEASE_RIGHTS", _label(str(source.get("id", "?"))) + "权利状态未知或未填写。", "error"))
    return notes


def _acceptance_rule(state: dict) -> list[dict]:
    version = state.get("artifact_version")
    if not present(version):
        return [finding("RELEASE_ACCEPTANCE", "artifact_version为空，无法对应人接受的版本。", "error")]
    if not _record(state.get("author_acceptance"), version):
        return [finding("RELEASE_ACCEPTANCE", "缺少人对版本" + _label(version) + "的接受记录"
                        "（author_acceptance需含相同version与evidence_ref）。", "error")]
    return []


def release_gate(root: Path, artifact: str) -> dict:
    """Return a pass/fail verdict. Every listed finding blocks release."""
    text = _without_code(read_text(safe_path(root, artifact)))
    blocking = []
    state = load_work(root)
    if state is None or state.get("schema_version") != 1:
        blocking.append(finding("RELEASE_SOURCE", "未找到schema_version=1的.kpdm/work.json；"
                                "没有主张、来源和接受记录就无法判定可发布。", "error"))
        blocking.append(finding("RELEASE_ACCEPTANCE", "没有工作单，也就没有人对具体版本的接受记录。", "error"))
    else:
        blocking += _source_rule(state) + _rights_rule(state) + _acceptance_rule(state)
    placeholders = _hits(PLACEHOLDER, text)
    if placeholders:
        blocking.append(finding("RELEASE_PLACEHOLDER", "成品仍有引用或内容占位：" + "；".join(placeholders[:20]), "error"))
    labels = _hits(WORKFLOW_LABEL, text)
    if labels:
        blocking.append(finding("RELEASE_WORKFLOW_LABEL", "成品含工作流标签：" + "；".join(labels[:20]), "error"))
    return {"gate": "release", "tool_version": __version__, "artifact": artifact,
            "artifact_version": state.get("artifact_version") if isinstance(state, dict) else None,
            "verdict": "fail" if blocking else "pass", "rules": list(RULES),
            "blocking": blocking, "limits": LIMITS}
