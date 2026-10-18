# KnowTether (知据)

**Work with AI to turn sources and ideas into grounded, useful articles, presentations and books.**

[中文](README.md) · [KPDM framework](framework/kpdm/README.md) · [Capability audit](docs/capabilities.md) · [Downloads](https://github.com/mchenla/knowtether/releases/latest)

| Question | Answer |
| --- | --- |
| Ontology | An open-source human–AI knowledge-work assistant: a framework plus an agent plugin. |
| Why | Bring source, judgment and writing requirements into AI work so people can review and revise it. |
| What | A method, templates, task reminders, optional work records and limited automated checks. |
| Where | Codex plugin; project hooks for Claude Code. The framework also works on its own. |
| Who | People writing articles, reports, research reviews or developing frameworks with AI. |
| When | When defining, drafting, reviewing and delivering knowledge work. |
| How | Install and trust the hooks, then ask normally. The agent receives guidance; people check the work and decide. |

**KPDM: Knowledge Product Development Meta-Model (知识产品开发元模型).** It describes how people and AI can develop knowledge that others can understand, use and check. KnowTether adapts selected requirements for agents.

## Codex: two commands

Requires Codex plugin commands and Python 3.10+ on the non-interactive PATH:

```bash
codex plugin marketplace add mchenla/knowtether
codex plugin add knowtether@knowtether
```

Review and trust the three hooks in `/hooks`, then start a new session; restart the desktop app after installation. No separate pip install is needed. Ask normally without a marker. Short requests receive compact guidance; complex writing receives relevant, hash-checked KPDM passages. Sufficient guidance avoids another Skill read; explicitly request “完整KPDM” for the full selected pack. Detection is heuristic and can miss cases. See [tiered reading](docs/minimum-reading.md).

To upgrade, run `codex plugin marketplace upgrade knowtether`, then `codex plugin add knowtether@knowtether`.

[Plugin guide](docs/codex-plugin.md) · [Python CLI and Claude Code](docs/cli.md)

## What is actually checked

Use it for management slide content, project documents, academic reports and reviews, explanatory articles, practical books, textbooks and publication drafts. Guidance connects claims to evidence, decisions to trade-offs and chapters to executable reader exercises. PPTX/Word creation requires host tools; the plugin itself does not render document files.

The 16-output four-arm pilot retained all completed drafts. Three-hook median overhead fell from 10.52s to 2.39s. Full-writing medians fell from 86.2s to 76.2s for reports and 82.7s to 67.2s for chapters versus 0.5.0. There were only two repeats per genre, with substantial variation. Optional paired-data computation showed no stable content-quality advantage over the runtime-only condition, and latency varied by genre. See [all drafts, metrics, input erratum and review limitations](docs/evaluation-0.6.0.md).

A typical example on the [Chinese homepage](README.md) contrasts actual old/new chapter excerpts: the old draft explains extra seconds and fixed formatting issues; the new one explains paired percentage changes. Both, as well as disabled drafts, have correct calculations and usable exercises. This is not a general quality improvement claim.

0.6.0 also fixes a source-path routing bug that accidentally requested the full framework. The pilot predates that fix; its deterministic context reduction is reported separately, without claiming measured writing-time gains. Explicit `.kpdm/task.json` files can opt into [experimental paired-data arithmetic and source receipts](docs/project-evidence.md). Ordinary writing needs no table or manifest. This is not general fact checking.

Text hints cover citation placeholders, narrow absolute research claims, independent-validation wording, concentrated stock phrases, numeric long-dash ranges, a few inflated praise phrases and selected invisible characters. Optional worksheets add record/version consistency checks.

Guidance asks for independent judgment, useful disagreement, conditional MECE, concrete language and genre-appropriate formatting. These checks do not guarantee freedom from sycophancy, contrarianism, blind obedience, cherry-picking, factual errors, classification gaps or formulaic prose. Invisible characters are not proof of watermarks. There is no statistical watermark removal, grammar guarantee or promise to bypass AI detectors. Silence is not a quality pass. See the [capability audit](docs/capabilities.md) and [validation record](docs/validation.md).

## Open source

Software **0.6.0**; [release downloads](https://github.com/mchenla/knowtether/releases/latest). Software/adaptation material: **MIT**. Original KPDM material under framework/kpdm: **CC BY 4.0**. See [licensing by path](LICENSING.md).

KPDM remains **0.5.0-rc.2 candidate**, with **0.4.0 trial / conditional-pass** as the latest accepted baseline. Software release is not framework acceptance.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

See the [collaboration policy](policy/collaboration.md) and proposed [human–AI knowledge creation discipline](framework/kpdm/extensions/人机协作知识创作学.md). Framework acceptance and independent reader validation remain separate from software publication.
