"""Pure advisory rules. Record consistency is not semantic verification."""
from __future__ import annotations

import json
from pathlib import Path
import re

from . import __version__

MAX_BYTES = 1_000_000
POLICY_VERSION = "0.5.0-rc.2"
FIELDS = ("intent", "central_idea", "expression_structure", "evidence_and_scope",
          "delegation", "acceptance", "results_and_revisions", "human_decision")
BASELINE = "0.4.0 trial / conditional-pass"


def finding(code: str, message: str, severity: str = "warning") -> dict:
    return {"code": code, "severity": severity, "message": message}


def present(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _label(value: str) -> str:
    """Bound untrusted identifiers and render control characters as data."""
    return json.dumps(value[:64], ensure_ascii=False)


def safe_path(root: Path, relative: str) -> Path:
    """Read only project-contained paths, resolving traversal and symlinks."""
    root = root.resolve(strict=True)
    path = (root / relative).resolve()
    if path == root or root not in path.parents:
        raise ValueError("Path must resolve to a file inside the project")
    return path


def read_text(path: Path) -> str:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Input exceeds 1 MB")
    return raw.decode("utf-8-sig")


def read_object(path: Path) -> dict:
    obj = json.loads(read_text(path))
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object")
    return obj


def load_work(root: Path) -> dict | None:
    path = safe_path(root, ".kpdm/work.json")
    return read_object(path) if path.exists() else None


def knowledge_prompt(text: str) -> bool:
    if not isinstance(text, str):
        return False
    if "[kpdm]" in text.lower():
        return True
    # Intent hints only; ambiguous requests still receive the conditional session guidance.
    action = r"写|编写|制作|准备|修订|撰写|写一|写篇|起草|改写|审阅|写作|解释|研究|分析|比较|综述|论证|探讨|梳理|总结|科普|write|draft|revise|review|explain|research|compare|summarize|analyse|analyze"
    product = r"文章|报告|概念|理论|知识|读者|论文|观点|学习|文献|PPT|汇报|文档|书籍|工具书|章节|出版|article|report|concept|theory|literature|essay|knowledge|slide|chapter|book"
    return bool(re.search(action, text, re.I) and re.search(product, text, re.I))


def context() -> str:
    return (
        f"KnowTether {__version__}: advisory, knowledge writing only; ordinary code is outside scope. 知识任务按复杂度提供指导："
        "短任务直接处理；复杂研究、报告、PPT和书籍仅读相关KPDM原文选段。"
        "不要为简单任务打开Skill；已有选段够用时不重复读。遵循当前授权，"
        "不编来源、不随用户期待评价，缺证不等于证伪。完整工作流可主动调用知据Skill。"
        "KPDM 0.5.0-rc.2 candidate；接受基线0.4.0 trial / conditional-pass。提醒不构成质量认证。"
    )


def lint_text(text: str) -> list[dict]:
    """Small, deliberately conservative heuristics; never assert truth or falsity."""
    notes = []
    # Code examples should not trigger prose-style findings.
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    if re.search(r'[\u200b\ufeff\u2060\u202a-\u202e]', prose):
        notes.append(finding('INVISIBLE_CHARACTERS', '发现零宽或双向控制字符；检查是否为正常排版、书写方向或意外残留。它不证明存在技术水印，不自动删除。'))
    if re.search(r'您的(?:想法|观点|判断)[^。\n]{0,24}(?:高瞻远瞩|极具洞察|无疑[^。\n]{0,8}突破)', prose):
        notes.append(finding('EVALUATIVE_PRAISE', '发现对用户观点的评价性赞语；核对具体判据和依据，避免以肯定替代判断。仅措辞提示，未判定是否谄媚。'))
    if re.search(r"\d+(?:\.\d+)?[ \t]*[—–]+[ \t]*\d+(?:\.\d+)?", prose):
        notes.append(finding("NUMERIC_RANGE_DASH", "发现数字之间的长破折号；若表示中文正文区间，改用带空格的短横线，如1 - 2天。公式与直接引文须保持含义及原文；本提示不自动改文。"))
    if re.search(r"\[citation needed\]|\[待补来源\]|\[来源待补\]|<SOURCE_TODO>", prose, re.I):
        notes.append(finding("CITATION_PLACEHOLDER", "引用占位尚未替换；补充真实且支持相关主张的来源，或明确保留未知。"))
    if re.search(r"(?:研究证明|科学证明|studies prove|research proves)[^。\n.!?]{0,80}(?:100%|百分之百|必然|always)", prose, re.I):
        notes.append(finding("ABSOLUTE_CLAIM", "发现强结论表达；请核对原始研究、适用条件、反例及不确定性。此提示未判定结论真假。"))
    if re.search(r"已通过独立验证|经过独立验证|independently validated|independently verified", prose, re.I):
        notes.append(finding("STATUS_LANGUAGE", "独立验证表述需核对验证者、对象、范围、版本和记录；文字扫描无法证明验证已发生。"))
    words = re.findall(r"赋能|底座|抓手|闭环|颗粒度|认知升级|范式跃迁", prose)
    if len(words) >= 4 and len(set(words)) >= 3:
        notes.append(finding("LANGUAGE_PATTERN", "抽象套语较集中；检查是否可改成具体的人、动作和结果。它们不是禁词。"))
    return notes


def _record(record, version) -> bool:
    return (isinstance(record, dict) and present(version)
            and record.get("version") == version and present(record.get("evidence_ref")))


def check_work(state: dict, session_id: str | None = None) -> list[dict]:
    if not isinstance(state, dict):
        return [finding("STATE_FORMAT", "工作单必须是JSON对象。", "error")]
    if state.get("enabled") is False:
        return []
    if session_id is not None and state.get("session_id") != session_id:
        return [finding("HANDOFF", "工作单属于另一会话；仅作历史资料，核对当前委托后使用bind，勿继承旧授权。")]
    if state.get("schema_version") != 1 or state.get("mode", "warn") != "warn":
        return [finding("STATE_FORMAT", "仅支持schema_version=1且mode=warn的工作单。", "error")]
    notes = []
    if state.get("policy_version") != POLICY_VERSION:
        notes.append(finding("POLICY_VERSION", "工作单继承版本与本适配不同，需核对规则来源；不会自动升级。"))
    ws = state.get("worksheet", {})
    if not isinstance(ws, dict):
        return notes + [finding("STATE_FORMAT", "worksheet必须是对象。", "error")]
    missing = [key for key in FIELDS[:6] if not present(ws.get(key))]
    if not present(state.get("input_version")):
        missing.append("input_version")
    if missing:
        notes.append(finding("WORKSHEET_GAPS", "起草/交接信息待补：" + ", ".join(missing) + "；未知可如实记录。"))
    missing = [key for key in FIELDS[6:] if not present(ws.get(key))]
    if missing:
        notes.append(finding("END_RECORD", "结束记录待补：" + ", ".join(missing) + "；人的决定尚无则写待定。"))
    if not isinstance(state.get("open_issues", []), list):
        notes.append(finding("STATE_FORMAT", "open_issues必须是列表。", "error"))
    elif state.get("open_issues"):
        notes.append(finding("OPEN_ISSUES", "仍有开放问题；交付时说明其影响和后续处理。"))
    required = {"draft": (), "author_accepted": ("author_acceptance",),
                "independently_verified": ("independent_validation",),
                "release_approved": ("author_acceptance", "independent_validation", "release_decision")}
    status = state.get("status", "draft")
    if not isinstance(status, str) or status not in required:
        notes.append(finding("STATUS_UNKNOWN", "无法识别成果状态，不能据此声称已接受或可发布。"))
    else:
        for key in required[status]:
            if not _record(state.get(key), state.get("artifact_version")):
                notes.append(finding("STATUS_EVIDENCE", key + "缺少当前版本对应的evidence_ref记录。"))
    sources = state.get("sources", [])
    claims = state.get("claims", [])
    if not isinstance(sources, list) or not isinstance(claims, list):
        return notes + [finding("STATE_FORMAT", "sources与claims必须是列表。", "error")]
    source_ids = set()
    for source in sources:
        if not isinstance(source, dict) or not present(source.get("id")):
            notes.append(finding("SOURCE_FORMAT", "来源记录需有非空id。", "error"))
            continue
        if source["id"] in source_ids:
            notes.append(finding("SOURCE_FORMAT", "来源id重复：" + _label(source["id"]), "error"))
        source_ids.add(source["id"])
        if not present(source.get("locator")):
            notes.append(finding("SOURCE_LOCATOR", _label(source["id"]) + "缺少可定位的原文位置。"))
        if source.get("verification") != "human-verified":
            notes.append(finding("SOURCE_UNVERIFIED", _label(source["id"]) + "尚无人工核验记录；链接存在不等于支持主张。"))
        rights = source.get("rights_status")
        if not present(rights) or rights.strip().lower() in ("unknown", "blocked-unknown-rights"):
            notes.append(finding("SOURCE_RIGHTS", _label(source["id"]) + "权利状态未明确；引用和复制/改编许可需分别判断。"))
    for claim in claims:
        if not isinstance(claim, dict) or not present(claim.get("id")):
            notes.append(finding("CLAIM_FORMAT", "主张记录需有非空id。", "error"))
            continue
        refs = claim.get("source_ids", [])
        valid_refs = isinstance(refs, list) and all(present(ref) for ref in refs)
        factual = claim.get("type") in ("fact", "data", "quote", "cause")
        if not valid_refs or (factual and not refs) or (valid_refs and any(ref not in source_ids for ref in refs)):
            notes.append(finding("CLAIM_SOURCE", _label(claim["id"]) + "需有可解析的来源关联；关联存在仍需核对是否支持主张。"))
        if factual and not present(claim.get("support_note")):
            notes.append(finding("CLAIM_SUPPORT", _label(claim["id"]) + "尚未说明来源中哪一部分支持此主张。"))
    publication = state.get("publication", {})
    if not isinstance(publication, dict):
        notes.append(finding("STATE_FORMAT", "publication必须是对象。", "error"))
    elif publication.get("usage") == "public":
        if publication.get("q_target") not in ("Q3", "Q4"):
            notes.append(finding("PUBLIC_Q", "公开知识成果的质量目标至少Q3。"))
        if not _record(publication.get("reader_validation"), state.get("artifact_version")):
            notes.append(finding("PUBLIC_REVIEW", "公开成果需真实目标读者或独立编辑执行预设任务并留下对应版本记录。"))
        if not _record(state.get("independent_validation"), state.get("artifact_version")):
            notes.append(finding("PUBLIC_INDEPENDENT", "公开成果的高影响主张需独立复核记录，或明确标为尚未验证。"))
    return notes


def check_project(root: Path, artifact: str | None = None, session_id: str | None = None) -> list[dict]:
    notes = []
    state = load_work(root)
    if state is not None:
        notes.extend(check_work(state, session_id))
    elif artifact is None:
        notes.append(finding("NO_WORK", "未找到工作单；可用init创建，轻任务也可仅对指定文本做启发式检查。"))
    if artifact is not None:
        notes.extend(lint_text(read_text(safe_path(root, artifact))))
    return notes
