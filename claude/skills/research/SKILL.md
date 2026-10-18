---
name: research
description: Run a human-steerable research loop for an open question. Proposes questions from several angles, finds material with exact locators, records what each source says versus what is inferred, keeps a knowledge overview the user can edit, and stops on coverage, user request, budget or no new findings. Use when the central claim is undecided, when the user wants to explore a topic before writing, or when a draft needs more grounding.
argument-hint: "[topic or question] [--budget N rounds]"
---

# Research loop

Topic: $ARGUMENTS

Read `knowtether/worksheet.md` first if it exists; the Mandate row gives the budget, allowed material and stop conditions. If there is no worksheet, run `/knowtether:start` first or ask for the three essentials: purpose, audience, budget.

Delegate the heavy lifting to the `knowtether:researcher` agent so your own context stays free for the user's steering. One researcher is enough; do not spin up several "experts" that share one model and one source pool.

## One round

1. **Ask from several angles.** From the user's purpose, the material already in hand, and adjacent fields, propose 3 to 6 questions. For each, one line on why it matters to the reader task. Skip questions that only add breadth.
2. **Find material you are allowed to use.** For every item keep the seven material fields (see template): ID, identification, version or retrieval date, locator (page / section / paragraph), question it answers, verification status, use restriction. Separate "the source says", "I infer", and "nobody has answered".
3. **Follow up on conflict, conditions and gaps.** When new material contradicts earlier material or exposes a missing condition, say what judgement it would change. Material that was retrieved but not yet discussed gets its own line, not a silent drop.
4. **Update the knowledge overview** in `knowtether/knowledge-overview.md` (template in `${CLAUDE_PLUGIN_ROOT}/claude/templates/<lang>/knowledge-overview.md`). One row per question or concept: current answer or disagreement, material IDs, open points, author's choice (`not chosen` until the user chooses), affected outline sections. Do not merge disagreeing sources into one tidy answer.
5. **Report to the user** in a short message: new findings, new questions, open conflicts, what you plan next. Record key choices; do not demand approval every round.

## Stop when any of these holds

- the coverage target in the mandate is met;
- the user says converge, narrow, pause or stop;
- the budget is spent;
- two rounds in a row added nothing relevant (default, adjustable).

Budget spent is not the same as "the question is answered". Write the remaining unknowns into the overview and say so.

## Steering

The user can add material, veto a branch, narrow scope, or stop at any time. The next action follows the latest instruction; completed material and recorded unknowns stay. After a stop or narrowing, never keep expanding.

## What you must not do

- Fabricate or complete references, quotes, page numbers or data.
- Count `search-summary-only` material as verified.
- Write an author hypothesis as fact because several sources are nearby.
- Turn the overview into a "knowledge graph" and treat its shape as proof; it is a view of what is known, disputed and missing.

## Hand-over

A research deliverable is the overview plus the material records plus a list of decisions waiting for the author. If the user then wants a piece written, `/knowtether:draft` builds the outline from the overview and revises it as findings change. Before drafting, every `search-summary-only` material that a claim depends on must be verified against the original or replaced.
