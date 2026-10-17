# KnowTether (知据)

[中文文档](README.md)

A local, warning-only Hook adapter for knowledge writing in Codex and Claude Code. It reminds agents to identify the audience and purpose, distinguish facts from inference, preserve sources and limitations, and keep human acceptance separate from release approval.

Version `0.1.1`; Python 3.10+; standard library only. Claude Code requires 2.1.139+ for the generated exec-form hooks. This adapter references **KPDM 0.5.0-rc.2 candidate**. The latest accepted framework baseline remains **0.4.0 trial / conditional-pass**.

## Install

Public downloads require no GitHub account: [Python wheel](https://github.com/mchenla/knowtether/releases/download/v0.1.1/kpdm_hooks-0.1.1-py3-none-any.whl), [source ZIP](https://github.com/mchenla/knowtether/releases/download/v0.1.1/knowtether-0.1.1-source.zip), [SHA-256 checksums](https://github.com/mchenla/knowtether/releases/download/v0.1.1/SHA256SUMS), and [release notes](https://github.com/mchenla/knowtether/releases/latest).

```bash
python -m pip install "https://github.com/mchenla/knowtether/releases/download/v0.1.1/kpdm_hooks-0.1.1-py3-none-any.whl"
knowtether --version
```

The primary command is `knowtether`. For compatibility, the Python distribution remains `kpdm-hooks`; the `kpdm-hooks` command, `kpdm_hooks` module and existing hook registrations remain supported. Add `--upgrade` to the install command to update an earlier version.

Alternatively, install from source:

```bash
git clone https://github.com/mchenla/knowtether.git
cd knowtether
python -m pip install .
```

From your writing project, choose `codex` or `claude`:

```bash
knowtether install --root . --host codex --dry-run
knowtether install --root . --host codex
```

The installer merges project configuration and backs up existing configuration before changing it: `.codex/hooks.json` for Codex and `.claude/settings.local.json` for Claude Code. It also creates `.kpdm/config.json` if missing. In Codex, review and trust the configuration with `/hooks`; installation does not grant trust or globally enable Hooks. Claude Code requires support for the current `command` + `args` exec form; upgrade older versions if needed. Restart or reload the session as required by your host. See the official [Codex Hooks](https://learn.chatgpt.com/docs/hooks) and [Claude Code Hooks](https://code.claude.com/docs/en/hooks) protocols.

`SessionStart` supplies conditional guidance, `UserPromptSubmit` matches likely knowledge tasks, and `Stop` checks the last assistant message plus a worksheet bound to the current session. Short tasks can use guidance without creating a worksheet.

## Optional worksheet and checks

```bash
knowtether init --root . --session-id YOUR_CURRENT_SESSION_ID
knowtether context --root .
knowtether check --root . --artifact article.md
knowtether check --root . --artifact article.md --strict
```

Session IDs can also come from supported environment variables. Fill the eight worksheet fields in `.kpdm/work.json`; see [the example](examples/work.json). Review the current delegation before using `bind`; binding does not renew human authorization. `close` disables the worksheet. All commands also work through `python -m kpdm_hooks`.

Default checks report warnings without blocking. Strict checks return `1` for warning/error findings; CLI execution errors return `2`. Host Hooks return `0` and do not approve or block actions.

```bash
knowtether uninstall --root . --host codex --dry-run
knowtether uninstall --root . --host codex
```

Uninstall removes this project's handlers while preserving unrelated configuration.

## Limits

Core-6 describes functional coverage, not six required headings or a fixed sequence. Exploratory work may leave its central claim undecided. Missing warnings do not establish truth, adequate citations, legal permission, reader comprehension, or release readiness. Public knowledge products require the framework's Q3 checks, independent review, reader tasks, and a separate human release decision.

Local tests, protocol fixtures, and shell execution of generated commands do not establish end-to-end operation in actual host applications. Real Codex and Claude Code integration still needs host-level verification. Examples are fictional teaching materials, with no real research data or reader results. The example worksheet intentionally retains open issues and an unverified source record; do not invent verification to silence warnings.

See [rule mapping](docs/rules.md), [design](docs/design.md), [contributing](CONTRIBUTING.md), and [security](SECURITY.md).

Original project code and adaptation text are [MIT licensed](LICENSE), copyright `2026 MC (mchenla)`. The upstream KPDM specification has not been relicensed as a whole. See [NOTICE](NOTICE).
