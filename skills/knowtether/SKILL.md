---
name: knowtether
description: "Explicitly expand the complete KPDM workflow, templates or publication review when requested. Automatic lightweight and focused guidance is supplied by hooks; do not load this skill for ordinary short writing."
---

# KnowTether: knowledge with traceable grounds

This is a practical adaptation of selected KPDM requirements, not the full framework or a certificate of quality. The reference is KPDM 0.5.0-rc.2 candidate; the accepted baseline remains 0.4.0 trial / conditional-pass. The author-licensed framework snapshot is bundled at [KPDM](../../framework/kpdm/README.md). See [rule mapping](../../docs/rules.md) and [source identities](../../policy/source-map.json).

## Expand only when needed

Automatic Hook routing handles simple and focused tasks without loading this file. Use this complete workflow when explicitly invoked or the user asks to expand KPDM. A LIGHT context is an adaptation summary, not a claim that specifications were read. A focused pack identifies only the exact source passages supplied.

## Consult the minimum sources before knowledge writing

- For this explicitly expanded workflow, consult the `MINIMUM_READING ready` source passages supplied by the UserPromptSubmit hook. Focused packs contain selected quality/type passages and compact adaptation guidance; the full pack reads three specification files plus the [collaboration requirements](../../policy/collaboration.md). Exact passages have snapshot hashes and locations. Delivery does not certify compliance or reading other documents.
- If that pack is absent or degraded, run `python -B <plugin-root>/hooks/entry.py prepare --root <project>` with an available Python 3.10+ interpreter and consult its output before writing. Resolve `<plugin-root>` two directories above this installed skill directory; quote actual paths for the shell. If the bundle is unavailable, disclose that fact and use only sources actually available; never claim a successful read. Ordinary code/account work stays outside scope. Do not reread identical passages already present in the current task.
- For complex knowledge products, KPDM workflows or publication review, additionally consult the bundled [quick start](../../framework/kpdm/spec/00%20Start/快速入门.md), [worksheet template](../../framework/kpdm/spec/04%20Templates/轻量工作单模板.md), relevant [quality constraints](../../framework/kpdm/spec/01%20Foundations/KPDM%20质量约束.md), [human-agent protocol](../../framework/kpdm/spec/02%20Methods%20and%20Protocols/人机协作协议.md) or [index](../../framework/kpdm/spec/KPDM%20知识索引.md). Read only the extra material the task needs.
- Resolve all paths from this installed skill; do not assume access to the author's private vault. Omitted local records are not available evidence. A user-supplied newer authoritative version takes precedence after checking its identity.
- The framework snapshot is CC BY 4.0; software and this adaptation skill are MIT. Preserve source attribution and modification notices when redistributing framework material; see [licensing](../../LICENSING.md).

## Work at the appropriate depth

- Identify the intended reader, problem and use. Cover purpose, knowledge, grounds, enablement, expression, and validation as functions; do not force six headings or six sequential steps.
- An exploration may deliver a sourced overview with an undecided central claim. Preserve unknowns, conflicts and alternatives; do not invent answers to complete a template.
- Use a familiar structure and language. Explain necessary terms and include examples, counterexamples or reader tasks where useful. Do not invent terminology to suggest originality.
- Short answers can remain short. Add records for complex work, data, strong causal claims, high-impact advice, unclear rights, sensitive material or public publication when those records support a real decision.

## Ground the result

- Distinguish facts, direct quotations, inference, hypotheses and value choices. For important external claims, locate the original material and check that it supports the specific statement. A link or search excerpt is not verification of the original.
- Explain applicability, assumptions, limitations, important unknowns and the strongest relevant counterexample or alternative explanation.
- Check rights and attribution separately from source accessibility; protect private and confidential information.
- Evaluate against stated criteria rather than the author's enthusiasm. Do not equate polished prose, structural checks, AI review, fictional cases or this plugin's silence with factual validity, independence or reader comprehension.
- Follow the collaboration requirements: assess independently without flattery, raise only consequential disagreements with reasons and workable alternatives, continue authorized work without repeated permission, preserve qualifiers and context, and check closed classifications for overlap and coverage. Open examples are not exhaustive categories. Check grammar, reference clarity and natural wording before delivery; none of these reviews guarantees correctness or watermark removal.

## Keep decisions and output honest

- Work within the current user request. Routine authorized research, drafting, edits and checks can continue. Bring new core claims, changed author intent, materially expanded scope, unapproved risks or failed essential checks back to the user. Candidate ideas do not automatically become the author's position.
- Keep drafted, author-accepted, independently verified and release-approved states separate, with the version and actual supporting record. Do not create missing human decisions or fabricate evidence.
- Public knowledge products require the applicable KPDM Q3+ checks, including actual source/rights/privacy review and reader or independent editorial tasks. AI simulations are simulations; this plugin does not perform or approve these checks for the user.
- Keep production notes in working records. Published content should contain what readers need to understand and use it, including necessary scope, version, limitations and disclosures.

## Optional records and checks

Use existing records when available. If the user needs a worksheet, use `.kpdm/work.json` in the actual creative project, not in this installed plugin. It has eight fields under `worksheet`: `intent`, `central_idea`, `expression_structure`, `evidence_and_scope`, `delegation`, `acceptance`, `results_and_revisions`, and `human_decision`. Include `schema_version: 1`, `mode: warn`, `enabled: true`, the current `session_id`, `policy_version: 0.5.0-rc.2`, input/artifact versions and open issues. Unknowns and reasoned non-applicability are allowed. Recheck current delegation before binding a previous session's worksheet.

For an explicitly requested mechanical check, invoke the bundled CLI with the available Python 3.10+ interpreter: `python -B <plugin-root>/hooks/entry.py check --root <project> --artifact <relative-text-file>`. Quote paths correctly for the active shell. Resolve `<plugin-root>` from this skill's location; never treat the plugin cache as the project. This command reports record consistency and text hints, not semantic approval. A worksheet is optional when checking a specified text file.

The installed hooks use the current event, bundled specifications and project-local records; they do not read full transcripts or rewrite results. Project-level `{"schema_version":1,"enabled":false}` in `.kpdm/config.json` disables them there. See [plugin installation and behavior](../../docs/codex-plugin.md).
