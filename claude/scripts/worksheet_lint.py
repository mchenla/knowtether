#!/usr/bin/env python3
"""Check a knowtether worksheet for the eight rows, a reader task, and public-use quality level.

Usage: python3 -I worksheet_lint.py knowtether/worksheet.md
Exit 1 if a required row is missing or empty.
"""
import re
import sys

ROWS = [
    ("Intent", "意图"),
    ("Central idea", "中心思想"),
    ("Expression", "表达结构"),
    ("Grounding and scope", "依据与适用范围"),
    ("Mandate", "委托范围"),
    ("Acceptance", "验收条件"),
    ("Results and revisions", "结果与修订"),
    ("Human decisions", "人的决定"),
]
REQUIRED_BEFORE_DRAFT = 6


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    text = open(argv[1], encoding="utf-8").read()
    problems, notes = [], []
    cells = {}
    for en, zh in ROWS:
        m = re.search(r"^\|\s*(%s|%s)\s*\|([^|]*)\|([^|]*)\|([^|\n]*)\|?\s*$" % (re.escape(en), re.escape(zh)), text, re.M)
        if not m:
            problems.append(f"row missing: {en} / {zh}")
            continue
        cells[en] = m.group(4).strip()
    for i, (en, zh) in enumerate(ROWS):
        if en in cells and i < REQUIRED_BEFORE_DRAFT and not cells[en]:
            problems.append(f"row empty (needed before drafting): {en} / {zh}")
    intent = cells.get("Intent", "")
    public = re.search(r"公开|public", intent, re.I)
    q = re.search(r"Q([0-4])", intent)
    if public and q and int(q.group(1)) < 3:
        problems.append("Intent says public but Q target is below Q3")
    if public and not q:
        notes.append("Intent says public; state a Q target (at least Q3)")
    acc = cells.get("Acceptance", "")
    if acc and not re.search(r"读者|reader|recipient|接收者|使用者|user", acc, re.I):
        notes.append("Acceptance row names no reader task (who should be able to do what)")
    mandate = cells.get("Mandate", "")
    if mandate and not re.search(r"返回|停|stop|return|ask|问", mandate, re.I):
        notes.append("Mandate row does not say when the agent must stop and ask")
    if re.search(r"(已验证|validated|verified)", text) and not re.search(r"(谁|who|by )", text):
        notes.append("a 'verified' word appears without saying who verified")
    for p in problems:
        print("ERROR", p)
    for n in notes:
        print("NOTE ", n)
    if not problems and not notes:
        print("worksheet ok: 8 rows present, first 6 filled")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
