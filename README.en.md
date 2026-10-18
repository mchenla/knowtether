# KnowTether (知据)

**Work with AI to turn sources and ideas into clearer, better-grounded articles and reports.**

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

Review and trust the three hooks in `/hooks`, then start a new session; restart the desktop app after installation. No separate pip install is needed. Ask in ordinary language without a manual marker. Matched knowledge requests now receive checked source passages before writing. Request detection can still miss cases; see the reading mechanism below.

To upgrade, run `codex plugin marketplace upgrade knowtether`, then `codex plugin add knowtether@knowtether`.

[Plugin guide](docs/codex-plugin.md) · [Python CLI and Claude Code](docs/cli.md)

## What is actually checked

Text checks cover citation placeholders, a narrow pattern of absolute research claims, independent-validation wording and concentrated stock phrases. Optional worksheets add record/version consistency checks.

These checks do not guarantee freedom from sycophancy, contrarianism, blind obedience, cherry-picking, factual errors, classification gaps or formulaic prose. There is no grammar correction or technical watermark detection/removal. A 0.3.0 live case exposed missing specification reads; 0.4.0 adds explicit minimum reading and collaboration guidance. Silence is not a quality pass. See the [capability audit](docs/capabilities.md) and [validation record](docs/validation.md).

## Open source

Software **0.4.0**; [release downloads](https://github.com/mchenla/knowtether/releases/latest). Software/adaptation material: **MIT**. Original KPDM material under framework/kpdm: **CC BY 4.0**. See [licensing by path](LICENSING.md).

KPDM remains **0.5.0-rc.2 candidate**, with **0.4.0 trial / conditional-pass** as the latest accepted baseline. Software release is not framework acceptance.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

Version 0.4.0 adds a bounded, hash-checked minimum reading pack before matched knowledge requests and explicit collaboration rules. See [reading evidence](docs/minimum-reading.md), [collaboration policy](policy/collaboration.md), and the proposed [human–AI knowledge creation discipline](framework/kpdm/extensions/人机协作知识创作学.md). Delivery does not prove compliance; semantic, grammar and watermark guarantees are not provided.
