from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentready.render.generator import generate_project


def run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/project.py"), *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_capability_help_forwards_to_real_parsers(tmp_path: Path) -> None:
    root = tmp_path / "sample"
    generate_project(root)
    help_text = run(root, "--help")
    assert help_text.returncode == 0
    for text in ("skill eval", "opt-in", "continuity", "checkpoint", "transition", "routing"):
        assert text in help_text.stdout
    for command, expected in (
        ("work", "next-ready"),
        ("skill", "eval"),
        ("hooks", "enable"),
        ("checkpoint", "--state"),
        ("resume", "work_id"),
    ):
        result = run(root, command, "--help")
        assert result.returncode == 0, result.stderr
        assert expected in result.stdout


def test_ready_authoring_and_accepted_feature_continuation(tmp_path: Path) -> None:
    root = tmp_path / "sample"
    generate_project(root)
    assert run(root, "work", "new", "--type", "FEATURE", "Accepted feature").returncode == 0
    record = root / "docs/work/W001-accepted-feature.md"
    assert run(root, "work", "transition", "W001", "READY").returncode != 0
    record.write_text(record.read_text().replace("Status: BACKLOG", "Status: READY"))
    assert run(root, "work", "sync").returncode == 0
    assert run(root, "work", "check").returncode == 0
    assert run(root, "work", "transition", "W001", "IN_PROGRESS").returncode == 0
    assert run(root, "work", "list", "--status", "IN_PROGRESS").stdout.startswith("W001")
    skill = (root / ".agents/skills/feature-builder/SKILL.md").read_text()
    assert "READY or IN_PROGRESS" in skill
    assert "without resetting status or seeking duplicate approval" in skill
    workflow = (root / "docs/agent/workflows/feature.md").read_text()
    assert "Status: BACKLOG" in workflow
    assert "work sync" in workflow
    assert "already accepted IN_PROGRESS" in workflow
