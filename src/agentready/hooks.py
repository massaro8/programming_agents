"""Explicit repository-local hook recipes; never executes the supplied command."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agentready.local_paths import SECRET, local_path, read_json, write_json

CONFIG = "docs/agent/hooks.json"
EVIDENCE = "docs/work/evidence/hooks.json"
RULES = {
    "recursive-delete": r"(?i)(?:\brm\s+[^\n]*(?:-[a-z]*r|--recursive)|"
    r"\b(?:rmdir|rd)\s+[^\n]*/s|\bRemove-Item\b[^\n]*-Recurse)",
    "force-push": r"(?i)\bgit\b[^\n]*\bpush\b[^\n]*(?:--force\b|--force-with-lease\b|\s-f\b|\s\+)",
    "hard-reset": r"(?i)\bgit\b[^\n]*\breset\b[^\n]*--hard\b",
    "protected-push": r"(?i)\bgit\b[^\n]*\bpush\b",
}


def defaults() -> dict[str, Any]:
    return {
        "schema": 1,
        "hooks": {
            "safe-shell": {
                "enabled": False,
                "mode": "warn",
                "exclusions": [],
                "protected_branches": ["main", "master"],
            },
            "evidence-recorder": {"enabled": False, "capture_output": False},
        },
    }


def validate(data: dict[str, Any]) -> None:
    if set(data) != {"schema", "hooks"} or data["schema"] != 1:
        raise ValueError("unsupported hook configuration")
    if not isinstance(data["hooks"], dict) or set(data["hooks"]) != set(defaults()["hooks"]):
        raise ValueError("unsupported hook recipes")
    safe = data["hooks"]["safe-shell"]
    recorder = data["hooks"]["evidence-recorder"]
    if not isinstance(safe, dict) or set(safe) != set(defaults()["hooks"]["safe-shell"]):
        raise ValueError("invalid safe-shell configuration")
    if type(safe["enabled"]) is not bool or safe["mode"] not in ("warn", "block"):
        raise ValueError("invalid safe-shell enabled/mode")
    if not isinstance(safe["exclusions"], list) or not all(
        isinstance(v, str) and v in RULES for v in safe["exclusions"]
    ):
        raise ValueError("exclusions must name built-in rules")
    if not isinstance(safe["protected_branches"], list) or not all(
        isinstance(v, str) and re.fullmatch(r"[a-zA-Z0-9_./-]+", v)
        for v in safe["protected_branches"]
    ):
        raise ValueError("invalid protected branches")
    if not isinstance(recorder, dict) or set(recorder) != {"enabled", "capture_output"}:
        raise ValueError("invalid evidence-recorder configuration")
    if type(recorder["enabled"]) is not bool or recorder["capture_output"] is not False:
        raise ValueError("output capture is unsupported; capture_output must be false")


def configuration(root: Path) -> dict[str, Any]:
    path = local_path(root, CONFIG)
    data = read_json(root, CONFIG) if path.exists() else defaults()
    validate(data)
    return data


def configure(
    root: Path,
    name: str,
    *,
    enabled: bool | None = None,
    mode: str | None = None,
    exclusions: list[str] | None = None,
    branches: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    data = configuration(root)
    if name not in data["hooks"]:
        raise ValueError("unknown hook recipe")
    recipe = data["hooks"][name]
    if enabled is not None:
        recipe["enabled"] = enabled
    if name != "safe-shell" and any(v is not None for v in (mode, exclusions, branches)):
        raise ValueError("safety parameters apply only to safe-shell")
    for key, value in (
        ("mode", mode),
        ("exclusions", exclusions),
        ("protected_branches", branches),
    ):
        if value is not None:
            recipe[key] = value
    validate(data)
    if not dry_run:
        write_json(root, CONFIG, data)
    return data


def check_command(root: Path, command: str, branch: str | None = None) -> dict[str, Any]:
    """Conservative lexical preflight, not a shell sandbox or a security guarantee."""
    if not isinstance(command, str) or not command.strip() or len(command) > 8192:
        raise ValueError("command must be nonempty and at most 8192 characters")
    recipe = configuration(root)["hooks"]["safe-shell"]
    matches: list[str] = []
    if recipe["enabled"]:
        for name, pattern in RULES.items():
            if name in recipe["exclusions"] or not re.search(pattern, command):
                continue
            if name == "protected-push":
                # Unknown current branch fails conservatively; explicit target refs count too.
                targets = recipe["protected_branches"]
                mentions = any(
                    re.search(rf"(?<![\w/-])(?:refs/heads/)?{re.escape(v)}(?![\w/-])", command)
                    for v in targets
                )
                if branch is not None and branch not in targets and not mentions:
                    continue
            matches.append(name)
    return {
        "enabled": recipe["enabled"],
        "mode": recipe["mode"],
        "rules": matches,
        "allowed": not matches or recipe["mode"] == "warn",
    }


def record(root: Path, command: str, exit_status: int, work_id: str) -> dict[str, Any]:
    """Record only executable identity, not arguments, output, environment or shell history."""
    if not configuration(root)["hooks"]["evidence-recorder"]["enabled"]:
        raise ValueError("evidence-recorder is disabled")
    if not re.fullmatch(r"W[0-9]{3,}", work_id):
        raise ValueError("invalid work ID")
    items = list(local_path(root, "docs/work").glob(f"{work_id}-*.md"))
    if len(items) != 1:
        raise ValueError("work item missing or ambiguous")
    local_path(root, items[0].relative_to(root.absolute()).as_posix())
    tokens = shlex.split(command, posix=True)
    if (
        not tokens
        or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", tokens[0])
        or SECRET.search(tokens[0])
    ):
        raise ValueError("command must start with an executable name; arguments are not stored")
    if type(exit_status) is not int or not -(2**31) <= exit_status <= 2**32 - 1:
        raise ValueError("invalid exit status")
    entry = {
        "command": tokens[0],
        "exit_status": exit_status,
        "work_id": work_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "external-report",
    }
    path = local_path(root, EVIDENCE)
    journal = read_json(root, EVIDENCE) if path.exists() else {"schema": 1, "entries": []}
    if (
        set(journal) != {"schema", "entries"}
        or journal["schema"] != 1
        or not isinstance(journal["entries"], list)
    ):
        raise ValueError("invalid evidence journal")
    if len(journal["entries"]) >= 200:
        raise ValueError("evidence journal full; archive it explicitly")
    journal["entries"].append(entry)
    write_json(root, EVIDENCE, journal)
    return entry


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("list")
    commands.add_parser("status")
    view = commands.add_parser("inspect")
    view.add_argument("name", choices=tuple(defaults()["hooks"]))
    for action in ("configure", "enable", "disable"):
        p = commands.add_parser(action)
        p.add_argument("name", choices=tuple(defaults()["hooks"]))
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--mode", choices=("warn", "block"))
        p.add_argument("--exclude", nargs="*", choices=tuple(RULES))
        p.add_argument("--protected-branches", nargs="*")
    preflight = commands.add_parser("check")
    preflight.add_argument("shell_command")
    preflight.add_argument("--branch")
    evidence = commands.add_parser("record")
    evidence.add_argument("shell_command")
    evidence.add_argument("--exit-status", type=int, required=True)
    evidence.add_argument("--work", required=True)
    args = parser.parse_args(argv)
    root = root or Path(__file__).resolve().parents[1]
    try:
        if args.action == "list":
            payload = defaults()
        elif args.action == "status":
            payload = configuration(root)
        elif args.action == "inspect":
            payload = {
                "name": args.name,
                "configuration": configuration(root)["hooks"][args.name],
                "rules": RULES if args.name == "safe-shell" else "executable identity only",
            }
        elif args.action in ("configure", "enable", "disable"):
            payload = configure(
                root,
                args.name,
                enabled={"enable": True, "disable": False}.get(args.action),
                mode=args.mode,
                exclusions=args.exclude,
                branches=args.protected_branches,
                dry_run=args.dry_run,
            )
        elif args.action == "check":
            payload = check_command(root, args.shell_command, args.branch)
        else:
            payload = record(root, args.shell_command, args.exit_status, args.work)
        print(json.dumps(payload, indent=2))
        return 0 if payload.get("allowed", True) else 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"hooks: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
