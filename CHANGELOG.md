# Changelog

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
