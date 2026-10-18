#!/bin/sh
# Codex provides PLUGIN_ROOT; Claude Code provides CLAUDE_PLUGIN_ROOT.
# No pip install, downloads, or project writes.
plugin_root=${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}
if [ -z "$plugin_root" ]; then
    printf '%s\n' '{"systemMessage":"[KnowTether CHECK_SKIPPED] Plugin root is unavailable; hook skipped."}'
    exit 0
fi
for interpreter in python3 python; do
    if command -v "$interpreter" >/dev/null 2>&1 &&
       "$interpreter" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
        "$interpreter" -B "$plugin_root/hooks/plugin_entry.py" "$@"
        exit 0
    fi
done
printf '%s\n' '{"systemMessage":"[KnowTether PYTHON_REQUIRED] Install Python 3.10+ on PATH, then start a new session. Hook skipped."}'
exit 0
