from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentready.render.generator import generate_project


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_generated_greeting_boundaries_match_profile(tmp_path: Path, profile: str) -> None:
    project = tmp_path / profile
    generate_project(project, profile=profile)

    greeting_path = project / "docs/modules/greeting.md"
    if profile == "minimal":
        assert not greeting_path.exists()
        return
    greeting = greeting_path.read_text()
    if profile == "service":
        assert "Console output through the console adapter." in greeting
        assert "No adapter boundary" not in greeting
    else:
        assert "No adapter boundary in this profile." in greeting
        assert "console adapter" not in greeting
    assert len(greeting.splitlines()) == 5
    assert f"{profile} profile" not in greeting

    codebase_map = (project / "docs/generated/CODEBASE_MAP.md").read_text()
    knowledge_check = subprocess.run(
        [sys.executable, "scripts/module_knowledge.py", "check"],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert knowledge_check.returncode == 0, knowledge_check.stderr
    map_check = subprocess.run(
        [sys.executable, "scripts/generate_codebase_map.py", "--check"],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert map_check.returncode == 0, map_check.stderr
    assert f"Profile: `{profile}`" in codebase_map
    assert ("Provide the greeting use case to project entrypoints." in codebase_map) == (
        profile != "minimal"
    )


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_generated_maintenance_and_resource_guidance(tmp_path: Path, profile: str) -> None:
    project = tmp_path / profile
    generate_project(project, profile=profile)

    architecture = (project / "docs/agent/standards/architecture.md").read_text()
    normalized_architecture = " ".join(architecture.split())
    assert "who creates or opens each resource" in normalized_architecture
    assert "who commits or rolls back" in normalized_architecture
    assert "who closes it" in normalized_architecture
    assert (
        "Reuse caller-owned resources; close only resources your code owns."
        in normalized_architecture
    )
    assert "does not automatically close every object it yields" in normalized_architecture
    assert "on success and failure" in normalized_architecture
    assert "whether reuse is supported after scope exit or failure" in normalized_architecture
    assert "commit, rollback, and release behavior" in normalized_architecture
    assert "leaving its caller-owned" in normalized_architecture
    assert "with connection.transaction():" in normalized_architecture

    workflow = (project / "docs/agent/workflows/maintenance.md").read_text()
    assert "Inspection may justify no code change" in workflow
    assert "dependency/tool state" in workflow
    skill = (project / ".agents/skills/maintenance/SKILL.md").read_text()
    assert "If no change is warranted" in skill
    assert "implementation outcome" in skill
