"""Opt-in local preparation for newly generated projects."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from agentready.doctor.inspector import format_report, inspect


class BootstrapError(RuntimeError):
    """A named project bootstrap stage failed."""


def _run(stage: str, command: list[str], root: Path) -> None:
    try:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise BootstrapError(f"bootstrap stage '{stage}' failed: {exc}") from exc
    if result.returncode:
        output = (result.stdout + result.stderr).strip()
        detail = f": {output[-2000:]}" if output else ""
        raise BootstrapError(f"bootstrap stage '{stage}' failed (exit {result.returncode}){detail}")


def bootstrap_project(target: Path) -> None:
    """Prepare and validate a generated repository without rolling it back."""

    root = target if target.is_absolute() else Path.cwd() / target
    uv = shutil.which("uv")
    if uv is None:
        raise BootstrapError("bootstrap stage 'uv availability' failed: install uv and retry")
    _run("project bootstrap", [sys.executable, "scripts/project.py", "bootstrap"], root)
    report = inspect(root)
    if not report.healthy:
        raise BootstrapError(f"bootstrap stage 'doctor' failed:\n{format_report(report)}")
