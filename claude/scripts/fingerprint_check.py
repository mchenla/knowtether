#!/usr/bin/env python3
"""Flag model-language fingerprints, status words and production talk in a text file.

Usage: python3 -I fingerprint_check.py <file> [--json]

Reports line numbers. It finds candidates; a person or the verifier decides what to change.
Pure standard library. Exit code 0 always (it is a report, not a gate).
"""
import json
import re
import sys
from collections import Counter

EM_DASH = re.compile(r"—|——")

BUZZ_ZH = ["闭环", "抓手", "赋能", "范式", "颗粒度", "链路", "认知升级", "底座", "顶层设计", "打通", "沉淀", "拉齐", "对齐颗粒度", "方法论感"]
BUZZ_EN = ["leverage", "delve", "robust", "seamless", "seamlessly", "tapestry", "navigate the complexities", "in today's fast-paced", "it's important to note", "it is important to note", "game-changer", "unlock", "empower", "holistic", "synergy", "paradigm", "cutting-edge", "at the end of the day", "a testament to", "underscores", "multifaceted", "landscape"]

PATTERN_ZH = [
    (re.compile(r"不是.{1,20}而是"), "“不是……而是……”句式"),
    (re.compile(r"(本文|本报告|本文件|本章)(将|不宣称|旨在|试图|认为|尝试)"), "元话语（关于文本自身的话）"),
    (re.compile(r"(候选发布版|内部探讨参考|供.{1,6}审阅|仅供参考)"), "工作流标签进入成品"),
    (re.compile(r"(接洽后|受控渠道|按授权范围)"), "过程语言"),
]
PATTERN_EN = [
    (re.compile(r"\bnot (just|only|merely) .{1,40} but\b", re.I), "'not just X but Y' cadence"),
    (re.compile(r"\b(in this (article|report|document|chapter)|this (article|report|document) (will|aims|does not claim|argues))\b", re.I), "metadiscourse about the text itself"),
    (re.compile(r"\b(candidate release|for review by|draft for internal discussion)\b", re.I), "workflow label in product text"),
]

STATUS_ZH = ["完成", "完整", "写透", "成熟", "有效", "可靠", "可用", "拿来即用", "经过验证", "标准", "权威", "中立", "领先", "国际化", "世界级", "最佳实践", "最佳"]
STATUS_EN = ["complete", "comprehensive", "mature", "validated", "proven", "reliable", "robust", "authoritative", "best practice", "best-practice", "world-class", "industry-leading", "state of the art", "state-of-the-art", "definitive"]

ABSTRACT_ZH = ["锁", "情境", "边界", "证据", "循证", "纪律", "铁律", "体系", "机制", "维度", "逻辑", "本质", "生态"]


def scan(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    hits = []
    abstract_counter = Counter()
    for no, line in enumerate(lines, 1):
        low = line.lower()
        if EM_DASH.search(line):
            hits.append((no, "em-dash", "长破折号 / em dash", line.strip()))
        for w in BUZZ_ZH:
            if w in line:
                hits.append((no, "buzzword", w, line.strip()))
        for w in BUZZ_EN:
            if w in low:
                hits.append((no, "buzzword", w, line.strip()))
        for rx, label in PATTERN_ZH + PATTERN_EN:
            if rx.search(line):
                hits.append((no, "pattern", label, line.strip()))
        for w in STATUS_ZH:
            if w in line:
                hits.append((no, "status-word", w, line.strip()))
        for w in STATUS_EN:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                hits.append((no, "status-word", w, line.strip()))
        for w in ABSTRACT_ZH:
            abstract_counter[w] += line.count(w)
    dense = {w: c for w, c in abstract_counter.items() if c >= 5}
    return hits, dense, len(lines)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    path = argv[1]
    as_json = "--json" in argv
    hits, dense, n = scan(path)
    if as_json:
        print(json.dumps({"file": path, "lines": n, "hits": [dict(line=h[0], kind=h[1], match=h[2], text=h[3]) for h in hits], "dense_abstract_words": dense}, ensure_ascii=False, indent=2))
        return 0
    print(f"{path}: {n} lines, {len(hits)} candidate hits")
    kinds = Counter(h[1] for h in hits)
    for k, c in kinds.most_common():
        print(f"  {k}: {c}")
    print()
    for no, kind, match, text in hits:
        print(f"L{no:>4} [{kind}] {match}: {text[:100]}")
    if dense:
        print()
        print("Abstract words used 5+ times (check whether they became all-purpose scaffolding):")
        for w, c in sorted(dense.items(), key=lambda kv: -kv[1]):
            print(f"  {w}: {c}")
    print()
    print("Status words are claims: each needs object, scope, criterion, evidence, verifier, version, limits, or a factual rewrite.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
