"""Standalone offline CloudFormation engineering commands."""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FORWARDED = ("work", "route", "skill", "hooks", "checkpoint", "resume", "context", "status")

def run(stage, command):
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        print(f"{stage} failed (exit {result.returncode})", file=sys.stderr)
    return result.returncode

def governance_commands():
    return [("work registry", [sys.executable, "scripts/work_registry.py", "check"]), ("skills", [sys.executable, "scripts/skill_check.py"]), ("codebase map", [sys.executable, "scripts/generate_codebase_map.py", "--check"])]

def check_commands():
    from infrastructure_checks import commands
    return governance_commands() + commands(ROOT)

def execute(task, arguments=None):
    arguments = arguments or []
    if task == "bootstrap":
        from infrastructure_tools import prepare_tools
        prepare_tools(ROOT)
        if execute("sync"):
            return 1
        return execute("check")
    if task == "sync":
        from work_registry import sync
        from local_paths import local_path
        from skill_qa import claude_view
        sync(ROOT)
        for canonical in local_path(ROOT, ".agents/skills").glob("*/SKILL.md"):
            canonical = local_path(ROOT, canonical.relative_to(ROOT).as_posix())
            adapter = local_path(ROOT, f".claude/skills/{canonical.parent.name}/SKILL.md")
            adapter.parent.mkdir(parents=True, exist_ok=True)
            adapter.write_text(claude_view(canonical.read_text(encoding="utf-8"), canonical.parent.name), encoding="utf-8", newline="\n")
        return run("codebase map", [sys.executable, "scripts/generate_codebase_map.py"])
    if task in FORWARDED:
        if task in ("checkpoint", "resume"):
            from continuity import main
            return main([task, *arguments], ROOT)
        if task == "skill":
            from skill_qa import main
            return main(arguments, ROOT)
        if task == "hooks":
            from hooks import main
            return main(arguments, ROOT)
        modules = {"work": "work_registry", "route": "skill_routes", "context": "context", "status": "status"}
        return __import__(modules[task]).main(arguments)
    if task == "verify" and arguments:
        from work_registry import read_work
        items = [item for item in read_work(ROOT) if item.work_id == arguments[0]]
        if len(items) != 1:
            raise ValueError("Unknown work ID: " + arguments[0])
        item = items[0]
        if item.kind == "DOCS":
            from verification import record
            return record(ROOT, item.work_id, item.kind, governance_commands(), runner=run)
    commands = check_commands()
    if task == "verify" and arguments:
        from verification import record
        from work_registry import read_work
        item = next(item for item in read_work(ROOT) if item.work_id == arguments[0])
        return record(ROOT, arguments[0], item.kind, commands, runner=run)
    for stage, command in commands:
        if run(stage, command):
            return 1
    return 0

def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] in FORWARDED:
        return execute(arguments[0], arguments[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "verify", "sync", "bootstrap", *FORWARDED))
    parser.add_argument("--work")
    args = parser.parse_args(arguments)
    try:
        return execute(args.command, [args.work] if args.work else [])
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
if __name__ == "__main__":
    raise SystemExit(main())
