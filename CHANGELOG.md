# Changelog

## 0.3.1 - 2026-10-17

- Explain KPDM in full and introduce KnowTether through seven plain questions: identity, purpose, contents, environment, audience, timing and use.
- Shorten Chinese/English homepages and move detailed project CLI instructions into docs/cli.md.
- Publish a scoped collaboration-behavior audit and reproducible synthetic Stop examples, including known misses.
- State the observed gap in automatic bundled-specification reading; do not claim semantic, grammar, style or watermark guarantees.
- Keep Hook commands, runtime rules, skill guidance and the KPDM specification snapshot unchanged.

## 0.3.0 - 2026-10-17

- Publish the author-licensed KPDM framework snapshot under CC BY 4.0; retain MIT for KnowTether software and adaptation material.
- Bundle specifications, templates, machine models/schemas and examples, selected baseline history and source fingerprints with the Codex plugin.
- Convert Obsidian links for standalone reading and mark unavailable private references.
- Link the knowledge-work skill to bundled framework documents and provide a separate framework ZIP.
- Preserve KPDM candidate/baseline status, existing installation commands and all three advisory Hook definitions.

## 0.2.1 - 2026-10-17

- Fix hook discovery on Codex 0.163 alpha by using the compatibility manifest alone and the standard hooks/hooks.json path.
- Verify all three hooks through the actual app-server hooks/list API during the isolated install check, before executing their commands.

## 0.2.0 - 2026-10-17

- Add Codex plugin manifests, a GitHub-backed marketplace catalog, a knowledge-work skill and an original SVG icon.
- Bundle Python code with cross-platform hooks; no separate pip install or per-project initialization is needed for plugin guidance.
- Read records from the current event's project cwd, respect explicit project disable settings and yield to existing project registrations for the same event.
- Add real isolated Codex CLI install checks and tests for cached plugin hooks, paths with spaces/Unicode/shell characters and missing runtimes.
- Retain the Python CLI, legacy command and worksheet format.

## 0.1.1 - 2026-10-17

- Name the project **KnowTether (知据)** and move the public repository to `mchenla/knowtether`.
- Add `knowtether` as the primary command; keep the `kpdm-hooks` distribution, command, module and installed-hook markers compatible.
- Add direct public downloads for the wheel, source archive and SHA-256 checksum.
- Include the product name and current software version in guidance and package metadata.

## 0.1.0 - 2026-10-17

- Add conditional knowledge-work guidance for Codex and Claude Code using SessionStart and UserPromptSubmit.
- Add advisory Stop checks without continuation, blocking, transcript access or automatic approval.
- Add optional session-bound worksheets, version/decision consistency and claim/source records.
- Add conservative text hints and a manual check command with optional strict exit codes.
- Add project-only installers with preview, backups, idempotency and selective uninstall.
- Add Windows PowerShell/cmd execution coverage and Python packaging.

This initial software release is an advisory adaptation of KPDM. Host-session end-to-end behavior and improvements to real knowledge outputs require further evaluation.
