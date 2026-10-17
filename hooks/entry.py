"""Repository entry point; keeps generated hook commands independent of shell cwd."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kpdm_hooks.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
