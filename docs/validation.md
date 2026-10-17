# Validation record: 0.1.0

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
