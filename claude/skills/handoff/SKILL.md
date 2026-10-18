---
name: handoff
description: Write or read a hand-over record so another session or collaborator can continue a knowledge product without inheriting stale authority. Captures the five essentials (valid input versions, current central claim, mandate, open items, acceptance criteria) plus research state (question list, material locations, overview version, stop position, tool configuration). Use at the end of a session, when resuming someone else's work, or when context was compacted.
argument-hint: "write | read [path]"
---

# Hand-over

Mode: $ARGUMENTS

## write

Create or update `knowtether/handoff.md` from `${CLAUDE_PLUGIN_ROOT}/claude/templates/<lang>/handoff.md`:

1. Valid input versions (files and versions the current work rests on)
2. Current central claim, or `claim undecided` with the live research questions
3. Mandate in force, and what it does **not** cover
4. Open items: decisions waiting for the author, unverified claims, `search-summary-only` material, failed checks
5. Acceptance criteria and reader task, unchanged from the worksheet
6. Research state if any: question list location, material record location, overview version, where you stopped and why
7. Automation config that affected results: model, search settings, usage figures you can actually see; mark `unknown` otherwise

Then say in one line what the next person should do first.

## read

When resuming (yours or someone else's work, or after compaction):

1. Read `knowtether/handoff.md`, `knowtether/worksheet.md`, `knowtether/knowledge-overview.md`. Find the five essentials. Anything missing gets filled with the user **before** work continues.
2. Do not inherit the previous session's authorisation. Restate the mandate and ask the user to confirm it for this session, in one question.
3. Check for upstream change: if any input version differs from the hand-over, list the sections and overview rows that depended on it and mark them `re-check needed`. Content produced from stale context is not a release candidate.
4. If only the outline is being revised, reuse research material that is still valid; do not redo the whole research.
5. Where a statement in the draft disagrees with the current worksheet, check before reusing it.

Report: what is valid, what needs re-check, what you will do next.
