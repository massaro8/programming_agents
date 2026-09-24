#!/usr/bin/env python3
"""Run the project's standard local development tasks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    try:
        return subprocess.run(command, cwd=ROOT, check=False).returncode
    except OSError as exc:
        print(f"could not run {' '.join(command)}: {exc}", file=sys.stderr)
        return 1


def execute(task: str) -> int:
    uv = shutil.which("uv")
    if uv is None:
        print("uv is required; install uv and retry", file=sys.stderr)
        return 1

    if task == "bootstrap":
        if run([uv, "sync", "--all-groups"]):
            return 1
        if not (ROOT / "uv.lock").is_file():
            print("bootstrap failed: uv sync did not create uv.lock", file=sys.stderr)
            return 1
        commands = [
            [uv, "run", "python", "scripts/work_registry.py", "check"],
            [uv, "run", "python", "scripts/architecture_check.py"],
        ]
    elif task == "check":
        commands = [
            [uv, "run", "python", "scripts/work_registry.py", "check"],
            [uv, "run", "python", "scripts/architecture_check.py"],
            [uv, "run", "ruff", "format", "--check", "."],
            [uv, "run", "ruff", "check", "."],
            [uv, "run", "mypy", "src"],
            [uv, "run", "pytest"],
        ]
    else:
        commands = []
        result = execute("check")
        if result:
            return result
        commands = [
            [uv, "build"],
            [uv, "run", "python", "scripts/generate_codebase_map.py", "--check"],
        ]

    for command in commands:
        if run(command):
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("bootstrap", "check", "verify"))
    return execute(parser.parse_args(argv).command)


if __name__ == "__main__":
    raise SystemExit(main())
