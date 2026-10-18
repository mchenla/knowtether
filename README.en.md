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

An actual Before / After example appears in the [Chinese homepage](README.md): in the second practical-book pair, the disabled chapter suggested adjusting and retesting; the enabled chapter also specified when to expand, retry or pause for serious errors. The other repeat did not show this gap. Only one of six complex pairs improved a declared content criterion; the others tied, so this is not evidence of a general quality improvement. See [the comparison](docs/evaluation-0.5.0.md).

In the two-repeat short-task pilot, injected guidance fell from 7,940 to 547 characters, with median wall time falling from 25.3s (0.4.1) to 17.5s (0.5.0); disabled was 8.2s. Complex writing remained slower than disabled. These are small, local descriptive observations.

Text hints cover citation placeholders, narrow absolute research claims, independent-validation wording, concentrated stock phrases, numeric long-dash ranges, a few inflated praise phrases and selected invisible characters. Optional worksheets add record/version consistency checks.

Guidance asks for independent judgment, useful disagreement, conditional MECE, concrete language and genre-appropriate formatting. These checks do not guarantee freedom from sycophancy, contrarianism, blind obedience, cherry-picking, factual errors, classification gaps or formulaic prose. Invisible characters are not proof of watermarks. There is no statistical watermark removal, grammar guarantee or promise to bypass AI detectors. Silence is not a quality pass. See the [capability audit](docs/capabilities.md) and [validation record](docs/validation.md).

## Open source

Software **0.5.0**; [release downloads](https://github.com/mchenla/knowtether/releases/latest). Software/adaptation material: **MIT**. Original KPDM material under framework/kpdm: **CC BY 4.0**. See [licensing by path](LICENSING.md).

KPDM remains **0.5.0-rc.2 candidate**, with **0.4.0 trial / conditional-pass** as the latest accepted baseline. Software release is not framework acceptance.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

See the [collaboration policy](policy/collaboration.md) and proposed [human–AI knowledge creation discipline](framework/kpdm/extensions/人机协作知识创作学.md). Framework acceptance and independent reader validation remain separate from software publication.
