"""Shared Codex/Claude JSON protocol; no network, writes, transcripts or blocking."""
from __future__ import annotations

from pathlib import Path

from .engine import (check_work, context, knowledge_prompt, lint_text, load_work,
                     read_object, safe_path)

EVENTS = ("SessionStart", "UserPromptSubmit", "Stop")


def handle(event: dict, root: Path, expected_event: str) -> dict:
    if not isinstance(event, dict) or expected_event not in EVENTS or event.get("hook_event_name") != expected_event:
        raise ValueError("Invalid hook event")
    config_path = safe_path(root, ".kpdm/config.json")
    if not config_path.exists():
        return {}
    config = read_object(config_path)
    if config.get("enabled") is False:
        return {}
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported config version")
    if expected_event == "SessionStart":
        note = context()
        state = load_work(root)
        if state and state.get("enabled") is not False and state.get("session_id") != event.get("session_id"):
            note += "\n[HANDOFF] 发现旧会话工作单，核对本次委托后再bind；旧记录不构成当前授权。"
        return {"hookSpecificOutput": {"hookEventName": expected_event, "additionalContext": note}}
    if expected_event == "UserPromptSubmit":
        if not knowledge_prompt(event.get("prompt", "")):
            return {}
        return {"hookSpecificOutput": {"hookEventName": expected_event, "additionalContext": context()}}
    if event.get("stop_hook_active") is True:
        return {}
    notes = []
    state = load_work(root)
    session_id = event.get("session_id")
    bound = (state and state.get("enabled") is not False and isinstance(session_id, str)
             and bool(session_id) and state.get("session_id") == session_id)
    if bound:
        notes.extend(check_work(state, session_id))
    text = event.get("last_assistant_message")
    if isinstance(text, str) and (bound or knowledge_prompt(text)):
        notes.extend(lint_text(text))
    if not notes:
        return {}
    return {"systemMessage": "[KPDM advisory] " + "\n".join(
        "[" + item["code"] + "] " + item["message"] for item in notes[:8])
        + "\n仅机械/启发式提示，未判定内容真实性或批准发布。"}
