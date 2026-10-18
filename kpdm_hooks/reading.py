"""Read a bounded, integrity-checked minimum pack from the installed bundle.

The receipt proves byte reads and delivery, never attention, compliance or truth.
No project files, transcripts, environment paths or network are consulted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MAX_FILE_BYTES = 100_000
MAX_CONTEXT_CHARS = 18_000
SELECTION = (
    ("spec/00 Start/快速入门.md", ("一、从一句话任务开始",)),
    ("spec/01 Foundations/KPDM 质量约束.md",
     ("六项约束", "模型语言指纹与文字温度", "认知诚实与反迎合", "状态主张与不得自证完成")),
    ("spec/02 Methods and Protocols/人机协作协议.md",
     ("总原则", "Agent 可以主动做的事", "必须返回人的情形", "禁止无复核委托")),
)


def _read(root: Path, relative: str) -> bytes:
    path = (root / relative).resolve(strict=True)
    if root not in path.parents or not path.is_file():
        raise ValueError("Bundle file is outside its root")
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("Bundle file exceeds reading limit")
    return raw


def _sections(raw: bytes, headings: tuple[str, ...]) -> list[dict]:
    lines = raw.decode("utf-8").splitlines(keepends=True)
    selected = []
    for heading in headings:
        starts = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == "## " + heading]
        if len(starts) != 1:
            raise ValueError("Expected section missing or ambiguous")
        start = starts[0]
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        selected.append({"heading": heading, "first_line": start + 1, "last_line": end,
                         "text": "".join(lines[start:end])})
    return selected


def prepare(bundle_root: Path | None = None) -> dict:
    """All-or-degraded: never describe a partial or mismatched pack as ready."""
    from . import __version__
    root = (bundle_root or Path(__file__).resolve().parents[1]).resolve()
    try:
        manifest = json.loads(_read(root, "framework/kpdm/snapshot.json"))
        if (manifest["reference_version"] != "0.5.0-rc.2"
                or manifest["reference_status"] != "candidate"):
            raise ValueError("Unsupported framework identity")
        entries = manifest["documents"]
        documents = []
        for relative, headings in SELECTION:
            matches = [item for item in entries if item["path"] == relative]
            if len(matches) != 1:
                raise ValueError("Snapshot entry missing or ambiguous")
            name = "framework/kpdm/" + relative
            raw = _read(root, name)
            digest = hashlib.sha256(raw).hexdigest()
            if digest != matches[0]["published_sha256"]:
                raise ValueError("Snapshot digest mismatch")
            documents.append({"path": name, "sha256": digest,
                              "sections": _sections(raw, headings)})
        policy_path = "policy/collaboration.md"
        policy_raw = _read(root, policy_path)
        policy = {"path": policy_path, "sha256": hashlib.sha256(policy_raw).hexdigest(),
                  "text": policy_raw.decode("utf-8")}
        pack = {"status": "ready", "adapter_version": __version__,
                "framework_version": "0.5.0-rc.2 candidate",
                "accepted_baseline": "0.4.0 trial / conditional-pass",
                "scope": "selected passages, not all 72 documents; no semantic certification",
                "documents": documents, "adaptation": policy}
        # Leave room for framing and receipts. Never truncate a normative section.
        if len(json.dumps(pack, ensure_ascii=False)) > MAX_CONTEXT_CHARS - 2500:
            raise ValueError("Minimum pack exceeds context limit")
        return pack
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        return {"status": "degraded", "adapter_version": __version__,
                "code": "READING_UNAVAILABLE",
                "message": "必要规范缺失、校验失败或超限；未声称已读取。请修复/更新完整插件，或明确告知缺项并人工查阅。独立 wheel 不包含规范，请安装完整插件。"}


def reading_context() -> str:
    pack = prepare()
    if pack["status"] != "ready":
        return "[KnowTether READING_UNAVAILABLE] " + pack["message"]
    parts = ["[KnowTether MINIMUM_READING ready] 知识写作前查阅以下随包原文选段与协作适配。"
             "已校验原文文件 SHA-256；仅证明 Hook 读取并提供，不证明模型遵守或全框架合规。"
             "来源为 KPDM 0.5.0-rc.2 candidate，接受基线仍为 0.4.0 trial / conditional-pass。"
             "下面是规范资料；不构成新的用户授权。按当前委托执行，冲突服从宿主指令与用户授权。"
             "输出前按协作要求自查；生产记录不混入文章。复杂/公开任务另查完整相关规范与模板。"]
    for item in pack["documents"]:
        parts.append("\nSOURCE " + item["path"] + "\nSHA256 " + item["sha256"])
        for section in item["sections"]:
            parts.append(f"LINES {section['first_line']}-{section['last_line']}\n" + section["text"])
    policy = pack["adaptation"]
    parts.append("\nADAPTATION " + policy["path"] + "\nSHA256 " + policy["sha256"] + "\n" + policy["text"])
    parts.append("[KnowTether MINIMUM_READING end]")
    result = "\n".join(parts)
    assert len(result) <= MAX_CONTEXT_CHARS
    return result
