"""Evidence-backed maintenance may complete without changing source or tooling."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from agentready.render.generator import generate_project


def test_no_change_maintenance_finishes_normal_lifecycle(tmp_path: Path) -> None:
    root = tmp_path / "maintenance_case"
    generate_project(root, profile="application")
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    def run(*args: str) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/project.py", *args],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    run("bootstrap")
    registry = [sys.executable, "scripts/work_registry.py"]
    subprocess.run(
        [*registry, "new", "--type", "MAINTENANCE", "Inspect tooling state"],
        cwd=root,
        check=True,
    )
    item = root / "docs/work/W001-inspect-tooling-state.md"
    text = item.read_text(encoding="utf-8")
    text = text.replace("Status: BACKLOG", "Status: READY")
    item.write_text(text, encoding="utf-8")
    run("sync")
    run("check")
    preserved = {
        path.relative_to(root): path.read_bytes()
        for directory in (root / "src", root / "scripts")
        for path in directory.rglob("*.py")
    }
    for name in ("pyproject.toml", "uv.lock"):
        preserved[Path(name)] = (root / name).read_bytes()
    subprocess.run([*registry, "transition", "W001", "IN_PROGRESS"], cwd=root, check=True)
    text = item.read_text(encoding="utf-8")
    for old, new in (
        ("### Result\nNOT_STARTED", "### Result\nCOMPLETE"),
        ("<None yet>", "NO CODE CHANGE; baseline inspection found no justified modification."),
        ("<None>", "None; existing locked tooling and dependencies retained."),
        ("README: NOT_EVALUATED", "README: NOT_REQUIRED"),
        ("ARCHITECTURE: NOT_EVALUATED", "ARCHITECTURE: NOT_REQUIRED"),
        ("ADR: NOT_EVALUATED", "ADR: NOT_REQUIRED"),
        ("Summary: <Concise summary>", "Summary: Inspected tooling; no modification justified."),
    ):
        text = text.replace(old, new)
    text = text.replace(
        "### Verification performed\nNone; existing locked tooling and dependencies retained.",
        "### Verification performed\nproject.py check passed before completion; lockfile retained.",
    )
    item.write_text(text, encoding="utf-8")
    subprocess.run([*registry, "transition", "W001", "DONE"], cwd=root, check=True)
    run("sync")
    run("check")
    assert "W001 [MAINTENANCE]" in (root / "docs/changelog/index.md").read_text(encoding="utf-8")
    assert all((root / path).read_bytes() == content for path, content in preserved.items())
