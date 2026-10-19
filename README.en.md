# KnowTether (知据)

**Work with AI to turn sources and ideas into grounded, useful articles, presentations and books.**

[中文](README.md) · [KPDM framework](framework/kpdm/README.md) · [Capability audit](docs/capabilities.md) · [Downloads](https://github.com/mchenla/knowtether/releases/latest)

| Question | Answer |
| --- | --- |
| Ontology | An open-source human–AI knowledge-work assistant: a framework plus an agent plugin. |
| Why | Bring source, judgment and writing requirements into AI work so people can review and revise it. |
| What | A method, templates, task reminders, optional work records and limited automated checks. |
| Where | Codex plugin; Claude Code plugin or project hooks. The framework also works on its own. |
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

## Claude Code: one command

Requires Claude Code 2.1.275+ and Python 3.10+ on PATH. In a session, run:

```
/plugin install knowtether --marketplace mchenla/knowtether
```

The same hooks provide guidance. Seven commands add an explicit path from a one-sentence task to a release check: `/knowtether:start`, `research`, `draft`, `check`, `release`, `handoff` and `adopt`. See the [Claude Code plugin guide](docs/claude-plugin.md) (Chinese).

## What is actually checked

Use it for management slide content, project documents, academic reports and reviews, explanatory articles, practical books, textbooks and publication drafts. Guidance connects claims to evidence, decisions to trade-offs and chapters to executable reader exercises. PPTX/Word creation requires host tools; the plugin itself does not render document files.

Version 0.7.0 preserves the Claude Code plugin and explicit release checks from other contributors, packages both host components, and rejects six reproducible mechanical false passes. The automatic writing context is unchanged. Claude manifests and Windows Git Bash launchers pass; Claude model-session/command/agent end-to-end validation remains unrun. The cloud reviewer stays in its pending PR. See the [integration review](docs/integration-review-0.7.0.md).

A new 16-draft automatic on/off comparison used reports and practical chapters with complete or deliberately damaged source packets, twice in reversed order. Both conditions handled all six planted issues. No added source-detection or overall content-quality advantage was established; enabled chapters left follow-up testing without a complete upper bound. Median paired wall time fell about 2% to 11% in this sample. Cumulative input fell about 37% to 38% for reports and 19% for complete chapters, but rose about 8% for damaged chapters. Enabled runs injected 6,310 to 6,409 characters and increased the first observed input; token totals are not bills. Two repeats and development-AI review do not establish stable effects. See [all 16 outputs, quality differences and resource metrics](docs/evaluation-0.7.0.md).

The preregistered first damaged-report pair on the [Chinese homepage](README.md) handled the same issues in both drafts: 68.334 to 62.986 seconds, 7 to 2 tool calls, 85,965 to 47,741 cumulative input tokens. The enabled draft still needs two speaker notes shortened. This shows one reduction in tool round trips, not a new quality guarantee. Earlier [24-draft results](docs/evaluation-0.6.0-source-quality.md) and [startup measurements](docs/evaluation-0.6.0.md) remain separate; cross-date differences are not a version speedup estimate.

Optional `.kpdm/task.json` enables [paired-data arithmetic and source receipts](docs/project-evidence.md), not general fact checking. Ordinary writing needs no manifest.

An explicit release gate blocks five issues: fact sources not verified by a person, leftover citation placeholders, materials with unknown rights, no acceptance record for the released version, and workflow labels in the final text. It checks records and text, not truth, and hooks never run it. See [release gate](docs/cli.md) (Chinese).

Text hints cover citation placeholders, narrow absolute research claims, independent-validation wording, concentrated stock phrases, numeric long-dash ranges, a few inflated praise phrases and selected invisible characters. Optional worksheets add record/version consistency checks.

Guidance asks for independent judgment, useful disagreement, conditional MECE, concrete language and genre-appropriate formatting. These checks do not guarantee freedom from sycophancy, contrarianism, blind obedience, cherry-picking, factual errors, classification gaps or formulaic prose. Invisible characters are not proof of watermarks. There is no statistical watermark removal, grammar guarantee or promise to bypass AI detectors. Silence is not a quality pass. See the [capability audit](docs/capabilities.md) and [validation record](docs/validation.md).

## Open source

Software **0.7.0**; [release downloads](https://github.com/mchenla/knowtether/releases/latest). Software/adaptation material: **MIT**. Original KPDM material under framework/kpdm: **CC BY 4.0**. See [licensing by path](LICENSING.md).

KPDM remains **0.5.0-rc.2 candidate**, with **0.4.0 trial / conditional-pass** as the latest accepted baseline. Software release is not framework acceptance.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

See the [collaboration policy](policy/collaboration.md) and proposed [human–AI knowledge creation discipline](framework/kpdm/extensions/人机协作知识创作学.md). Framework acceptance and independent reader validation remain separate from software publication.
