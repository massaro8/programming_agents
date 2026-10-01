#!/usr/bin/env python3
"""Summarize local project health without running tests or changing files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
from work_registry import RegistryError, read_work  # noqa: E402
from work_registry import check as work_check  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _health(check: object, root: Path) -> str:
    try:
        check(root)
    except (ValueError, OSError, UnicodeError, KeyError) as exc:
        return f"FAIL: {exc}"
    return "OK"


def _architecture_health(root: Path) -> str:
    from architecture_check import check

    del root  # The generated checker owns its repository root.
    errors = check()
    return "OK" if not errors else "FAIL: " + "; ".join(errors)


def _map_health(root: Path) -> str:
    from generate_codebase_map import render

    path = root / "docs/generated/CODEBASE_MAP.md"
    if not path.is_file() or path.read_text(encoding="utf-8") != render():
        return "FAIL: stale or missing map"
    return "OK"


def summarize(root: Path) -> dict[str, object]:
    """Report registry and deterministic structural-check results only."""
    from module_knowledge import check as module_check
    from skill_check import check as skill_check

    map_text = (root / "docs/generated/CODEBASE_MAP.md").read_text(encoding="utf-8")
    profile_line = next(
        (line for line in map_text.splitlines() if line.startswith("Profile: `")), ""
    )
    profile = profile_line.removeprefix("Profile: `").removesuffix("`") or "unknown"
    works = read_work(root)
    counts = Counter(work.status for work in works)
    return {
        "profile": profile,
        "work": {
            status: counts[status]
            for status in ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE")
        },
        "next_ready": next(
            (work.work_id for work in works if work.status == "READY"), "NO_READY_WORK"
        ),
        "work_indexes": _health(work_check, root),
        "architecture": _architecture_health(root),
        "module_knowledge": _health(module_check, root),
        "skills": _health(skill_check, root),
        "codebase_map": _map_health(root),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = summarize(ROOT)
    except (RegistryError, OSError, UnicodeError) as exc:
        print(f"status: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result, sort_keys=True))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
