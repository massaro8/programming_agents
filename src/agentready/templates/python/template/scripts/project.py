#!/usr/bin/env python3
"""Run the project's standard local development tasks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    "bootstrap",
    "check",
    "verify",
    "package-check",
    "sync",
    "next",
    "context",
    "status",
    "module",
)


def run(stage: str, command: list[str]) -> int:
    try:
        result = subprocess.run(command, cwd=ROOT, check=False)
    except OSError as exc:
        print(f"{stage} failed ({' '.join(command)}): {exc}", file=sys.stderr)
        return 1
    if result.returncode:
        print(
            f"{stage} failed (exit {result.returncode}): {' '.join(command)}",
            file=sys.stderr,
        )
    return result.returncode


def check_commands(uv: str) -> list[tuple[str, list[str]]]:
    return [
        ("work registry", [uv, "run", "--locked", "python", "scripts/work_registry.py", "check"]),
        ("architecture", [uv, "run", "--locked", "python", "scripts/architecture_check.py"]),
        (
            "module knowledge",
            [uv, "run", "--locked", "python", "scripts/module_knowledge.py", "check"],
        ),
        ("skills", [uv, "run", "--locked", "python", "scripts/skill_check.py"]),
        ("commands", [uv, "run", "--locked", "python", "scripts/command_check.py"]),
        (
            "codebase map",
            [uv, "run", "--locked", "python", "scripts/generate_codebase_map.py", "--check"],
        ),
        ("format", [uv, "run", "--locked", "ruff", "format", "--check", "."]),
        ("lint", [uv, "run", "--locked", "ruff", "check", "."]),
        ("types", [uv, "run", "--locked", "mypy", "src"]),
        ("tests", [uv, "run", "--locked", "pytest"]),
    ]


def execute(task: str, arguments: list[str] | None = None) -> int:
    arguments = arguments or []
    if task in ("context", "next"):
        from context import main as context_main

        return context_main(arguments if task == "context" else ["--format", "text"])
    if task == "status":
        from status import main as status_main

        return status_main(arguments)
    if task == "module":
        from module_knowledge import main as module_main

        return module_main(arguments)
    if task == "sync":
        from work_registry import sync

        try:
            sync(ROOT)
        except (ValueError, OSError, UnicodeError) as exc:
            print(f"sync failed: {exc}", file=sys.stderr)
            return 1
        return run("codebase map", [sys.executable, "scripts/generate_codebase_map.py"])

    uv = shutil.which("uv")
    if uv is None:
        print("uv is required; install uv and retry", file=sys.stderr)
        return 1

    if task == "bootstrap":
        if run("dependency sync", [uv, "sync", "--all-groups"]):
            return 1
        if not (ROOT / "uv.lock").is_file():
            print("bootstrap failed: uv sync did not create uv.lock", file=sys.stderr)
            return 1
        return execute("check")
    elif task == "check":
        commands = check_commands(uv)
    elif task == "verify":
        result = execute("check")
        if result:
            return result
        commands = [("build", [uv, "build"])]
    elif task == "package-check":
        from package_check import check

        return check(ROOT, uv)
    else:
        raise ValueError(f"unsupported task: {task}")

    for stage, command in commands:
        if run(stage, command):
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in COMMANDS[:6]:
        commands.add_parser(name)
    context = commands.add_parser("context")
    target = context.add_mutually_exclusive_group()
    target.add_argument("--next", action="store_true")
    target.add_argument("work_id", nargs="?")
    context.add_argument("--format", choices=("text", "json"), default="text")
    status = commands.add_parser("status")
    status.add_argument("--format", choices=("text", "json"), default="text")
    module = commands.add_parser("module")
    module.add_argument("action", choices=("new", "check"))
    module.add_argument("name", nargs="?")
    module.add_argument("--responsibility")
    args = parser.parse_args(argv)
    if args.command == "context":
        parameters = ["--format", args.format]
        if args.work_id:
            parameters.append(args.work_id)
        return execute("context", parameters)
    if args.command == "status":
        return execute("status", ["--format", args.format])
    if args.command == "module":
        parameters = [args.action]
        if args.name:
            parameters.append(args.name)
        if args.responsibility:
            parameters.extend(["--responsibility", args.responsibility])
        return execute("module", parameters)
    return execute(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
