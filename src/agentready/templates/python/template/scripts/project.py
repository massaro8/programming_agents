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
    "skill",
    "hooks",
    "checkpoint",
    "resume",
    "work",
    "route",
)
FORWARDED = ("skill", "hooks", "checkpoint", "resume", "work", "route")
HELP = {
    "bootstrap": "Install dependencies and check the project",
    "check": "Run required repository checks",
    "verify": "Run checks and build the package",
    "package-check": "Validate the distributable package",
    "sync": "Refresh work indexes and the codebase map",
    "next": "Show context for the next READY work item",
    "context": "Show focused context for a work item",
    "status": "Show repository and work status",
    "module": "Create or check module knowledge",
    "skill": "Evaluate portable skills (skill eval --help)",
    "hooks": "Inspect or configure opt-in repository hooks",
    "checkpoint": "Save work continuity evidence",
    "resume": "Validate a saved checkpoint before continuing work",
    "work": "Create, list, check, sync, or transition work items",
    "route": "Resolve skill and model routing from task evidence",
}


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
    commands = [
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
    if (ROOT / "infrastructure").is_dir():
        from infrastructure_checks import commands as infrastructure_commands

        commands.extend(infrastructure_commands(ROOT))
    return commands


def execute(task: str, arguments: list[str] | None = None) -> int:
    arguments = arguments or []
    if task == "work":
        from work_registry import main as work_main

        return work_main(arguments)
    if task == "route":
        from skill_routes import main as route_main

        return route_main(arguments)
    if task == "skill":
        from skill_qa import main as skill_main

        return skill_main(arguments, ROOT)
    if task == "hooks":
        from hooks import main as hooks_main

        return hooks_main(arguments, ROOT)
    if task in ("checkpoint", "resume"):
        from continuity import main as continuity_main

        return continuity_main([task, *arguments], ROOT)
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
        from local_paths import local_path, read_text
        from skill_qa import claude_view
        from skill_routes import EXPECTED_SKILLS
        from work_registry import sync

        try:
            sync(ROOT)
            for name in EXPECTED_SKILLS:
                text = read_text(ROOT, f".agents/skills/{name}/SKILL.md")
                path = local_path(ROOT, f".claude/skills/{name}/SKILL.md")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(claude_view(text, name), encoding="utf-8", newline="\n")
        except (ValueError, OSError, UnicodeError) as exc:
            print(f"sync failed: {exc}", file=sys.stderr)
            return 1
        return run("codebase map", [sys.executable, "scripts/generate_codebase_map.py"])

    if task == "verify" and arguments:
        from verification import VerificationError, record
        from work_registry import read_work

        try:
            work_id = arguments[0]
            item = next((item for item in read_work(ROOT) if item.work_id == work_id), None)
            if item is None or item.status != "IN_PROGRESS":
                raise VerificationError("verification requires an IN_PROGRESS work item")
            uv = shutil.which("uv")
            if uv is None:
                raise VerificationError("uv is required")
            commands = check_commands(uv)
            if item.kind == "DOCS" and not (ROOT / "infrastructure").is_dir():
                commands = [
                    entry
                    for entry in commands
                    if entry[0] in {"work registry", "skills", "codebase map"}
                ]
            else:
                commands.append(("build", [uv, "build"]))
            return record(ROOT, work_id, item.kind, commands, run)
        except (ValueError, OSError) as exc:
            print(f"verification failed: {exc}", file=sys.stderr)
            return 1

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
        if (ROOT / "infrastructure").is_dir():
            from infrastructure_tools import prepare_tools

            try:
                prepare_tools(ROOT)
            except (ValueError, OSError) as exc:
                print(f"infrastructure bootstrap failed: {exc}", file=sys.stderr)
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
    arguments = list(sys.argv[1:] if argv is None else argv)
    # Let each capability parse its own options, including --help.
    if arguments and arguments[0] in FORWARDED:
        return execute(arguments[0], arguments[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in COMMANDS[:6]:
        command = commands.add_parser(name, help=HELP[name])
        if name == "verify":
            command.add_argument("--work")
    context = commands.add_parser("context", help=HELP["context"])
    target = context.add_mutually_exclusive_group()
    target.add_argument("--next", action="store_true")
    target.add_argument("work_id", nargs="?")
    context.add_argument("--format", choices=("text", "json"), default="text")
    status = commands.add_parser("status", help=HELP["status"])
    status.add_argument("--format", choices=("text", "json"), default="text")
    module = commands.add_parser("module", help=HELP["module"])
    module.add_argument("action", choices=("new", "check"))
    module.add_argument("name", nargs="?")
    module.add_argument("--responsibility")
    for name in FORWARDED:
        capability = commands.add_parser(name, help=HELP[name])
        capability.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(arguments)
    if args.command in FORWARDED:
        return execute(args.command, args.arguments)
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
    if args.command == "verify" and args.work:
        return execute("verify", [args.work])
    return execute(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
