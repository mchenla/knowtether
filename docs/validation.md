# Validation records

## 0.2.1: actual host discovery

On Codex CLI 0.163.0-alpha.10.2, the 0.2.0 package installed but the host reported no plugin hooks. An isolated A/B check found that root plugin.json shadowed the compatibility manifest while the host ignored its hook extension. Version 0.2.1 uses only .codex-plugin/plugin.json and hooks/hooks.json. The isolated checker now calls the real app-server hooks/list API and requires all three plugin event entries before command checks. It never changes trust or copies credentials.

The updated isolated install discovered SessionStart, UserPromptSubmit and Stop as enabled, untrusted plugin hooks with no loading errors; all three cached commands passed. Local Windows regression: 90 tests, 89 passed and 1 POSIX-only test skipped. Host discovery is distinct from trust and lifecycle execution; those require a reviewed, trusted installation and a live session.

## 0.2.0: Codex plugin and repository marketplace

The installed local Codex CLI was `0.163.0-alpha.10.2`. A fresh test HOME inside the project was used; the user's active Codex configuration, credentials and hook trust were not changed. The real CLI registered a local fixture marketplace, installed `knowtether@knowtether` version `0.2.0`, and listed it as installed/enabled. The fixture used a copy of the actual public plugin components with a local source entry. The downloaded GitHub source path is checked separately before release.

All three hook commands from the installed cache were executed with fixture events against a new project that had no `.kpdm` directory. The skill was present, startup/prompt returned context, Stop returned only a warning, and no project files were created. This verifies installation and installed-command execution; it does not mean the interactive host's lifecycle or trust UI was tested.

New regression cases cover manifest consistency, contained component references, project defaults/disable settings, legacy-registration deduplication, event.cwd isolation, malformed events, guard against Stop continuation, and cross-platform launchers. Windows paths with spaces, Chinese characters, apostrophes, ampersands, dollar signs and percent signs were exercised through both cmd and PowerShell. POSIX runtime-present/runtime-missing checks run on Linux in CI. The original rule/CLI suite is retained.

Local Windows run: 90 tests ran successfully, with the POSIX-only launcher test skipped (89 passed, 1 skipped). The matching 0.2.0 wheel was built and installed in the project's virtual environment; both CLI names returned 0.2.0.

The reproducible install checker is `python scripts/smoke_codex_plugin.py --home <new-test-directory>`. Use `--source mchenla/knowtether` to test the exact public two-command flow in an isolated HOME. It never copies credentials, modifies trust or runs a model turn. Check the actual Actions run and release notes for the release commit; a configured matrix alone is not proof of a successful run.

## 0.1.1: KnowTether naming release

This release adds the KnowTether name, the `knowtether` command alias and direct public downloads. The rule engine, legacy command, Python distribution and installed-hook ownership markers remain compatible. The release is checked with the existing regression suite, an isolated wheel installation, both command names, and the Windows/Linux Python matrix in Actions. See the actual run results for the release commit and the release notes; these mechanical checks do not establish new semantic validation.

## 0.1.0

Checked on 2026-10-17 using Windows and Python 3.13. Automated tests cover rule consistency, session isolation, malformed input, path traversal, size limits, host JSON fixtures, non-blocking Stop output, installation preservation, repeated installs, uninstall, CLI exit codes and generated command execution.

Final local run: 78 tests passed, including the filesystem symlink checks. A restricted run also passed 76 tests with 2 symlink checks skipped for Windows permissions; the final run used sufficient local privileges to exercise those two checks.

The generated Codex command was executed through both PowerShell and the Windows cmd fallback. The Claude command was executed directly with its argument vector. A wheel was built and installed in a project-specific virtual environment. The isolated Python invocation verifies the installed package rather than importing from the source checkout.

GitHub Actions defines additional Windows/Linux and Python 3.10/3.13 checks. A configured matrix is not a completed run; inspect the actual Actions result for a commit.

These are mechanical and protocol checks. They do not establish that the host has discovered or trusted a hook, that an agent follows every reminder, that a cited source is true, or that knowledge quality improves for real readers. No full Codex/Claude host-session evaluation, independent domain review, user study or effect-size claim is recorded for this release.

## Evaluation still needed

1. Start real trusted Codex and Claude sessions and confirm all three event callbacks, including resume/compact behavior where supported.
2. Compare matched knowledge tasks with and without guidance; have domain reviewers assess factual support and readers perform declared tasks.
3. Record false positives and false negatives for prompt matching and text hints across Chinese/English requests, technical explanations and ordinary code maintenance.
4. Test adversarial or contradictory work records; measure useful review findings separately from metadata completeness.
5. Use those results to adjust rules while preserving unknowns, candidate status and human decisions.

The source identities used for this adaptation are recorded in [source-map.json](../policy/source-map.json). The original framework remains outside this repository and keeps its own version, status and rights.
