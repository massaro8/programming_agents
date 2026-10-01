#!/usr/bin/env python3
"""Resolve the smallest useful work context without changing the repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from skill_routes import ROUTES  # noqa: E402
from work_registry import RegistryError, Work, read_work  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def resolve(root: Path, work_id: str | None = None) -> dict[str, object]:
    """Return deterministic pointers, not a speculative implementation plan."""
    items = read_work(root)
    item: Work | None
    if work_id is None:
        item = next((work for work in items if work.status == "READY"), None)
    else:
        item = next((work for work in items if work.work_id == work_id), None)
        if item is None:
            raise RegistryError(f"unknown work ID: {work_id}")
    if item is None:
        return {"status": "NO_READY_WORK"}
    route = ROUTES[item.kind]
    return {
        "work_id": item.work_id,
        "type": item.kind,
        "status": item.status,
        "title": item.title,
        "specification": f"docs/work/{item.filename}",
        "skill": route["skill"],
        "workflow": route["workflow"],
        "standards": list(route["standards"]),
        "map": "docs/generated/CODEBASE_MAP.md",
        "likely_module": "UNKNOWN",
        "verify": "uv run python scripts/project.py check",
        "actionable": item.status == "READY",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id", nargs="?")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = resolve(ROOT, args.work_id)
    except (RegistryError, OSError, UnicodeError) as exc:
        print(f"context: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result, sort_keys=True))
    elif result["status"] == "NO_READY_WORK":
        print("NO_READY_WORK")
    else:
        for key, value in result.items():
            if key == "standards":
                value = ", ".join(value)
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
