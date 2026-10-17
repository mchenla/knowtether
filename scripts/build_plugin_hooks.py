"""Reproducibly generate the three cross-platform plugin hook handlers."""
import argparse
import base64
import json
from pathlib import Path


def definition():
    hooks = {}
    for event in ("SessionStart", "UserPromptSubmit", "Stop"):
        # Only a fixed, reviewable bootstrap is encoded. Real code is in the
        # bundled run-windows.ps1; paths stay in env/argument values, not code.
        script = ("$p=$env:PLUGIN_ROOT; if (-not $p) { $p=$env:CLAUDE_PLUGIN_ROOT }; "
                  "& (Join-Path $p 'hooks/run-windows.ps1') -Event '" + event + "'; exit 0")
        encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
        handler = {"type": "command",
                   "command": 'sh "$PLUGIN_ROOT/hooks/run-posix.sh" ' + event,
                   "commandWindows": "powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand " + encoded,
                   "timeout": 10,
                   "statusMessage": "KnowTether: " + event}
        if event != "Stop":
            handler["additionalContextLimit"] = 1600
        hooks[event] = [{"hooks": [handler]}]
    return {"description": "KnowTether advisory hooks; bundled Python 3.10+ code, no pip install, no blocking.", "hooks": hooks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / "hooks/hooks.json"
    expected = json.dumps(definition(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            parser.exit(1, "Plugin hook definition is stale; run scripts/build_plugin_hooks.py\n")
    else:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(expected)


if __name__ == "__main__":
    main()
