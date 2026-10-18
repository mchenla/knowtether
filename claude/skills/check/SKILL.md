---
name: check
description: Independent verification of a draft against its worksheet. Runs the six-dimension check, tests claim-evidence fit (link exists but does not support, one source posing as many, false causal joins, snippet-only material, hypothesis written as fact), checks status language and model fingerprints, and reports pass / conditional-pass / fail with locations. Use after drafting, before accepting a version, and whenever the user asks "is this right?".
argument-hint: "<draft file> [--readers]"
---

# Check (Verify mode)

Target: $ARGUMENTS

Verification is separate from drafting. Do the check through the `knowtether:verifier` agent, which starts without the drafter's assumptions, and pass it: the draft path, `knowtether/worksheet.md`, `knowtether/knowledge-overview.md`. If this same session drafted the text, say so in the report; the agent's pass still counts only as an independent *agent* check, not as human or reader verification.

## What the verifier checks

Freeze the criteria first: take the Acceptance row and the quality level from the worksheet. Changing the bar after looking at the result cancels the check.

| Dimension | Question |
|---|---|
| Completeness | Are the agreed outputs all there? |
| Consistency | Same definitions as the authority source and other views? Same version? |
| Correctness | Facts, logic, formulas, citations, relations hold? |
| Reproducibility | Could another person reach the same result from the same inputs? |
| Usability | Can the stated reader complete the reader task? |
| Boundary and risk | Are unknowns, counter-examples, failure modes and limits disclosed? |

Claim-evidence fit, per important claim:

1. The cited material exists, opens, and the locator points at text that supports the claim as stated.
2. Multiple citations are genuinely independent, not one source reposted.
3. Any causal link in the text is made by a source, or is labelled as the author's inference.
4. No claim rests only on `search-summary-only` material.
5. Author hypotheses are still labelled as such.

Status language: every "complete / validated / reliable / authoritative / best practice" style word has object, scope, criterion, evidence, verifier, version, limits, or is rewritten as a factual description.

Model fingerprints: run `python3 -I ${CLAUDE_PLUGIN_ROOT}/claude/scripts/fingerprint_check.py <file>`; the verifier reads the hits and judges which ones hurt understanding or trust. At Q3/Q4, dense model language or needless coined terms fail the language gate.

New terms: for each coined term, five answers: why existing terms fall short; definition and non-examples; relation to existing concepts; what is lost without it; how a reader would say it in plain words. No answers, no term.

Honesty: the strongest counter-example and alternative explanation; whether length, structure or term count is being mistaken for validity; whether a flaw the author would not like to see was skipped; whether "worth exploring" became "established".

## Reader task

If `--readers` is passed or the piece is Q3+, propose how a **real** target reader or an independent editor will run the reader task (what they are given, what they must restate or do, pass rule). You may also run the `knowtether:reader-sim` agent for an early signal; its output is labelled `simulated reader (model)` and never goes in the "real reader result" field.

## Report format

```
Verdict: pass | conditional-pass (usable only within: …) | fail
Criteria used: <Acceptance row, Q level, version checked>
Findings (most severe first): location, what is wrong, what would fix it
Claim-evidence table: claim → material ID → status (supports / does not support / unverified)
Status-language hits: line → word → missing fields
Fingerprint hits worth fixing: line → phrase
Not checked: <dimensions not covered and why>
Who checked: agent (independent context) | agent (same session as drafter) 
```

Truth or Rights failures make the verdict `fail` regardless of the other dimensions. Do not average.

## After the report

Write the verdict and the open items into the worksheet's `Results and revisions` row. Set production status to `structurally-reviewed` only if the verdict is pass or conditional-pass. Acceptance (`author-accepted`) is the user's move, on a named version; do not set it.
