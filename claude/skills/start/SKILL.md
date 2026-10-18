---
name: start
description: Start a knowledge product (article, report, book chapter, framework, research overview) from a one-sentence task. Asks the six core questions, picks a profile and quality level, writes a lightweight worksheet with an explicit mandate for the agent, and says when more control is needed. Use when the user wants to begin a piece of writing or research with Claude's help.
argument-hint: "<one-sentence task>"
---

# Start a knowledge product

Task from the user: $ARGUMENTS

Goal: within one exchange, turn the task into `knowtether/worksheet.md` that both of you can work from. Do not ask the user to learn any model or vocabulary first.

## 1. Ask the six core questions

Ask them together, in the user's language, in plain words. "Don't know" is a valid answer; write it down as `unknown`, never fill it in yourself.

| Question | What you need | Worksheet row |
|---|---|---|
| For whom, solving what? What should change for the reader? Internal or public? | audience, problem, expected change, use | Intent |
| What exactly is being proposed? Where is the contribution against what people already know? | current claim, proposed contribution, open points | Central idea |
| On what basis? When does it fail? | sources, experience, reasoning, counter-examples, unknowns | Grounding and scope |
| What should the reader be able to do afterwards? | at least one reader task: understand, judge, learn, act or create | Acceptance |
| In what form, and how will the reader move through it? | article, report, chapter, framework; structure | Expression |
| How will we know it is right, and fix it when it is not? | who checks, what, pass condition | Acceptance |

Only gaps that block the next step need discussion now. Leave the rest as `unknown` and move on.

## 2. Pick the entry mode

- **Goal is clear**: the user has a claim and material. Fill the worksheet, note only the gaps that would change the result, proceed to `/knowtether:draft`.
- **Question is open**: the user has a topic but no central idea. Write `Central idea: claim undecided; research questions: …`, set a research budget and stop condition in the Mandate row, proceed to `/knowtether:research`. A research overview can be the final deliverable; do not force an article.

## 3. Pick profile and quality level

| Profile | Default quality | Reader task to write down |
|---|---|---|
| Article | Q3 if public, Q1 if private draft | reader can restate the main point and its scope |
| Report | Q2 internal, Q3 if it leaves the recipient | recipient can say what question it answers, on what basis, under what conditions the recommendation holds |
| Book / long publication | Q3, flagship Q4 candidate | reader can restate the central proposition and apply one chapter's method |
| Framework / knowledge system | Q4 candidate | user can apply it to their own case and state its limits |
| Series | Q3 | reader entering at any unit can find the core and the other units |

Quality levels: Q0 capture, Q1 working draft, Q2 professional internal, Q3 publishable, Q4 authority candidate. Anything public is at least Q3. Q4 means "candidate", never self-declared authority.

## 4. Write the mandate

The Mandate row must answer four things: what the agent may do; which input versions it works from; how far to explore or what budget before converging; what makes it stop and ask. Default stop list: the agent stops and returns to the user when: a new central claim appears or would change the central position; the author's intent drifted; the scope widened in substance; unauthorised risk appears (high-stakes facts, unclear rights, sensitive data, public accusations); a key check failed or the acceptance criteria would have to change; sources or agents disagree in a way existing sources, criteria and the user's decisions cannot settle (full text: the section 必须返回人的情形 in `${CLAUDE_PLUGIN_ROOT}/framework/kpdm/spec/02 Methods and Protocols/人机协作协议.md`). Wording, formatting and authorised tidying do not need line-by-line approval.

## 5. Write the worksheet

Copy `${CLAUDE_PLUGIN_ROOT}/claude/templates/<lang>/worksheet.md` to `knowtether/worksheet.md` (create the folder; ask only if the user already keeps project notes elsewhere). Fill the first six rows to "good enough for the next step"; the last two rows (Results, Human decisions) fill in later. Reference existing files instead of copying them. Write `not applicable` only with a reason.

Then run `python3 -I ${CLAUDE_PLUGIN_ROOT}/claude/scripts/worksheet_lint.py knowtether/worksheet.md` and fix what it reports.

## 6. Say whether to expand control

Tell the user, in one or two sentences, if any of these applies and what record it adds; otherwise say the worksheet is enough:

| Trigger | Add |
|---|---|
| data, strong causal claims or high-impact recommendations | a claim-evidence ledger and source checks item by item; domain review |
| material with unclear rights or sensitive content | a source and rights ledger; restrict use until resolved |
| many chapters, outputs or people | versioned context, named work packets, an authority matrix, change-impact notes |
| a core definition or method changes | a decision record, affected outputs listed, re-check |
| public release | at least Q3, independent check, a real reader test, `/knowtether:release` |

Close by naming the next command (`/knowtether:research` or `/knowtether:draft`) and the single most important unknown.
