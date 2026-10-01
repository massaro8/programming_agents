"""Generated work orientation is deterministic and read-only."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from agentready.render.generator import generate_project


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/project.py", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_context_status_and_next_are_read_only(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    generate_project(root, profile="application")
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert "NO_READY_WORK" in _run(root, "next").stdout
    assert "profile: application" in _run(root, "status").stdout
    assert "codebase_map: OK" in _run(root, "status").stdout
    assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_context_resolves_work_type_and_keeps_blocked_non_actionable(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    generate_project(root)
    scripts = str(root / "scripts")
    sys.path.insert(0, scripts)
    try:
        registry = runpy.run_path(str(root / "scripts/work_registry.py"))
        work_id = registry["new_work"](root, "BUGFIX", "Fix deterministic issue")
        work_path = next((root / "docs/work").glob(f"{work_id}-*.md"))
        work_path.write_text(
            work_path.read_text(encoding="utf-8").replace("Status: BACKLOG", "Status: READY", 1),
            encoding="utf-8",
        )
        context = runpy.run_path(str(root / "scripts/context.py"))
        result = context["resolve"](root)
        assert result["work_id"] == work_id
        assert result["skill"] == "bug-investigation"
        assert result["actionable"] is True
        output = _run(root, "context", "--next", "--format", "json")
        assert output.returncode == 0
        assert json.loads(output.stdout)["work_id"] == work_id
        work_path.write_text(
            work_path.read_text(encoding="utf-8").replace("Status: READY", "Status: BLOCKED", 1),
            encoding="utf-8",
        )
        assert context["resolve"](root) == {"status": "NO_READY_WORK"}
        blocked = context["resolve"](root, work_id)
        assert blocked["actionable"] is False
        assert json.loads(json.dumps(blocked))["status"] == "BLOCKED"
    finally:
        sys.path.remove(scripts)


def test_generated_check_commands_are_locked(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    generate_project(root)
    project = runpy.run_path(str(root / "scripts/project.py"))
    commands = project["check_commands"]("uv")
    assert commands
    assert all(command[:3] == ["uv", "run", "--locked"] for _, command in commands)


def test_context_routes_ready_feature_docs_and_security(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    generate_project(root)
    scripts = str(root / "scripts")
    sys.path.insert(0, scripts)
    try:
        registry = runpy.run_path(str(root / "scripts/work_registry.py"))
        context = runpy.run_path(str(root / "scripts/context.py"))
        for kind, expected_skill in (
            ("FEATURE", "feature-builder"),
            ("DOCS", "documentation"),
            ("SECURITY", "security-review"),
        ):
            work_id = registry["new_work"](root, kind, f"{kind} qualification")
            path = next((root / "docs/work").glob(f"{work_id}-*.md"))
            path.write_text(
                path.read_text(encoding="utf-8").replace("Status: BACKLOG", "Status: READY", 1),
                encoding="utf-8",
            )
            assert context["resolve"](root, work_id)["skill"] == expected_skill
        with pytest.raises(ValueError, match="unknown work ID"):
            context["resolve"](root, "W999")
    finally:
        sys.path.remove(scripts)


def test_command_check_detects_documented_cli_drift(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    generate_project(root)
    script = root / "scripts/command_check.py"
    valid = subprocess.run(
        [sys.executable, str(script)], cwd=root, capture_output=True, text=True, check=False
    )
    assert valid.returncode == 0, valid.stderr
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\n`python scripts/project.py impossible`\n",
        encoding="utf-8",
    )
    invalid = subprocess.run(
        [sys.executable, str(script)], cwd=root, capture_output=True, text=True, check=False
    )
    assert invalid.returncode == 1
    assert "unknown ['impossible']" in invalid.stderr


def test_project_module_new_delegates_to_module_knowledge(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    generate_project(root, profile="application")
    result = _run(root, "module", "new", "records", "--responsibility", "Hold local records.")
    assert result.returncode == 0, result.stderr
    assert (root / "docs/modules/records.md").is_file()
    assert (root / "src/generated/modules/records/__init__.py").is_file()
    assert "`records`: module package — Hold local records." in (
        root / "docs/generated/CODEBASE_MAP.md"
    ).read_text(encoding="utf-8")
