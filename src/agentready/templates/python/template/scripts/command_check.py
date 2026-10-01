#!/usr/bin/env python3
"""Check that published project commands match the generated CLI."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from project import COMMANDS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = re.compile(r"(?:uv run )?python scripts/project\.py ([a-z-]+)")


def check(root: Path) -> None:
    required = {
        "README.md": {"bootstrap", "check", "verify"},
        "AGENTS.md": {"bootstrap", "check", "verify"},
        "docs/generated/CODEBASE_MAP.md": {"bootstrap", "check", "verify"},
    }
    for relative, essential in required.items():
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe command documentation: {relative}")
        text = path.read_text(encoding="utf-8")
        named = set(REFERENCE.findall(text))
        unknown = named - set(COMMANDS)
        absent = essential - named
        if unknown or absent:
            raise ValueError(
                f"{relative} command drift: unknown {sorted(unknown)}, missing {sorted(absent)}"
            )
    for base in (root / ".agents/skills", root / "docs/agent"):
        for path in base.rglob("*.md"):
            unknown = set(REFERENCE.findall(path.read_text(encoding="utf-8"))) - set(COMMANDS)
            if unknown:
                raise ValueError(f"{path.relative_to(root)} unknown commands: {sorted(unknown)}")


def main() -> int:
    try:
        check(ROOT)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"command check: {exc}", file=sys.stderr)
        return 1
    print("documented project commands are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
