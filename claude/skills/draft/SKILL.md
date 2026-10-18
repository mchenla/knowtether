---
name: draft
description: Draft or revise a knowledge product inside the mandate written in knowtether/worksheet.md. Keeps candidate ideas as candidates, keeps external facts tethered to material records, separates drafting from verification, and stops when a new central claim, drifted intent, widened scope or unauthorised risk appears. Use when the user asks to write, continue or revise a piece that has a worksheet.
argument-hint: "[section or instruction]"
---

# Draft inside the mandate

Instruction: $ARGUMENTS

## Before writing

1. Read `knowtether/worksheet.md`. Confirm: input versions, central idea (or "claim undecided"), mandate, acceptance criteria. If any of the four is missing, stop and say which; do not inherit authority from an earlier session.
2. Read `knowtether/knowledge-overview.md` if present. Every claim that needs external support must trace to a material ID with a locator and `verified-original` status. List the claims that cannot, and either verify now (if the mandate allows) or mark them `[unverified: M-xx]` in the draft.
3. State in one line what you will produce (which section, which version number, which outline).

## While writing

- Write for the reader task in the Acceptance row, in the register the profile asks for. Say the concrete person, problem, action and result before any abstraction.
- Keep the author's candidate claims visibly provisional until accepted: "the author's working hypothesis is…", or a `[candidate]` tag in a working draft. Do not polish a hypothesis into a fact.
- Label the nature of important claims where it matters to the reader: fact, interpretation, recommendation, original construct, boundary.
- For reports: every recommendation must trace to a judgement, every judgement to analysis and material. No chain break.
- One main working mode at a time. If you find yourself exploring new questions mid-draft, note them in the overview and return to drafting; do not silently switch.
- Do not add process talk to the product text: no "this document does not claim…", no "candidate version", no workflow labels in titles or headers. Production status goes in the worksheet, not the prose.

## Stop and hand back when

Any of these fires (from the section 必须返回人的情形 in `${CLAUDE_PLUGIN_ROOT}/framework/kpdm/spec/02 Methods and Protocols/人机协作协议.md`):

1. A new central claim appears, or a candidate idea would change the central position.
2. The author's intent drifted while drafting, or a structural change altered the meaning.
3. The scope widened in substance (one case generalised to a class of cases).
4. Unauthorised risk: high-stakes facts, material with unclear rights, sensitive or personal data, public accusations.
5. A key check failed, or the acceptance criteria would have to change to pass.
6. Sources or agents disagree in a way the current sources, acceptance criteria and the user's earlier decisions cannot settle.

Keep going without asking for wording and formatting, tidying inside the mandate, link and consistency checks, and writing approved sections to an agreed outline. Hand back with: the question, the candidates, the evidence for each, your recommendation if you have one. Then wait.

## After writing

1. Update the worksheet: version/date, `Results and revisions` (what changed, what is still open), production status `drafted`.
2. Run `python3 -I ${CLAUDE_PLUGIN_ROOT}/claude/scripts/fingerprint_check.py <draft file>` and fix model-language hits yourself; this is wording, inside the mandate.
3. Do **not** verify your own draft and call it checked. Say: "Drafted vN. Run `/knowtether:check` for an independent pass." Self-review is allowed and should be noted as `author/agent self-check`, never as independent verification.
4. List for the user: decisions waiting, unverified claims, material still `search-summary-only`.

## Revising from feedback

When the user or a reader test returns problems: locate the affected rows in the overview and the affected sections, fix those, re-run the relevant check, and record the change in the worksheet. Do not rebuild the whole piece for a local defect. If an upstream definition changed, list every section that used it before editing any.
