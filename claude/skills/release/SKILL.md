---
name: release
description: Pre-publication gate for a knowledge product. Runs the minimal checklist for a worksheet-only article or report, then the full release gate (identity, claims and evidence, status wording, rights, data, privacy, editorial, model language, production-talk isolation). Any red line fails the gate. Use when the user wants to publish, send out, or declare a piece finished.
argument-hint: "<final file>"
---

# Release gate

Target: $ARGUMENTS

Read `knowtether/worksheet.md`. Public use requires at least Q3 and a `/knowtether:check` verdict of pass or conditional-pass on the version being released. Acceptance and release are two separate human decisions; record both in the `Human decisions` row with the version number.

## Step 1: run the hard gate

Run the gate on the final file before anything else:

```
python3 -B "${CLAUDE_PLUGIN_ROOT}/hooks/entry.py" release --root "$PWD" --artifact <final file>
```

Exit code 1 means **fail**. Report every `blocking` item with its location and stop. Do not continue to the checklist, do not describe the piece as release-ready, and do not edit records just to make the gate pass.

The gate blocks on five rules, read from `.kpdm/work.json` and the final text:

| Rule | Blocks when |
|---|---|
| `RELEASE_SOURCE` | a fact, data, quote or cause claim has no source, no support note, a source without a locator, or a source not marked `human-verified`; or no claims are registered and `publication.external_facts` is not `"none"` |
| `RELEASE_PLACEHOLDER` | the text still has `[citation needed]`, `TODO`, `TBD`, `[待补]`, `[待核实]` or similar |
| `RELEASE_RIGHTS` | any source has an unknown, pending or empty `rights_status` |
| `RELEASE_ACCEPTANCE` | there is no `author_acceptance` record with the same `version` as `artifact_version` and an `evidence_ref` |
| `RELEASE_WORKFLOW_LABEL` | the text has workflow labels such as 候选发布版, 内部草稿, 供某人审阅, DRAFT or WIP |

If `.kpdm/work.json` does not exist, you may draft its `claims` and `sources` from `knowtether/knowledge-overview.md`. Three fields are the user's to give, never yours:

- `verification: "human-verified"`, only for a source the user says they checked against the original in this conversation;
- `author_acceptance`, only after the user names the exact version they accept; put their words and the date in `evidence_ref`;
- `publication.external_facts: "none"`, only when the user states the piece contains no external facts.

The gate checks records, not truth. A pass means the five rules hold; it does not show that sources support the claims or that nothing went unregistered.

## Step 2: seven red lines (any one stops release)

1. A core fact or number has no traceable source.
2. A citation does not exist, does not open, or was not checked against the original.
3. Rights for copied, translated, adapted material, charts or images are unknown.
4. AI-generated facts, quotes or data were not verified by a person.
5. Confidential, personal or client information is disclosed without authorisation.
6. Title, abstract or marketing promise exceeds what the body supports.
7. Authorship, contributors, funding, conflicts of interest or material AI use are concealed.

## Minimal checklist (worksheet-only article or report)

- [ ] Intent says public and Q target is at least Q3
- [ ] Core claims classified; grounding locatable; unknowns kept explicit
- [ ] Every external material has a rights status; none is `blocked-unknown-rights`
- [ ] Facts, quotes and data drafted by the agent were verified by a person
- [ ] The reader task was run by a real target reader or independent editor and the result is recorded
- [ ] Human decisions row names the accepted version; release decision recorded separately
- [ ] Sections below on rights, truth, privacy and production-talk isolation pass item by item

The lightweight entry reduces paperwork, not checks.

## Full gate

**Identity and quality**: profile and Q level stated; title / abstract / cover promises do not exceed the body; authors, contributors, funding, conflicts disclosed; AI use recorded as the Q level requires.

**Claims and evidence**: all core facts and external data traceable; quotes verified verbatim with stable locators; interpretations, causal claims, predictions and normative choices not posing as facts; counter-examples, limits and major unknowns disclosed; high-risk conclusions independently reviewed; each citation checked to support the claim it is attached to; `search-summary-only` material marked as not verified.

**Status wording**: every status word has object, scope, criterion, evidence, verifier, version, limits; production, quality and publication status not mixed; self-checks, agent self-assessment, structural checks, hypothetical cases and bootstrap tests not rewritten as independent validation; derived views do not raise the source's status or drop its limits; after the user asked to stop or narrow research, no further expansion; budget spent not written as "question resolved".

**Rights**: rights status per external item; images, charts, screenshots, code, long quotes licensed; CC licence version and BY/NC/ND/SA conditions met; translations and adaptations have a rights basis and a note of changes; zero `blocked-unknown-rights`.

**Data**: dataset author, name, version, repository, ID, access date, licence; raw vs computed vs estimated numbers distinguished; cleaning, filters, units, currency, inflation, time range recomputable; chart footnotes carry source and transformation; uncertainty, gaps and incomparability stated.

**Privacy and confidentiality**: lawful basis for personal data; client, internal or confidential material cleared; anonymised cases not easily re-identified; no unauthorised sensitive data was pasted into tools.

**Editorial and usability**: terms, numbering, cross-references, bibliography consistent; links and DOIs resolve; target reader test done; accessibility, figure captions, media format; version, date, limits and feedback channel stated. For Chinese deliverables in Office formats: no red underlines under Chinese text (no decorative red rules; set `noProof` or correct `lang` on Chinese runs) and sufficient text-to-fill contrast in every coloured shape.

**Model language and warmth**: `python3 -I ${CLAUDE_PLUGIN_ROOT}/claude/scripts/fingerprint_check.py <file>` run; em dashes replaced with " - ", colon or comma except true parentheticals; buzzwords replaced with concrete actors, actions and sources; coined terms passed the new-term test; the text reads aloud naturally and a target reader or independent editor checked warmth and professionalism.

**Production-talk isolation**: no workflow labels ("candidate release", "for review by…") in cover, title, headers, body, slides or UI; no reasoning process, generation notes, session info, repository paths or framework names in the product; "this document does not claim…" style self-commentary rewritten as direct rules about object, evidence, verifier and conditions; editor checklists and change rationale kept out of reader-facing text; remaining version / status / limit notes justified by reader need, law or regulation.

## Output

```
Release gate: pass | fail
Red lines: 7/7 clear | failed: <numbers>
Sections: identity ✓/✗ … production-talk ✓/✗
Blocking items: location → issue → fix
Record: accepted version vX by <user> on <date>; release decision: <pending | approved by user>
```

Release gate `fail` makes the whole result `fail`. Only the user approves release. Write the result into the worksheet and stop.
