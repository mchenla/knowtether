"""Project-only hook registration. Preserve other handlers and never grant trust."""
from __future__ import annotations

import base64
import datetime
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile

from .engine import POLICY_VERSION, read_object, safe_path
from .hooks import EVENTS

MARKER = "kpdm-hooks-v1"
HOST_PATHS = {"codex": ".codex/hooks.json", "claude": ".claude/settings.local.json"}


def atomic_json(path: Path, value: dict, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if exclusive:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
        return
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".kpdm-tmp-", delete=False) as stream:
            name = stream.name
            stream.write(text)
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def _ours(handler) -> bool:
    if not isinstance(handler, dict):
        return False
    args = handler.get("args")
    if args is None:
        command = handler.get("command", "")
        if not isinstance(command, str):
            return False
        try:
            args = shlex.split(command)
            # Windows shell-independent wrapper generated below. Decode data,
            # never execute it, when locating our reserved ownership marker.
            if args and args[0].lower() == "powershell.exe" and "-EncodedCommand" in args:
                pos = args.index("-EncodedCommand")
                inner = base64.b64decode(args[pos + 1], validate=True).decode("utf-16le")
                args = shlex.split(inner)
        except (ValueError, IndexError, UnicodeError):
            return False
    # This exact adjacent option/value is reserved for this adapter. Do not
    # match marker prefixes or unrelated values elsewhere in an argument list.
    return (isinstance(args, list) and any(
        args[i] == "--adapter-id" and args[i + 1] == MARKER
        for i in range(len(args) - 1)))


def _handler(root: Path, event: str, host: str) -> dict:
    repo_entry = Path(__file__).resolve().parents[1] / "hooks/entry.py"
    args = ([str(repo_entry)] if repo_entry.is_file() else ["-m", "kpdm_hooks"])
    args += ["hook", "--root", str(root), "--event", event, "--adapter-id", MARKER]
    if host == "claude":
        # Current Claude exec form avoids any shell interpolation.
        return {"type": "command", "command": sys.executable, "args": args, "timeout": 10}
    argv = [sys.executable, *args]
    if os.name == "nt":
        # Codex can inherit PowerShell or fall back to cmd.exe. This fixed
        # wrapper works in either; all project paths stay inside literal args.
        inner = "& " + " ".join("'" + part.replace("'", "''") + "'" for part in argv)
        encoded = base64.b64encode(inner.encode("utf-16le")).decode("ascii")
        command = "powershell.exe -NoLogo -NoProfile -NonInteractive -EncodedCommand " + encoded
    else:
        command = shlex.join(argv)
    handler = {"type": "command", "command": command, "timeout": 10}
    if event == "UserPromptSubmit":
        handler["additionalContextLimit"] = 0  # reading.py bounds the pack.
    return handler


def configure(root: Path, host: str, remove: bool = False, dry_run: bool = False) -> dict:
    root = root.resolve(strict=True)
    path = safe_path(root, HOST_PATHS[host])
    config_path = None if remove else safe_path(root, ".kpdm/config.json")
    old = read_object(path) if path.exists() else {}
    # Clone so callers never observe a half mutation.
    new = json.loads(json.dumps(old))
    hooks = new.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Existing hooks must be an object; no files changed")
    for event in EVENTS:
        groups = hooks.get(event, [])
        if not isinstance(groups, list):
            raise ValueError("Existing event groups must be arrays; no files changed")
        kept = []
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise ValueError("Malformed existing hook group; no files changed")
            original = group["hooks"]
            handlers = [handler for handler in original if not _ours(handler)]
            # Preserve empty third-party groups too.
            if handlers or not any(_ours(handler) for handler in original):
                kept.append({**group, "hooks": handlers})
        if not remove:
            kept.append({"hooks": [_handler(root, event, host)]})
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event, None)
    if not hooks:
        new.pop("hooks", None)
    project_config = read_object(config_path) if config_path is not None and config_path.exists() else None
    if not remove and project_config is not None and project_config.get("schema_version") != 1:
        raise ValueError("Unsupported existing KPDM config; no files changed")
    changed = new != old
    result = {"host": host, "action": "uninstall" if remove else "install",
              "dry_run": dry_run, "changed": changed, "config": str(path),
              "trust": "Review and trust hooks in the host; installation does not grant trust."}
    if dry_run:
        result["preview"] = new
        return result
    if changed:
        if path.exists():
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = safe_path(root, HOST_PATHS[host] + ".kpdm-hooks-backup-" + stamp)
            with backup.open("xb") as stream:
                stream.write(path.read_bytes())
            result["backup"] = str(backup)
        atomic_json(path, new)
    if not remove and project_config is None:
        atomic_json(config_path, {"schema_version": 1, "enabled": True,
                                  "policy_version": POLICY_VERSION}, exclusive=True)
    return result
