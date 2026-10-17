"""Bundled plugin entry: use event.cwd, never the installed plugin cache as a project."""
from pathlib import Path
import json
import sys

# Keep the installed bundle read-only, including Python bytecode caches.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kpdm_hooks.engine import MAX_BYTES
from kpdm_hooks.hooks import EVENTS, handle


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        expected = sys.argv[1] if len(sys.argv) == 2 else ""
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("oversize")
        event = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(event, dict) or expected not in EVENTS:
            raise ValueError("invalid event")
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not Path(cwd).is_absolute():
            raise ValueError("missing absolute project cwd")
        root = Path(cwd).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("project cwd is not a directory")
        result = handle(event, root, expected, plugin=True)
    except (OSError, ValueError, TypeError, AttributeError, RecursionError):
        result = {"systemMessage": "[KnowTether CHECK_SKIPPED] 输入或项目配置异常，已跳过检查；未阻断操作。"}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
