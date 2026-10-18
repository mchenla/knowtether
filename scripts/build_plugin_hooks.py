"""Reproducibly generate the three cross-platform plugin hook handlers."""
import argparse
import json
from pathlib import Path


def definition():
    hooks = {}
    for event in ("SessionStart", "UserPromptSubmit", "Stop"):
        # Delayed expansion occurs only in the inner cmd; percent signs in the
        # resulting path are not expanded again. The batch disables it on entry.
        handler = {"type": "command",
                   "command": 'sh "$PLUGIN_ROOT/hooks/run-posix.sh" ' + event,
                   "commandWindows": 'cmd.exe /d /v:on /c "!PLUGIN_ROOT!\\hooks\\run-windows.cmd" ' + event,
                   "timeout": 10,
                   "statusMessage": "KnowTether: " + event}
        if event != "Stop":
            # The reader enforces an 18,000-character cap without cutting sections.
            handler["additionalContextLimit"] = 0 if event == "UserPromptSubmit" else 1600
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
