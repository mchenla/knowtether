"""Standard-library CLI. Hooks always return advisory JSON and exit zero."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from . import __version__
from .engine import (FIELDS, MAX_BYTES, POLICY_VERSION, check_project, context,
                     read_object, safe_path)
from .hooks import EVENTS, handle
from .install import atomic_json, configure


def emit(value) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Advisory KPDM hooks for knowledge outputs")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "bind", "close", "context", "check", "install", "uninstall", "hook"):
        command = sub.add_parser(name)
        command.add_argument("--root", type=Path, default=Path.cwd())
        if name in ("init", "bind"):
            command.add_argument("--session-id", default=os.getenv("CODEX_THREAD_ID") or os.getenv("CODEX_SESSION_ID") or os.getenv("CLAUDE_SESSION_ID"))
        if name == "check":
            command.add_argument("--artifact", help="UTF-8 text file inside the project")
            command.add_argument("--strict", action="store_true")
        if name in ("install", "uninstall"):
            command.add_argument("--host", required=True, choices=("codex", "claude"))
            command.add_argument("--dry-run", action="store_true")
        if name == "hook":
            command.add_argument("--event", required=True, choices=EVENTS)
            command.add_argument("--adapter-id", default="kpdm-hooks-v1")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Root must be an existing project directory")
        if args.action == "hook":
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Hook input exceeds 1 MB")
            event = json.loads(raw.decode("utf-8-sig"))
            emit(handle(event, root, args.event))
            return 0
        if args.action == "context":
            print(context())
            return 0
        if args.action in ("install", "uninstall"):
            emit(configure(root, args.host, args.action == "uninstall", args.dry_run))
            return 0
        if args.action == "check":
            notes = check_project(root, args.artifact)
            emit({"tool_version": __version__, "policy_version": POLICY_VERSION,
                  "scope": "record-consistency and text heuristics only",
                  "findings": notes, "semantic_review": "requires-human-review",
                  "release_approval": "not-assessed"})
            return int(args.strict and any(n["severity"] in ("warning", "error") for n in notes))
        dest = safe_path(root, ".kpdm/work.json")
        if args.action == "init":
            if not args.session_id:
                raise ValueError("Pass --session-id from the hook's session_id; no session was inferred")
            state = {"schema_version": 1, "enabled": True, "mode": "warn",
                     "session_id": args.session_id, "policy_version": POLICY_VERSION,
                     "input_version": "", "artifact_version": "draft-1", "status": "draft",
                     "allowed_write_roots": [str(root)], "open_issues": [],
                     "worksheet": {key: "" for key in FIELDS}}
            atomic_json(dest, state, exclusive=True)
        else:
            state = read_object(dest)
            if args.action == "bind":
                if not args.session_id:
                    raise ValueError("Pass --session-id after reviewing the current delegation")
                state.update(session_id=args.session_id, enabled=True, mode="warn")
            else:
                state["enabled"] = False
            atomic_json(dest, state)
        emit({"action": args.action, "work": str(dest)})
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        if args.action == "hook":
            # Do not echo event bodies, project paths, or arbitrary exception text into context.
            emit({"systemMessage": "[KPDM CHECK_SKIPPED] 输入或项目配置异常，本次检查已跳过；未阻断操作。"})
            return 0
        print("kpdm-hooks: " + str(exc), file=sys.stderr)
        return 2
